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

router = APIRouter(prefix="/templates", tags=["templates"])


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
    """List template categories with top-level templates and their children."""
    # Top-level only
    q = (
        select(ProjectTemplate)
        .where(ProjectTemplate.parent_id.is_(None), ProjectTemplate.is_disabled.is_(False))
        .order_by(ProjectTemplate.sort_order.asc())
    )
    result = await db.execute(q)
    parents = result.scalars().all()

    # Children for each parent
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
            "template": TemplateSummary.model_validate(p),
            "children": [TemplateSummary.model_validate(c) for c in children],
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


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: uuid.UUID,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get template by ID with full details."""
    result = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if template.is_disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return TemplateResponse.model_validate(template)


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


@router.get("/slug/{slug}", response_model=TemplateResponse)
async def get_template_by_slug(
    slug: str,
    current_user: Annotated[dict, Depends(CurrentUser)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get template by slug."""
    result = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.slug == slug)
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if template.is_disabled:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return TemplateResponse.model_validate(template)
