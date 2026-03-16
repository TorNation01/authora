"""Writing frameworks API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import WritingFramework
from authora.services.framework_recommendation import get_framework_by_slug, recommend_frameworks

router = APIRouter(prefix="/frameworks", tags=["frameworks"])


class FrameworkResponse(BaseModel):
    """Writing framework in API response."""

    id: uuid.UUID
    slug: str
    book_type: str
    name: str
    description: str | None
    ideal_use_cases: str | None
    ideal_genres: list[str] | None
    planning_stages: list[dict] | None
    beat_stages: list[dict] | None
    chapter_structure: dict | None
    manuscript_scaffolding: dict | None
    chapter_skeletons: list[dict] | None
    milestone_logic: dict | None
    accountability_mapping: dict | None
    revision_checklist: list[str] | None
    ai_prompt_presets: dict | None
    scene_prompts: dict | None
    sort_order: int
    is_featured: bool

    model_config = {"from_attributes": True}


@router.get("", response_model=list[FrameworkResponse])
async def list_frameworks(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_type: str | None = Query(None, description="fiction | nonfiction"),
    featured_only: bool = Query(False, description="Only featured frameworks"),
    launch_priority: bool = Query(False, description="Only launch-priority flagship frameworks"),
):
    """List available writing frameworks."""
    q = (
        select(WritingFramework)
        .where(WritingFramework.is_disabled.is_(False))
        .order_by(WritingFramework.sort_order.asc(), WritingFramework.name.asc())
    )
    if book_type:
        q = q.where(WritingFramework.book_type == book_type)
    if featured_only:
        q = q.where(WritingFramework.is_featured.is_(True))
    result = await db.execute(q)
    frameworks = list(result.scalars().all())
    if launch_priority:
        frameworks = [f for f in frameworks if (f.recommendation_rules or {}).get("launch_priority")]
    return [FrameworkResponse.model_validate(f) for f in frameworks]


@router.get("/recommend", response_model=list[FrameworkResponse])
async def recommend_frameworks_endpoint(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_type: str = Query(..., description="fiction | nonfiction"),
    genre: str | None = Query(None),
    template_id: uuid.UUID | None = Query(None),
    template_slug: str | None = Query(None),
    is_series: bool = Query(False),
    limit: int = Query(5, ge=1, le=10),
):
    """Get recommended frameworks for a book based on type, genre, and template."""
    frameworks = await recommend_frameworks(
        db,
        book_type=book_type,
        genre=genre,
        template_id=template_id,
        template_slug=template_slug,
        is_series=is_series,
        limit=limit,
    )
    return [FrameworkResponse.model_validate(f) for f in frameworks]


@router.get("/{framework_id_or_slug}", response_model=FrameworkResponse)
async def get_framework(
    framework_id_or_slug: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get framework by ID or slug."""
    try:
        fid = uuid.UUID(framework_id_or_slug)
        result = await db.execute(
            select(WritingFramework).where(
                WritingFramework.id == fid,
                WritingFramework.is_disabled.is_(False),
            )
        )
    except ValueError:
        result = await db.execute(
            select(WritingFramework).where(
                WritingFramework.slug == framework_id_or_slug,
                WritingFramework.is_disabled.is_(False),
            )
        )
    fw = result.scalar_one_or_none()
    if not fw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Framework not found")
    return FrameworkResponse.model_validate(fw)
