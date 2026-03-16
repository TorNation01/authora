"""Milestone engine: framework-aware and freeform milestone generation."""

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Chapter, Milestone, Project, WritingPlan
from authora.models.project_template import ProjectTemplate

# Fiction milestone types (framework-aware)
FICTION_MILESTONE_TYPES = [
    "premise_complete",
    "outline_complete",
    "act_one_complete",
    "act_two_complete",
    "midpoint_reached",
    "act_three_complete",
    "first_draft_complete",
    "revision_pass_one",
    "beta_feedback",
    "export_ready",
]

# Nonfiction milestone types
NONFICTION_MILESTONE_TYPES = [
    "chapter_promise_complete",
    "framework_section_complete",
    "workbook_module_complete",
    "research_phase_complete",
    "intro_draft",
    "core_chapters_draft",
    "conclusion_draft",
    "first_draft_complete",
    "expert_review",
    "export_ready",
]

# Freeform: generic types
FREEFORM_MILESTONE_TYPES = [
    "custom",
    "chapter_count",
    "word_count",
    "deadline",
]


def get_default_milestones_for_template(
    template: ProjectTemplate | None,
    book_type: str = "fiction",
) -> list[dict[str, Any]]:
    """Get default milestones from template or fallback to book type."""
    defaults = template.default_milestones if template and template.default_milestones else None
    if defaults:
        return [
            {
                "id": m.get("id", f"m{i}"),
                "label": m.get("label", m.get("title", f"Milestone {i+1}")),
                "type": m.get("type", "draft"),
                "milestone_type": m.get("milestone_type"),
                "framework_stage": m.get("framework_stage"),
                "sort_order": i,
            }
            for i, m in enumerate(defaults)
        ]

    if book_type == "nonfiction":
        return [
            {"id": "outline", "label": "Chapter outline complete", "type": "planning", "sort_order": 0},
            {"id": "intro", "label": "Introduction draft", "type": "draft", "sort_order": 1},
            {"id": "core", "label": "Core chapters draft", "type": "draft", "sort_order": 2},
            {"id": "conclusion", "label": "Conclusion draft", "type": "draft", "sort_order": 3},
            {"id": "revision", "label": "First revision pass", "type": "revision", "sort_order": 4},
            {"id": "final", "label": "Final polish", "type": "revision", "sort_order": 5},
        ]
    return [
        {"id": "outline", "label": "Outline complete", "type": "planning", "sort_order": 0},
        {"id": "act1", "label": "Act I draft complete", "type": "draft", "sort_order": 1},
        {"id": "act2", "label": "Act II draft complete", "type": "draft", "sort_order": 2},
        {"id": "act3", "label": "Act III draft complete", "type": "draft", "sort_order": 3},
        {"id": "revision", "label": "First revision pass", "type": "revision", "sort_order": 4},
        {"id": "final", "label": "Final polish", "type": "revision", "sort_order": 5},
    ]


async def generate_milestones_for_book(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    writing_plan_id: UUID | None = None,
    total_target_words: int = 50000,
    target_finish_date: date | None = None,
) -> list[Milestone]:
    """Generate milestones for a book from template/framework or freeform defaults."""
    result = await db.execute(
        select(Book, Project, ProjectTemplate)
        .join(Project, Book.project_id == Project.id)
        .outerjoin(ProjectTemplate, Book.template_id == ProjectTemplate.id)
        .where(Book.id == book_id, Project.user_id == user_id)
    )
    row = result.one_or_none()
    if not row:
        return []

    book, project, template = row
    book_type = getattr(book, "type", None) or "fiction"
    defs = get_default_milestones_for_template(template, book_type)

    chapters_result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None)).order_by(Chapter.sort_order)
    )
    chapters = chapters_result.scalars().all()
    total_chapters = len(chapters)
    words_per_milestone = total_target_words // max(1, len(defs)) if total_target_words else 5000

    milestones: list[Milestone] = []
    for i, d in enumerate(defs):
        target_words = (i + 1) * words_per_milestone
        target_date = None
        if target_finish_date and total_target_words:
            pct = (i + 1) / len(defs)
            days_out = int((target_finish_date - date.today()).days * pct)
            target_date = date.today() + timedelta(days=max(0, days_out))

        m = Milestone(
            user_id=user_id,
            book_id=book_id,
            writing_plan_id=writing_plan_id,
            title=d["label"],
            target_words=target_words,
            target_date=target_date,
            milestone_type=d.get("milestone_type") or d.get("type", "draft"),
            framework_stage=d.get("framework_stage"),
            sort_order=d.get("sort_order", i),
        )
        db.add(m)
        milestones.append(m)

    await db.flush()
    return milestones


async def create_custom_milestone(
    db: AsyncSession,
    user_id: UUID,
    title: str,
    target_words: int = 0,
    target_date: date | None = None,
    book_id: UUID | None = None,
    writing_plan_id: UUID | None = None,
    milestone_type: str = "custom",
    sort_order: int = 0,
) -> Milestone:
    """Create a custom milestone (freeform mode)."""
    m = Milestone(
        user_id=user_id,
        book_id=book_id,
        writing_plan_id=writing_plan_id,
        title=title,
        target_words=target_words or 1000,
        target_date=target_date,
        milestone_type=milestone_type,
        sort_order=sort_order,
    )
    db.add(m)
    await db.flush()
    await db.refresh(m)
    return m


async def complete_milestone(
    db: AsyncSession,
    milestone_id: UUID,
    user_id: UUID,
) -> Milestone | None:
    """Mark a milestone as complete."""
    from datetime import datetime, timezone

    result = await db.execute(
        select(Milestone).where(
            Milestone.id == milestone_id,
            Milestone.user_id == user_id,
        )
    )
    m = result.scalar_one_or_none()
    if m:
        m.completed_at = datetime.now(timezone.utc)
        await db.flush()
    return m


async def list_milestones_for_book(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    include_completed: bool = True,
) -> list[Milestone]:
    """List milestones for a book, optionally excluding completed."""
    q = (
        select(Milestone)
        .where(Milestone.book_id == book_id, Milestone.user_id == user_id)
        .order_by(Milestone.sort_order, Milestone.created_at)
    )
    if not include_completed:
        q = q.where(Milestone.completed_at.is_(None))
    result = await db.execute(q)
    return list(result.scalars().all())
