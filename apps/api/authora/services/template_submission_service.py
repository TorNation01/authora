"""Template submission service: create, approve, reject, performance."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, Project, ProjectTemplate, TemplateSubmission, TemplatePurchase, User

SUBMISSION_STATUS_PENDING = "pending"
SUBMISSION_STATUS_APPROVED = "approved"
SUBMISSION_STATUS_REJECTED = "rejected"
SUBMISSION_STATUS_CHANGES_REQUESTED = "changes_requested"


def _slugify(s: str) -> str:
    """Simple slug: lowercase, replace spaces with hyphens, alphanumeric + hyphen."""
    return "".join(c if c.isalnum() or c == "-" else "-" for c in s.lower().replace(" ", "-")).strip("-")


async def create_submission(
    db: AsyncSession,
    creator_id: uuid.UUID,
    *,
    slug: str | None = None,
    name: str,
    description: str | None = None,
    category: str | None = None,
    price_cents: int | None = None,
    payload: dict | None = None,
) -> TemplateSubmission:
    """Create template submission. Slug derived from name if not provided."""
    slug_final = (slug or _slugify(name))[:100]
    if not slug_final:
        raise ValueError("Slug cannot be empty")

    existing = (
        await db.execute(
            select(ProjectTemplate).where(ProjectTemplate.slug == slug_final)
        )
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Slug '{slug_final}' already used by an existing template")

    existing_sub = (
        await db.execute(
            select(TemplateSubmission).where(
                TemplateSubmission.creator_id == creator_id,
                TemplateSubmission.slug == slug_final,
                TemplateSubmission.status != SUBMISSION_STATUS_REJECTED,
            )
        )
    ).scalar_one_or_none()
    if existing_sub:
        raise ValueError(f"You already have a submission with slug '{slug_final}'")

    from authora.services.template_validation_service import validate_template_payload

    validation = validate_template_payload(
        payload, name=name, description=description
    )
    if not validation["valid"]:
        raise ValueError(
            validation["errors"][0] if validation["errors"] else "Template validation failed"
        )

    sub = TemplateSubmission(
        creator_id=creator_id,
        slug=slug_final,
        name=name,
        description=description,
        category=category,
        price_cents=price_cents,
        payload=payload or {},
        status=SUBMISSION_STATUS_PENDING,
    )
    db.add(sub)
    await db.flush()
    return sub


async def update_submission(
    db: AsyncSession,
    submission_id: uuid.UUID,
    creator_id: uuid.UUID,
    *,
    name: str | None = None,
    description: str | None = None,
    category: str | None = None,
    price_cents: int | None = None,
    payload: dict | None = None,
) -> TemplateSubmission | None:
    """Update submission. Only pending submissions can be edited."""
    r = await db.execute(
        select(TemplateSubmission).where(
            TemplateSubmission.id == submission_id,
            TemplateSubmission.creator_id == creator_id,
        )
    )
    sub = r.scalar_one_or_none()
    if not sub:
        return None
    if sub.status not in (SUBMISSION_STATUS_PENDING, SUBMISSION_STATUS_CHANGES_REQUESTED):
        raise ValueError("Can only edit pending or changes_requested submissions")

    if name is not None:
        sub.name = name
    if description is not None:
        sub.description = description
    if category is not None:
        sub.category = category
    if price_cents is not None:
        sub.price_cents = price_cents
    if payload is not None:
        sub.payload = payload

    from authora.services.template_validation_service import validate_template_payload

    validation = validate_template_payload(
        sub.payload or {},
        name=sub.name,
        description=sub.description,
    )
    if not validation["valid"]:
        raise ValueError(
            validation["errors"][0] if validation["errors"] else "Template validation failed"
        )

    if sub.status == SUBMISSION_STATUS_CHANGES_REQUESTED:
        sub.status = SUBMISSION_STATUS_PENDING
        sub.change_request_reason = None
    await db.flush()
    return sub


async def approve_submission(
    db: AsyncSession,
    submission_id: uuid.UUID,
) -> ProjectTemplate:
    """Admin: approve submission, create ProjectTemplate from payload, link to creator."""
    sub = await db.get(TemplateSubmission, submission_id)
    if not sub:
        raise ValueError("Submission not found")
    if sub.status not in (SUBMISSION_STATUS_PENDING, SUBMISSION_STATUS_CHANGES_REQUESTED):
        raise ValueError(f"Submission status is {sub.status}")

    existing = (
        await db.execute(select(ProjectTemplate).where(ProjectTemplate.slug == sub.slug))
    ).scalar_one_or_none()
    if existing:
        raise ValueError(f"Template with slug '{sub.slug}' already exists")

    payload = sub.payload or {}
    t = ProjectTemplate(
        slug=sub.slug,
        category=sub.category or "creator",
        name=sub.name,
        description=sub.description,
        creator_id=sub.creator_id,
        price_cents=sub.price_cents,
        is_paid=bool(sub.price_cents and sub.price_cents > 0),
        access_level="creator_paid" if (sub.price_cents and sub.price_cents > 0) else "free",
        book_type=payload.get("book_type"),
        genre=payload.get("genre"),
        who_it_is_for=payload.get("who_it_is_for"),
        expected_outcome=payload.get("expected_outcome"),
        suggested_workflow=payload.get("suggested_workflow"),
        structure_framework=payload.get("structure_framework"),
        default_structure=payload.get("default_structure"),
        default_milestones=payload.get("default_milestones"),
        default_planning_prompts=payload.get("default_planning_prompts"),
        default_accountability=payload.get("default_accountability"),
        ai_prompts=payload.get("ai_prompts"),
        export_recommendations=payload.get("export_recommendations"),
        setup_questions=payload.get("setup_questions"),
        chapter_skeletons=payload.get("chapter_skeletons"),
        sort_order=payload.get("sort_order", 0),
        is_featured=False,
        is_disabled=False,
    )
    db.add(t)
    await db.flush()

    sub.status = SUBMISSION_STATUS_APPROVED
    sub.approved_template_id = t.id
    sub.reviewed_at = datetime.now(timezone.utc)
    sub.rejected_reason = None
    await db.flush()
    return t


async def reject_submission(
    db: AsyncSession,
    submission_id: uuid.UUID,
    *,
    rejection_reason: str | None = None,
) -> TemplateSubmission:
    """Admin: reject submission."""
    sub = await db.get(TemplateSubmission, submission_id)
    if not sub:
        raise ValueError("Submission not found")
    if sub.status not in (SUBMISSION_STATUS_PENDING, SUBMISSION_STATUS_CHANGES_REQUESTED):
        raise ValueError(f"Submission status is {sub.status}")
    sub.status = SUBMISSION_STATUS_REJECTED
    sub.reviewed_at = datetime.now(timezone.utc)
    sub.rejected_reason = rejection_reason
    sub.change_request_reason = None
    await db.flush()
    return sub


async def request_changes(
    db: AsyncSession,
    submission_id: uuid.UUID,
    *,
    change_request_reason: str,
) -> TemplateSubmission:
    """Admin: request changes. Creator can edit and resubmit."""
    sub = await db.get(TemplateSubmission, submission_id)
    if not sub:
        raise ValueError("Submission not found")
    if sub.status not in (SUBMISSION_STATUS_PENDING, SUBMISSION_STATUS_CHANGES_REQUESTED):
        raise ValueError(f"Submission status is {sub.status}")
    if not change_request_reason or not change_request_reason.strip():
        raise ValueError("Change request reason is required")
    sub.status = SUBMISSION_STATUS_CHANGES_REQUESTED
    sub.reviewed_at = datetime.now(timezone.utc)
    sub.change_request_reason = change_request_reason.strip()
    sub.rejected_reason = None
    await db.flush()
    return sub


async def get_creator_performance(
    db: AsyncSession,
    creator_id: uuid.UUID,
) -> dict[str, Any]:
    """Get usage and sales stats for creator's approved templates (views, projects, books, sales, revenue)."""
    import asyncio

    from authora.services.creator_growth_service import get_template_views

    r = await db.execute(
        select(ProjectTemplate.id, ProjectTemplate.slug, ProjectTemplate.name)
        .where(
            ProjectTemplate.creator_id == creator_id,
            ProjectTemplate.is_disabled.is_(False),
        )
    )
    templates = list(r.all())
    if not templates:
        return {"templates": [], "total_projects": 0, "total_books": 0}

    template_ids = [t.id for t in templates]
    r_sales = await db.execute(
        select(
            TemplatePurchase.template_id,
            func.count(TemplatePurchase.id).label("sales"),
            func.coalesce(func.sum(TemplatePurchase.amount_cents), 0).label("revenue_cents"),
        )
        .where(TemplatePurchase.template_id.in_(template_ids))
        .group_by(TemplatePurchase.template_id)
    )
    sales_data = list(r_sales.all())
    sales_counts = {str(tid): cnt for tid, cnt, _ in sales_data}
    revenue_by_template = {str(tid): rev for tid, _, rev in sales_data}

    r_proj = await db.execute(
        select(Project.template_id, func.count(Project.id))
        .where(Project.template_id.in_(template_ids))
        .group_by(Project.template_id)
    )
    proj_counts = {str(tid): cnt for tid, cnt in r_proj.all()}

    r_book = await db.execute(
        select(Book.template_id, func.count(Book.id))
        .where(Book.template_id.in_(template_ids))
        .group_by(Book.template_id)
    )
    book_counts = {str(tid): cnt for tid, cnt in r_book.all()}

    total_projects = sum(proj_counts.values())
    total_books = sum(book_counts.values())
    total_sales = sum(sales_counts.values())
    total_revenue_cents = sum(revenue_by_template.values())

    views_list = await asyncio.gather(*[get_template_views(db, t.id) for t in templates])
    views_by_id = {str(t.id): v for t, v in zip(templates, views_list)}
    total_views = sum(views_by_id.values())

    return {
        "templates": [
            {
                "id": str(t.id),
                "slug": t.slug,
                "name": t.name,
                "views": views_by_id.get(str(t.id), 0),
                "projects_count": proj_counts.get(str(t.id), 0),
                "books_count": book_counts.get(str(t.id), 0),
                "sales_count": sales_counts.get(str(t.id), 0),
                "revenue_cents": revenue_by_template.get(str(t.id), 0),
            }
            for t in templates
        ],
        "total_projects": total_projects,
        "total_books": total_books,
        "total_sales": total_sales,
        "total_revenue_cents": total_revenue_cents,
        "total_views": total_views,
    }


async def list_submissions_admin(
    db: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[tuple[TemplateSubmission, str | None]]:
    """Admin: list submissions with creator email."""
    q = (
        select(TemplateSubmission, User.email)
        .join(User, TemplateSubmission.creator_id == User.id)
        .order_by(TemplateSubmission.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status:
        q = q.where(TemplateSubmission.status == status)
    r = await db.execute(q)
    return list(r.all())
