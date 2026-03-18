"""Growth API: viral share, content generation, referrals, SEO, creator growth."""

from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import AdminUser, CurrentUser
from authora.config import get_settings
from authora.database import get_db
from authora.services.creator_growth_service import (
    get_featured_creators,
)
from authora.services.growth_service import (
    create_share_link,
    generate_share_content,
    get_growth_feature_enabled,
    get_growth_settings,
    get_or_create_referral_code,
    get_seo_page_by_slug,
    get_share_link_by_slug,
    list_seo_pages,
    update_growth_setting,
)

router = APIRouter(prefix="/growth", tags=["growth"])


# --- Share ---
class ShareCreate(BaseModel):
    share_type: str = Field(..., pattern="^(progress|milestone|achievement|book_finished)$")
    payload: dict[str, Any] = Field(default_factory=dict)
    expires_days: int = Field(90, ge=0, le=365)


class ShareResponse(BaseModel):
    id: str
    slug: str
    share_type: str
    share_url: str
    card: dict[str, Any]
    caption: str
    social_links: dict[str, str]


@router.post("/share", response_model=ShareResponse)
async def create_share(
    data: ShareCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Create shareable link and get content for social."""
    feature_map = {
        "progress": "share_progress",
        "milestone": "share_milestones",
        "achievement": "share_achievements",
        "book_finished": "share_milestones",
    }
    feature = feature_map.get(data.share_type, "share_progress")
    if not await get_growth_feature_enabled(db, feature):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sharing disabled")

    payload = {**data.payload, "display_name": current_user.display_name or "A writer"}
    link = await create_share_link(
        db, current_user.id, data.share_type, payload, expires_days=data.expires_days
    )
    await db.commit()

    settings = get_settings()
    app_url = settings.branding_product_name or "AUTHORA"
    base_url = settings.app_base_url.rstrip("/")
    share_url = f"{base_url}/share/{link.slug}"
    content = generate_share_content(data.share_type, payload, product_name=app_url, app_url=share_url)

    return ShareResponse(
        id=str(link.id),
        slug=link.slug,
        share_type=link.share_type,
        share_url=share_url,
        card=content["card"],
        caption=content["caption"],
        social_links=content["social_links"],
    )


@router.get("/share/{slug}")
async def get_share_public(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Public: get share card data (for OG, embed). No auth."""
    link = await get_share_link_by_slug(db, slug)
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share not found")
    if link.expires_at and link.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share expired")
    await db.commit()

    settings = get_settings()
    base_url = settings.app_base_url.rstrip("/")
    content = generate_share_content(
        link.share_type, link.payload,
        product_name=settings.branding_product_name or "AUTHORA",
        app_url=base_url,
    )
    return {
        "share_type": link.share_type,
        "payload": link.payload,
        "card": content["card"],
        "share_url": f"{base_url}/share/{slug}",
    }


# --- Referral ---
@router.get("/referral/code")
async def get_referral_code(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get or create user referral code."""
    if not await get_growth_feature_enabled(db, "referral_enabled"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Referrals disabled")
    code = await get_or_create_referral_code(db, current_user.id)
    await db.commit()
    settings = get_settings()
    base_url = settings.app_base_url.rstrip("/")
    return {
        "code": code,
        "invite_url": f"{base_url}/register?ref={code}",
    }


# --- SEO (public) ---
@router.get("/seo/pages")
async def list_seo_pages_route(
    db: Annotated[AsyncSession, Depends(get_db)],
    page_type: str | None = Query(None),
):
    """List published SEO pages. Public."""
    pages = await list_seo_pages(db, page_type=page_type)
    return [{"slug": p.slug, "page_type": p.page_type, "title": p.title} for p in pages]


@router.get("/seo/pages/{slug}")
async def get_seo_page_route(
    slug: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get SEO page by slug. Public."""
    page = await get_seo_page_by_slug(db, slug)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return {
        "slug": page.slug,
        "page_type": page.page_type,
        "title": page.title,
        "meta_description": page.meta_description,
        "content": page.content,
        "internal_links": page.internal_links or [],
    }


# --- Creator growth (public) ---


@router.get("/featured-creators")
async def list_featured_creators(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
):
    """List featured creators. Public."""
    creators = await get_featured_creators(db, limit=limit)
    return creators


# --- Admin ---
class GrowthSettingsUpdate(BaseModel):
    features: dict[str, bool] | None = None
    incentives: dict[str, Any] | None = None
    campaigns: dict[str, Any] | None = None


@router.get("/admin/settings")
async def admin_get_growth_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: get growth settings."""
    settings = await get_growth_settings(db)
    return settings


@router.patch("/admin/settings")
async def admin_update_growth_settings(
    data: GrowthSettingsUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: update growth features, incentives, campaigns."""
    if data.features:
        await update_growth_setting(db, "features", data.features)
    if data.incentives:
        await update_growth_setting(db, "incentives", data.incentives)
    if data.campaigns:
        await update_growth_setting(db, "campaigns", data.campaigns)
    await db.commit()
    return await get_growth_settings(db)
