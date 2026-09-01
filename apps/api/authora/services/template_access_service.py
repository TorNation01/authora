"""Template access control — simplified tier gating for Authora v2.

All templates are either free or pro. Pro+ plans unlock everything.
Founder lifetime bypasses all checks. No more premium packs.
"""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import ProjectTemplate, TemplatePurchase
from authora.services.billing_service import get_user_plan

# Plan hierarchy: free < starter < pro < studio < founder_lifetime
PLAN_ORDER = {"free": 0, "starter": 1, "pro": 2, "studio": 3, "founder_lifetime": 4}


def _plan_rank(slug: str) -> int:
    return PLAN_ORDER.get(slug, 0)


def _check_template_access(
    access_level: str,
    user_plan_slug: str,
    purchased_template_ids: set[UUID] | None = None,
    template_id: UUID | None = None,
) -> tuple[bool, str | None]:
    """Check template access without DB. Returns (can_use, required_action).

    - free: everyone
    - pro: requires pro+ plan
    - creator_paid: requires individual purchase
    - founder_lifetime: bypasses everything
    """
    # Founder gets everything, always
    if user_plan_slug == "founder_lifetime":
        return True, None

    if access_level == "free":
        return True, None

    if access_level == "creator_paid" and template_id and purchased_template_ids:
        if template_id in purchased_template_ids:
            return True, None
        return False, f"purchase_template:{template_id}"

    # Pro templates: need pro or above
    if access_level == "pro":
        if _plan_rank(user_plan_slug) >= _plan_rank("pro"):
            return True, None
        return False, "upgrade"

    # Studio templates: need studio or above
    if access_level == "studio":
        if _plan_rank(user_plan_slug) >= _plan_rank("studio"):
            return True, None
        return False, "upgrade"

    return True, None


async def has_template_access(
    db: AsyncSession,
    user_id: UUID,
    template: ProjectTemplate,
) -> tuple[bool, str | None]:
    """Check if user can use this template. Returns (can_use, required_action)."""
    access_level = getattr(template, "access_level", None) or "free"

    # Founder gets everything
    plan = await get_user_plan(db, user_id)
    plan_slug = getattr(plan, "slug", "free") or "free"
    if plan_slug == "founder_lifetime":
        return True, None

    if access_level == "free":
        return True, None

    if access_level == "creator_paid":
        r = await db.execute(
            select(TemplatePurchase).where(
                TemplatePurchase.user_id == user_id,
                TemplatePurchase.template_id == template.id,
            )
        )
        if r.scalar_one_or_none():
            return True, None
        return False, f"purchase_template:{template.id}"

    # Pro and studio: gated by plan tier
    if access_level in ("pro", "studio"):
        if _plan_rank(plan_slug) >= _plan_rank(access_level):
            return True, None
        return False, "upgrade"

    return True, None


async def get_user_purchased_packs(db: AsyncSession, user_id: UUID) -> set[str]:
    """Deprecated in v2 — packs are folded into plans. Returns empty set."""
    return set()


async def get_user_purchased_template_ids(db: AsyncSession, user_id: UUID) -> set[UUID]:
    """Return set of template IDs the user has purchased (creator templates)."""
    r = await db.execute(
        select(TemplatePurchase.template_id).where(TemplatePurchase.user_id == user_id)
    )
    return {row[0] for row in r.all()}
