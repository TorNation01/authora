"""Growth service: share links, content generation, referrals, growth settings."""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import GrowthSetting, Referral, SEOPage, ShareLink, User

SHARE_TYPES = ("progress", "milestone", "achievement", "book_finished")
DEFAULT_SHARE_EXPIRY_DAYS = 90


def _generate_slug() -> str:
    """URL-safe random slug."""
    return secrets.token_urlsafe(12)[:20]


def _generate_referral_code() -> str:
    """Short referral code."""
    return secrets.token_hex(4)


# --- Content generation templates ---
PROGRESS_CAPTIONS = {
    "words_today": "I wrote {words:,} words today. {product}",
    "streak": "Day {streak} of my writing streak. {product}",
    "chapter_done": "Just finished chapter {chapter}. {product}",
    "book_finished": "I finished my book. {product}",
    "milestone": "Hit {milestone} words. {product}",
}

CARD_TEMPLATES = {
    "progress": {
        "title": "Writing Progress",
        "subtitle": "{display_name} wrote {words:,} words",
        "cta": "Start writing",
    },
    "milestone": {
        "title": "Milestone Reached",
        "subtitle": "{display_name} hit {milestone}",
        "cta": "Join AUTHORA",
    },
    "achievement": {
        "title": "Achievement Unlocked",
        "subtitle": "{display_name} earned {badge_name}",
        "cta": "See your potential",
    },
    "book_finished": {
        "title": "Book Complete",
        "subtitle": "{display_name} finished their book",
        "cta": "Write yours",
    },
}


async def get_growth_settings(db: AsyncSession) -> dict[str, Any]:
    """Get merged growth settings."""
    result = await db.execute(select(GrowthSetting))
    rows = result.scalars().all()
    out: dict[str, Any] = {}
    for r in rows:
        out[r.key] = r.value
    return out


async def get_growth_feature_enabled(db: AsyncSession, feature: str) -> bool:
    """Check if growth feature is enabled."""
    settings = await get_growth_settings(db)
    features = settings.get("features", {})
    return features.get(feature, True)


async def create_share_link(
    db: AsyncSession,
    user_id: uuid.UUID,
    share_type: str,
    payload: dict[str, Any],
    *,
    slug: str | None = None,
    expires_days: int = DEFAULT_SHARE_EXPIRY_DAYS,
) -> ShareLink:
    """Create shareable link."""
    if share_type not in SHARE_TYPES:
        raise ValueError(f"Invalid share_type. Must be one of {SHARE_TYPES}")
    slug = slug or _generate_slug()
    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_days) if expires_days > 0 else None
    link = ShareLink(
        user_id=user_id,
        slug=slug,
        share_type=share_type,
        payload=payload,
        expires_at=expires_at,
    )
    db.add(link)
    await db.flush()
    return link


async def get_share_link_by_slug(db: AsyncSession, slug: str) -> ShareLink | None:
    """Get share link by slug. Increments view_count."""
    result = await db.execute(select(ShareLink).where(ShareLink.slug == slug))
    link = result.scalar_one_or_none()
    if link:
        link.view_count += 1
        await db.flush()
    return link


def generate_share_content(
    share_type: str,
    payload: dict[str, Any],
    *,
    product_name: str = "AUTHORA",
    app_url: str = "https://authora.studio",
) -> dict[str, Any]:
    """Generate share card data and captions for social."""
    template = CARD_TEMPLATES.get(share_type, CARD_TEMPLATES["progress"])
    display_name = payload.get("display_name", "A writer")
    card = {
        "title": template["title"],
        "subtitle": template["subtitle"].format(
            display_name=display_name,
            words=payload.get("words", 0),
            milestone=payload.get("milestone", ""),
            badge_name=payload.get("badge_name", ""),
        ),
        "cta": template["cta"],
        "product_name": product_name,
        "share_url": app_url,
    }
    caption_key = payload.get("caption_key", "words_today")
    caption_template = PROGRESS_CAPTIONS.get(caption_key, PROGRESS_CAPTIONS["words_today"])
    caption = caption_template.format(
        words=payload.get("words", 0),
        streak=payload.get("streak", 0),
        chapter=payload.get("chapter", ""),
        milestone=payload.get("milestone", ""),
        badge_name=payload.get("badge_name", ""),
        product=product_name,
    )
    return {
        "card": card,
        "caption": caption,
        "social_links": {
            "twitter": f"https://twitter.com/intent/tweet?text={caption[:200]}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={app_url}",
        },
    }


async def get_or_create_referral_code(db: AsyncSession, user_id: uuid.UUID) -> str:
    """Get or create user referral code. Ensures Referral record exists for signup resolution."""
    from authora.services.network_effect_service import ensure_referral_record

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")
    if user.referral_code:
        await ensure_referral_record(db, user_id, user.referral_code)
        return user.referral_code
    code = _generate_referral_code()
    while True:
        existing = await db.execute(select(User).where(User.referral_code == code))
        if existing.scalar_one_or_none() is None:
            break
        code = _generate_referral_code()
    user.referral_code = code
    await db.flush()
    await ensure_referral_record(db, user_id, code)
    return code


async def create_referral(
    db: AsyncSession,
    inviter_id: uuid.UUID,
    referral_code: str,
    *,
    email: str | None = None,
) -> Referral:
    """Create referral record (pending signup)."""
    ref = Referral(
        inviter_id=inviter_id,
        referral_code=referral_code,
        email=email,
        status="pending",
    )
    db.add(ref)
    await db.flush()
    return ref


async def resolve_referral_on_signup(
    db: AsyncSession,
    invitee_id: uuid.UUID,
    referral_code: str,
) -> Referral | None:
    """Link invitee to referral when they sign up. Returns referral if matched."""
    result = await db.execute(
        select(Referral).where(
            Referral.referral_code == referral_code,
            Referral.status == "pending",
        )
    )
    ref = result.scalar_one_or_none()
    if not ref:
        return None
    ref.invitee_id = invitee_id
    ref.status = "signed_up"
    await db.flush()
    return ref


async def get_seo_page_by_slug(db: AsyncSession, slug: str) -> SEOPage | None:
    """Get published SEO page by slug."""
    result = await db.execute(
        select(SEOPage).where(SEOPage.slug == slug, SEOPage.is_published == True)
    )
    return result.scalar_one_or_none()


async def list_seo_pages(
    db: AsyncSession,
    *,
    page_type: str | None = None,
) -> list[SEOPage]:
    """List published SEO pages."""
    q = select(SEOPage).where(SEOPage.is_published == True)
    if page_type:
        q = q.where(SEOPage.page_type == page_type)
    q = q.order_by(SEOPage.sort_order, SEOPage.slug)
    result = await db.execute(q)
    return list(result.scalars().all())


async def update_growth_setting(
    db: AsyncSession,
    key: str,
    value: dict[str, Any],
) -> GrowthSetting:
    """Update growth setting (admin)."""
    result = await db.execute(select(GrowthSetting).where(GrowthSetting.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = {**row.value, **value}
    else:
        row = GrowthSetting(key=key, value=value)
        db.add(row)
    await db.flush()
    return row
