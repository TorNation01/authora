"""Billing service - plan resolution, limits, usage metering, feature gating.

Works without live billing: when feature_billing is False, all users get premium
(no limits). When True, free plan is default; premium via admin override or Stripe.
"""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models import Book, Plan, Project, Subscription, UsageRecord, User

FREE_PLAN_SLUG = "free"
PREMIUM_PLAN_SLUG = "premium"


def _period_str(d: date | None = None) -> str:
    """Return YYYY-MM for current or given date."""
    d = d or date.today()
    return d.strftime("%Y-%m")


async def get_plan_by_slug(db: AsyncSession, slug: str) -> Plan | None:
    """Get plan by slug."""
    r = await db.execute(select(Plan).where(Plan.slug == slug))
    return r.scalar_one_or_none()


async def get_user_plan(db: AsyncSession, user_id: UUID) -> Plan:
    """Resolve user's effective plan. Admin override and billing_exempt take precedence."""
    settings = get_settings()
    if not getattr(settings, "feature_billing", False):
        premium = await get_plan_by_slug(db, PREMIUM_PLAN_SLUG)
        return premium or (await get_plan_by_slug(db, FREE_PLAN_SLUG))

    r = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = r.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    # Admin override: use override plan or premium
    if getattr(user, "billing_exempt", False):
        premium = await get_plan_by_slug(db, PREMIUM_PLAN_SLUG)
        return premium or (await get_plan_by_slug(db, FREE_PLAN_SLUG))
    if getattr(user, "plan_override_id", None):
        r2 = await db.get(Plan, user.plan_override_id)
        if r2:
            return r2

    # Active subscription
    r3 = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.status == "active")
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    sub = r3.scalar_one_or_none()
    if sub:
        await db.refresh(sub, ["plan"])
        return sub.plan

    # Default: free
    free = await get_plan_by_slug(db, FREE_PLAN_SLUG)
    return free or (await get_plan_by_slug(db, PREMIUM_PLAN_SLUG))


async def get_usage(db: AsyncSession, user_id: UUID, period: str, metric: str) -> int:
    """Get usage value for user/period/metric."""
    r = await db.execute(
        select(UsageRecord).where(
            UsageRecord.user_id == user_id,
            UsageRecord.period == period,
            UsageRecord.metric == metric,
        )
    )
    rec = r.scalar_one_or_none()
    return rec.value if rec else 0


async def record_usage(db: AsyncSession, user_id: UUID, metric: str, amount: int = 1) -> int:
    """Increment usage for current period. Returns new total."""
    period = _period_str()
    r = await db.execute(
        select(UsageRecord).where(
            UsageRecord.user_id == user_id,
            UsageRecord.period == period,
            UsageRecord.metric == metric,
        )
    )
    rec = r.scalar_one_or_none()
    if rec:
        rec.value += amount
        await db.flush()
        return rec.value
    rec = UsageRecord(user_id=user_id, period=period, metric=metric, value=amount)
    db.add(rec)
    await db.flush()
    return amount


async def get_limit(db: AsyncSession, user_id: UUID, limit_key: str) -> int:
    """Get plan limit for key. -1 means unlimited."""
    plan = await get_user_plan(db, user_id)
    limits = plan.limits or {}
    val = limits.get(limit_key)
    if val is None:
        return -1
    return int(val)


async def check_limit(
    db: AsyncSession,
    user_id: UUID,
    limit_key: str,
    current_count: int,
) -> tuple[bool, int]:
    """Check if current_count is within limit. Returns (allowed, limit)."""
    limit = await get_limit(db, user_id, limit_key)
    if limit < 0:
        return True, -1
    return current_count < limit, limit


async def has_feature(db: AsyncSession, user_id: UUID, feature: str) -> bool:
    """Check if user's plan includes feature."""
    plan = await get_user_plan(db, user_id)
    features = plan.features or []
    return feature in features


async def check_project_limit(db: AsyncSession, user_id: UUID) -> tuple[bool, int, int]:
    """Check if user can create another project. Returns (allowed, current, limit)."""
    r = await db.execute(select(Project).where(Project.user_id == user_id))
    count = len(r.scalars().all())
    limit = await get_limit(db, user_id, "projects")
    if limit < 0:
        return True, count, -1
    return count < limit, count, limit


async def check_book_limit(db: AsyncSession, user_id: UUID) -> tuple[bool, int, int]:
    """Check if user can create another book (total across projects)."""
    r = await db.execute(
        select(Book).join(Project).where(Project.user_id == user_id)
    )
    count = len(r.scalars().all())
    limit = await get_limit(db, user_id, "books")
    if limit < 0:
        return True, count, -1
    return count < limit, count, limit


async def check_ai_action_limit(db: AsyncSession, user_id: UUID) -> tuple[bool, int, int]:
    """Check if user can run another AI action this month."""
    period = _period_str()
    used = await get_usage(db, user_id, period, "ai_actions")
    limit = await get_limit(db, user_id, "ai_actions_per_month")
    if limit < 0:
        return True, used, -1
    return used < limit, used, limit


async def check_export_limit(db: AsyncSession, user_id: UUID, format: str) -> tuple[bool, int, int]:
    """Check if user can export (count + format)."""
    period = _period_str()
    used = await get_usage(db, user_id, period, "exports")
    limit = await get_limit(db, user_id, "exports_per_month")
    if limit < 0:
        return True, used, -1
    # Check format allowance
    plan = await get_user_plan(db, user_id)
    formats = (plan.limits or {}).get("export_formats") or ["docx", "txt"]
    if format.lower() not in [f.lower() for f in formats]:
        return False, used, limit
    return used < limit, used, limit
