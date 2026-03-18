"""Project templates API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.data.premium_templates import PREMIUM_LAUNCH_SLUGS
from authora.models import ProjectTemplate
from authora.schemas.template import TemplateResponse, TemplateSummary
from authora.services.billing_service import get_user_plan
from authora.services.template_access_service import (
    _check_template_access,
    get_user_purchased_packs,
    get_user_purchased_template_ids,
    has_template_access,
)

router = APIRouter(prefix="/templates", tags=["templates"])


def _template_to_summary_with_access(
    t: ProjectTemplate,
    user_plan_slug: str,
    purchased_packs: set[str],
    purchased_template_ids: set[uuid.UUID] | None = None,
    *,
    creator_name: str | None = None,
    usage_count: int = 0,
    rating_avg: float | None = None,
    rating_count: int = 0,
) -> TemplateSummary:
    """Build TemplateSummary with can_use and required_action."""
    access_level = getattr(t, "access_level", None) or "free"
    pack_slug = getattr(t, "premium_pack_slug", None)
    can_use, required_action = _check_template_access(
        access_level,
        pack_slug,
        user_plan_slug,
        purchased_packs,
        purchased_template_ids=purchased_template_ids or set(),
        template_id=t.id,
    )
    return TemplateSummary(
        id=t.id,
        slug=t.slug,
        category=t.category,
        parent_id=t.parent_id,
        name=t.name,
        description=t.description,
        book_type=t.book_type,
        genre=t.genre,
        sort_order=t.sort_order,
        is_featured=t.is_featured,
        access_level=access_level,
        premium_pack_slug=pack_slug,
        price_cents=getattr(t, "price_cents", None),
        is_paid=getattr(t, "is_paid", False),
        can_use=can_use,
        required_action=required_action,
        creator_name=creator_name,
        usage_count=usage_count,
        rating_avg=rating_avg,
        rating_count=rating_count,
    )


@router.get("", response_model=list[TemplateSummary])
async def list_templates(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(None, description="Filter by category"),
    parent_id: uuid.UUID | None = Query(None, description="Filter by parent (sub-templates only)"),
    featured: bool | None = Query(None, description="Only featured templates"),
    include_disabled: bool = Query(False, description="Include disabled templates (admin)"),
):
    """List available project templates."""
    q = select(ProjectTemplate)
    if not include_disabled:
        q = q.where(ProjectTemplate.is_disabled.is_(False))
    if category:
        q = q.where(ProjectTemplate.category == category)
    if parent_id is not None:
        q = q.where(ProjectTemplate.parent_id == parent_id)
    elif parent_id is None and category is None:
        # Default: top-level only (parent_id is null)
        q = q.where(ProjectTemplate.parent_id.is_(None))
    if featured is True:
        q = q.where(ProjectTemplate.is_featured.is_(True))
    q = q.order_by(ProjectTemplate.sort_order.asc(), ProjectTemplate.name.asc())
    result = await db.execute(q)
    templates = result.scalars().all()
    return [TemplateSummary.model_validate(t) for t in templates]


@router.get("/featured-launch", response_model=list[TemplateSummary])
async def list_featured_launch_templates(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List first-wave premium launch templates (Romance, Fantasy, Thriller, Sci-fi, Memoir, Self-help, Business, Workbook)."""
    from sqlalchemy import and_

    q = (
        select(ProjectTemplate)
        .where(
            and_(
                ProjectTemplate.slug.in_(PREMIUM_LAUNCH_SLUGS),
                ProjectTemplate.is_disabled.is_(False),
            )
        )
        .order_by(ProjectTemplate.sort_order.asc())
    )
    result = await db.execute(q)
    templates = result.scalars().all()
    return [TemplateSummary.model_validate(t) for t in templates]


@router.get("/categories", response_model=list[dict])
async def list_categories(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List template categories with top-level templates and their children. Includes access info."""
    from authora.services.marketplace_service import get_creator_names, get_template_usage_counts

    plan = await get_user_plan(db, current_user.id)
    plan_slug = getattr(plan, "slug", "free") or "free"
    purchased = await get_user_purchased_packs(db, current_user.id)
    purchased_templates = await get_user_purchased_template_ids(db, current_user.id)

    q = (
        select(ProjectTemplate)
        .where(ProjectTemplate.parent_id.is_(None), ProjectTemplate.is_disabled.is_(False))
        .order_by(ProjectTemplate.sort_order.asc())
    )
    result = await db.execute(q)
    parents = result.scalars().all()

    all_templates = list(parents)
    for p in parents:
        cq = (
            select(ProjectTemplate)
            .where(ProjectTemplate.parent_id == p.id, ProjectTemplate.is_disabled.is_(False))
            .order_by(ProjectTemplate.sort_order.asc())
        )
        cr = await db.execute(cq)
        children = cr.scalars().all()
        all_templates.extend(children)

    usage_counts = await get_template_usage_counts(db)
    creator_ids = {t.creator_id for t in all_templates if t.creator_id}
    creator_names = await get_creator_names(db, creator_ids)

    def _with_trust(t):
        return _template_to_summary_with_access(
            t,
            plan_slug,
            purchased,
            purchased_templates,
            creator_name=creator_names.get(t.creator_id) if t.creator_id else None,
            usage_count=usage_counts.get(t.id, 0),
        )

    out = []
    for p in parents:
        cq = (
            select(ProjectTemplate)
            .where(ProjectTemplate.parent_id == p.id, ProjectTemplate.is_disabled.is_(False))
            .order_by(ProjectTemplate.sort_order.asc())
        )
        cr = await db.execute(cq)
        children = cr.scalars().all()
        out.append({
            "category": p.category,
            "name": p.name,
            "slug": p.slug,
            "template": _with_trust(p),
            "children": [_with_trust(c) for c in children],
        })
    return out


@router.get("/all", response_model=list[TemplateSummary])
async def list_all_templates(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all templates (top-level and sub-templates) for wizard."""
    q = (
        select(ProjectTemplate)
        .where(ProjectTemplate.is_disabled.is_(False))
        .order_by(ProjectTemplate.sort_order.asc(), ProjectTemplate.name.asc())
    )
    result = await db.execute(q)
    templates = result.scalars().all()
    return [TemplateSummary.model_validate(t) for t in templates]


@router.get("/trending")
async def list_trending_templates(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = 7,
    limit: int = 10,
):
    """List trending templates by recent activity (projects + purchases)."""
    from authora.services.creator_growth_service import get_trending_templates

    items = await get_trending_templates(db, days=days, limit=limit)
    return items


@router.get("/top-sellers")
async def list_top_sellers(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 10,
):
    """List top-selling templates by purchase count."""
    from authora.services.creator_growth_service import get_top_sellers

    items = await get_top_sellers(db, limit=limit)
    return items


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get template by ID with full details. Includes can_use, required_action, trust signals."""
    from authora.services.marketplace_service import get_creator_names, get_template_usage_counts

    result = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if template.is_disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    can_use, required_action = await has_template_access(db, current_user.id, template)

    usage_counts = await get_template_usage_counts(db)
    creator_name = None
    if template.creator_id:
        creator_names = await get_creator_names(db, {template.creator_id})
        creator_name = creator_names.get(template.creator_id)

    resp = TemplateResponse.model_validate(template)
    return resp.model_copy(
        update={
            "can_use": can_use,
            "required_action": required_action,
            "creator_name": creator_name,
            "usage_count": usage_counts.get(template.id, 0),
        }
    )


@router.post("/{template_id}/view")
async def record_template_view(
    template_id: uuid.UUID,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Record a template view (preview opened). Used for analytics."""
    from authora.services.creator_growth_service import record_template_view as svc_record_view

    result = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template or template.is_disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")

    await svc_record_view(db, template_id, current_user.id)
    await db.commit()
    return {"ok": True}


@router.get("/{template_id}/analytics")
async def get_template_analytics(
    template_id: uuid.UUID,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get analytics for a template (views, conversions, earnings). Creator-only."""
    from authora.services.creator_growth_service import get_template_analytics as svc_get_analytics
    from authora.services.creator_service import is_approved_creator

    if not await is_approved_creator(db, current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Creator access required")

    result = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template or template.is_disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if template.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your template")

    analytics = await svc_get_analytics(db, template_id)
    return analytics


@router.get("/starters", response_model=list[dict])
async def list_starters(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List starter templates with template IDs resolved from slugs.
    Returns { id, template_id } for each starter. Frontend merges with starter-templates.ts.
    """
    from authora.data.starter_definitions import get_starter_metadata

    slugs = [m["template_slug"] for m in get_starter_metadata() if m.get("template_slug")]
    q = select(ProjectTemplate.slug, ProjectTemplate.id).where(
        ProjectTemplate.slug.in_(slugs),
        ProjectTemplate.is_disabled.is_(False),
    )
    result = await db.execute(q)
    slug_to_id = {row.slug: str(row.id) for row in result.all()}

    return [
        {
            "id": m["id"],
            "template_id": slug_to_id.get(m["template_slug"]) if m.get("template_slug") else None,
        }
        for m in get_starter_metadata()
    ]


@router.get("/purchased", response_model=list[TemplateSummary])
async def list_purchased_templates(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List templates the user has purchased (creator templates). Saved to account, accessible anytime."""
    from authora.models import TemplatePurchase

    r = await db.execute(
        select(ProjectTemplate)
        .join(TemplatePurchase, TemplatePurchase.template_id == ProjectTemplate.id)
        .where(
            TemplatePurchase.user_id == current_user.id,
            ProjectTemplate.is_disabled.is_(False),
        )
        .order_by(ProjectTemplate.name.asc())
    )
    templates = r.scalars().all()
    return [
        TemplateSummary.model_validate(t).model_copy(update={"can_use": True, "required_action": None})
        for t in templates
    ]


@router.get("/packs", response_model=list[dict])
async def list_template_packs(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List available template packs for purchase."""
    from authora.models import TemplatePack

    q = select(TemplatePack).where(TemplatePack.is_active.is_(True)).order_by(TemplatePack.sort_order.asc())
    result = await db.execute(q)
    packs = result.scalars().all()
    purchased = await get_user_purchased_packs(db, current_user.id)

    return [
        {
            "slug": p.slug,
            "name": p.name,
            "description": p.description,
            "price_cents": p.price_cents,
            "template_slugs": p.template_slugs or [],
            "purchased": p.slug in purchased,
        }
        for p in packs
    ]


@router.get("/marketplace", response_model=list[TemplateSummary])
async def list_marketplace_templates(
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(None, description="Filter by category"),
    featured: bool | None = Query(None, description="Only featured templates"),
    search: str | None = Query(None, description="Search by name or description"),
    book_type: str | None = Query(None, description="Filter by book_type"),
    genre: str | None = Query(None, description="Filter by genre"),
    price_min: int | None = Query(None, description="Min price in cents"),
    price_max: int | None = Query(None, description="Max price in cents"),
):
    """Browse templates for marketplace. Supports category, featured, search, and filters."""
    from sqlalchemy import or_

    from authora.services.marketplace_service import get_creator_names, get_template_usage_counts

    plan = await get_user_plan(db, current_user.id)
    plan_slug = getattr(plan, "slug", "free") or "free"
    purchased = await get_user_purchased_packs(db, current_user.id)
    purchased_templates = await get_user_purchased_template_ids(db, current_user.id)

    q = select(ProjectTemplate).where(ProjectTemplate.is_disabled.is_(False))
    if category:
        q = q.where(ProjectTemplate.category == category)
    if featured is True:
        q = q.where(ProjectTemplate.is_featured.is_(True))
    if search:
        pattern = f"%{search}%"
        q = q.where(
            or_(
                ProjectTemplate.name.ilike(pattern),
                ProjectTemplate.description.ilike(pattern),
            )
        )
    if book_type:
        q = q.where(ProjectTemplate.book_type == book_type)
    if genre:
        q = q.where(ProjectTemplate.genre.ilike(f"%{genre}%"))
    if price_min is not None:
        q = q.where(ProjectTemplate.price_cents >= price_min)
    if price_max is not None:
        q = q.where(ProjectTemplate.price_cents <= price_max)
    q = q.order_by(ProjectTemplate.sort_order.asc(), ProjectTemplate.name.asc())
    result = await db.execute(q)
    templates = result.scalars().all()

    usage_counts = await get_template_usage_counts(db)
    creator_ids = {t.creator_id for t in templates if t.creator_id}
    creator_names = await get_creator_names(db, creator_ids)

    return [
        _template_to_summary_with_access(
            t,
            plan_slug,
            purchased,
            purchased_templates,
            creator_name=creator_names.get(t.creator_id) if t.creator_id else None,
            usage_count=usage_counts.get(t.id, 0),
        )
        for t in templates
    ]


@router.get("/slug/{slug}", response_model=TemplateResponse)
async def get_template_by_slug(
    slug: str,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get template by slug with access info."""
    result = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.slug == slug)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if template.is_disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    can_use, required_action = await has_template_access(db, current_user.id, template)
    resp = TemplateResponse.model_validate(template)
    return resp.model_copy(update={"can_use": can_use, "required_action": required_action})
