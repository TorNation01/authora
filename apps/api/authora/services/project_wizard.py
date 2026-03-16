"""Project creation wizard service.

Creates project + book + chapters from a template with optional wizard answers.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, FictionWorkspace, NonfictionWorkspace, Project, ProjectTemplate, WritingFramework
from authora.services.framework_recommendation import get_framework_by_slug, get_framework_for_template


async def create_project_from_wizard(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    template_id: uuid.UUID | None = None,
    project_name: str,
    book_title: str | None = None,
    book_type: str = "fiction",
    genre: str | None = None,
    core_idea: str | None = None,
    wizard_answers: dict[str, Any] | None = None,
    structure_framework: str | None = None,
    framework_id: uuid.UUID | None = None,
    target_words: int | None = None,
    target_date: str | None = None,
) -> tuple[Project, Book]:
    """Create project and book from template (or blank)."""
    from authora.services.billing_service import check_book_limit, check_project_limit

    allowed, current, limit = await check_project_limit(db, user_id)
    if not allowed:
        raise ValueError(f"Project limit reached ({current}/{limit})")

    allowed, current, limit = await check_book_limit(db, user_id)
    if not allowed:
        raise ValueError(f"Book limit reached ({current}/{limit})")

    template: ProjectTemplate | None = None
    if template_id:
        result = await db.execute(select(ProjectTemplate).where(ProjectTemplate.id == template_id))
        template = result.scalar_one_or_none()
        if not template or template.is_disabled:
            raise ValueError("Template not found")

    # Resolve book type and genre from template
    bt = template.book_type if template and template.book_type else book_type
    gn = genre or (template.genre if template else None)

    book_title_str = book_title or project_name

    # Create project
    project = Project(
        user_id=user_id,
        name=project_name,
        template_id=template_id,
    )
    db.add(project)
    await db.flush()

    # Build planner_data from wizard answers and template
    planner_data: dict[str, Any] = {}
    if wizard_answers:
        planner_data.update(wizard_answers)
    if core_idea:
        planner_data["core_idea"] = core_idea
    if target_words:
        planner_data["target_words"] = target_words
    if target_date:
        planner_data["target_date"] = target_date
    if structure_framework:
        planner_data["structure_framework"] = structure_framework
    if framework:
        planner_data["framework_slug"] = framework.slug
        planner_data["framework_name"] = framework.name
    if template and template.default_planning_prompts:
        for k, v in template.default_planning_prompts.items():
            if k not in planner_data:
                planner_data[k] = ""

    # Resolve framework
    framework: WritingFramework | None = None
    if framework_id:
        framework = await db.get(WritingFramework, framework_id)
        if framework and framework.is_disabled:
            framework = None
    if not framework and template:
        framework = await get_framework_for_template(db, template, structure_framework)

    # Create book
    book = Book(
        project_id=project.id,
        title=book_title_str,
        genre=gn,
        type=bt,
        template_id=template_id,
        framework_id=framework.id if framework else None,
        planner_data=planner_data if planner_data else None,
    )
    db.add(book)
    await db.flush()

    # Create chapters: template skeletons first, then framework skeletons if empty
    chapter_skeletons: list[dict[str, Any]] = []
    if template and template.chapter_skeletons:
        chapter_skeletons = template.chapter_skeletons
    if not chapter_skeletons and framework and framework.chapter_skeletons:
        chapter_skeletons = framework.chapter_skeletons

    if chapter_skeletons:
        for i, skel in enumerate(chapter_skeletons):
            title = skel.get("title", f"Chapter {i + 1}")
            ch = Chapter(
                book_id=book.id,
                title=title,
                sort_order=i,
                content={"type": "doc", "content": [{"type": "paragraph", "content": []}]},
                word_count=0,
            )
            db.add(ch)

    # Create workspace (fiction or nonfiction)
    if bt == "fiction":
        fw = FictionWorkspace(
            book_id=book.id,
            premise=core_idea or planner_data.get("premise"),
            genre=gn,
            tone=planner_data.get("tone"),
            themes=planner_data.get("themes"),
        )
        db.add(fw)
    elif bt == "nonfiction":
        nw = NonfictionWorkspace(
            book_id=book.id,
            core_message=core_idea or planner_data.get("core_idea"),
            reader_outcome=planner_data.get("reader_outcome"),
            reader_promise=planner_data.get("reader_promise"),
        )
        db.add(nw)

    await db.flush()
    return project, book
