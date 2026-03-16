"""Project creation wizard service.

Creates project + book + chapters from a template with optional wizard answers.
Supports guided, flexible, and freeform guidance modes.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, FictionWorkspace, NonfictionWorkspace, Project, ProjectMember, ProjectTemplate, WritingFramework
from authora.services.framework_recommendation import get_framework_for_template

GUIDANCE_MODES = ("guided", "flexible", "freeform")
KNOWLEDGE_MODES = ("fiction", "nonfiction", "memoir", "workbook", "hybrid")


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
    guidance_mode: str = "guided",
    knowledge_mode: str | None = None,
) -> tuple[Project, Book]:
    """Create project and book from template (or blank)."""
    from authora.services.billing_service import check_book_limit, check_project_limit

    if guidance_mode not in GUIDANCE_MODES:
        guidance_mode = "guided"
    if not knowledge_mode or knowledge_mode not in KNOWLEDGE_MODES:
        knowledge_mode = "fiction" if book_type == "fiction" else "nonfiction"

    allowed, current, limit = await check_project_limit(db, user_id)
    if not allowed:
        raise ValueError(f"Project limit reached ({current}/{limit})")

    allowed, current, limit = await check_book_limit(db, user_id)
    if not allowed:
        raise ValueError(f"Book limit reached ({current}/{limit})")

    # Freeform: no template, no framework, minimal structure
    use_template = template_id and guidance_mode != "freeform"
    use_framework = guidance_mode == "guided" or (guidance_mode == "flexible" and framework_id)

    template: ProjectTemplate | None = None
    if use_template and template_id:
        result = await db.execute(select(ProjectTemplate).where(ProjectTemplate.id == template_id))
        template = result.scalar_one_or_none()
        if not template or template.is_disabled:
            raise ValueError("Template not found")

    # Resolve book type and genre from template (or user input)
    bt = template.book_type if template and template.book_type else book_type
    gn = genre or (template.genre if template else None)

    book_title_str = book_title or project_name

    # Resolve framework (guided: from template; flexible: optional; freeform: never)
    framework: WritingFramework | None = None
    if use_framework:
        if framework_id:
            framework = await db.get(WritingFramework, framework_id)
            if framework and framework.is_disabled:
                framework = None
        if not framework and template:
            framework = await get_framework_for_template(db, template, structure_framework)

    # Create project
    project = Project(
        user_id=user_id,
        name=project_name,
        template_id=template_id if use_template else None,
        guidance_mode=guidance_mode,
        knowledge_mode=knowledge_mode,
    )
    db.add(project)
    await db.flush()

    # Add owner as project member for collaboration consistency
    owner_member = ProjectMember(
        user_id=user_id,
        project_id=project.id,
        role="owner",
        invited_by=None,
    )
    db.add(owner_member)
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
    if template and template.default_planning_prompts and guidance_mode != "freeform":
        for k, v in template.default_planning_prompts.items():
            if k not in planner_data:
                planner_data[k] = ""

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

    # Create chapters: guided/flexible use skeletons; freeform gets one blank chapter
    chapter_skeletons: list[dict[str, Any]] = []
    if guidance_mode == "freeform":
        chapter_skeletons = [{"title": "Chapter 1", "summary": ""}]
    elif template and template.chapter_skeletons:
        chapter_skeletons = template.chapter_skeletons
        if guidance_mode == "flexible" and len(chapter_skeletons) > 10:
            chapter_skeletons = chapter_skeletons[:5]  # Lighter structure
    if not chapter_skeletons and framework and framework.chapter_skeletons and guidance_mode == "guided":
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
