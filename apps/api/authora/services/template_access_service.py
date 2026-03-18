"""Template access control - tier and pack gating."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import ProjectTemplate, TemplatePackPurchase
from authora.services.billing_service import get_user_plan

# Plan hierarchy for template access: free < starter < pro < studio < founder_lifetime
PLAN_ORDER = {"free": 0, "starter": 1, "pro": 2, "studio": 3, "founder_lifetime": 4}


def _plan_rank(slug: str) -> int:
    return PLAN_ORDER.get(slug, 0)


def _check_template_access(
    access_level: str,
    premium_pack_slug: str | None,
    user_plan_slug: str,
    purchased_packs: set[str],
) -> tuple[bool, str | None]:
    """
    Check template access without DB. Use with batch results.
    Returns (can_use, required_action).
    """
    if access_level == "free":
        return True, None

    if access_level == "premium_pack" and premium_pack_slug:
        if premium_pack_slug in purchased_packs:
            return True, None
        return False, f"purchase:{premium_pack_slug}"

    user_rank = _plan_rank(user_plan_slug)

    if access_level == "pro":
        if user_rank >= _plan_rank("pro"):
            return True, None
        return False, "upgrade"

    if access_level == "studio":
        if user_rank >= _plan_rank("studio"):
            return True, None
        return False, "upgrade"

    return True, None


async def has_template_access(
    db: AsyncSession,
    user_id: UUID,
    template: ProjectTemplate,
) -> tuple[bool, str | None]:
    """
    Check if user can use this template.
    Returns (can_use, required_action).
    required_action: None if allowed, else "upgrade" | "purchase:{pack_slug}"
    """
    access_level = getattr(template, "access_level", None) or "free"
    pack_slug = getattr(template, "premium_pack_slug", None)

    if access_level == "free":
        return True, None

    if access_level == "premium_pack" and pack_slug:
        r = await db.execute(
            select(TemplatePackPurchase).where(
                TemplatePackPurchase.user_id == user_id,
                TemplatePackPurchase.pack_slug == pack_slug,
            )
        )
        if r.scalar_one_or_none():
            return True, None
        return False, f"purchase:{pack_slug}"

    plan = await get_user_plan(db, user_id)
    plan_slug = getattr(plan, "slug", "free") or "free"
    purchased = await get_user_purchased_packs(db, user_id)
    return _check_template_access(access_level, pack_slug, plan_slug, purchased)


async def get_user_purchased_packs(db: AsyncSession, user_id: UUID) -> set[str]:
    """Return set of pack slugs the user has purchased."""
    r = await db.execute(
        select(TemplatePackPurchase.pack_slug).where(TemplatePackPurchase.user_id == user_id)
    )
    return {row[0] for row in r.all()}
