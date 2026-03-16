"""Billing service - plan resolution, limits, usage metering, feature gating.

Entitlement precedence (highest first):
1. billing_exempt / legacy plan_override
2. Active admin grant with override_stripe=True
3. Active Stripe subscription
4. Active admin grant (override_stripe=False, no Stripe)
5. Lifetime subscription
6. Expired grant fallback (revert_previous → Stripe/free, revert_free, prompt_billing)
7. Free plan
"""

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models import Book, EntitlementGrant, Plan, Project, Subscription, UsageRecord, User

FREE_PLAN_SLUG = "free"
STUDIO_PLAN_SLUG = "studio"


def _period_str(d: date | None = None) -> str:
    """Return YYYY-MM for current or given date."""
    d = d or date.today()
    return d.strftime("%Y-%m")


async def get_plan_by_slug(db: AsyncSession, slug: str) -> Plan | None:
    """Get plan by slug."""
    r = await db.execute(select(Plan).where(Plan.slug == slug))
    return r.scalar_one_or_none()


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def _get_active_grant(
    db: AsyncSession, user_id: UUID, override_stripe: bool | None = None
) -> EntitlementGrant | None:
    """Get best active (non-revoked, non-expired) entitlement grant for user."""
    now = _now_utc()
    q = (
        select(EntitlementGrant)
        .where(
            EntitlementGrant.user_id == user_id,
            EntitlementGrant.revoked_at.is_(None),
            or_(
                EntitlementGrant.expires_at.is_(None),
                EntitlementGrant.expires_at > now,
            ),
        )
        .order_by(
            EntitlementGrant.expires_at.desc().nulls_first(),
            EntitlementGrant.granted_at.desc(),
        )
        .limit(1)
    )
    if override_stripe is not None:
        q = q.where(EntitlementGrant.override_stripe == override_stripe)
    r = await db.execute(q)
    return r.scalar_one_or_none()


async def _get_active_subscription(db: AsyncSession, user_id: UUID) -> Subscription | None:
    """Get active Stripe or lifetime subscription for user."""
    now = _now_utc()
    r = await db.execute(
        select(Subscription)
        .where(
            Subscription.user_id == user_id,
            Subscription.status == "active",
            or_(
                Subscription.period_end.is_(None),
                Subscription.period_end > now,
                Subscription.is_lifetime == True,
            ),
        )
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    return r.scalar_one_or_none()


async def get_user_plan(db: AsyncSession, user_id: UUID) -> Plan:
    """Resolve user's effective plan. See module docstring for precedence."""
    settings = get_settings()
    if not getattr(settings, "feature_billing", False):
        studio = await get_plan_by_slug(db, STUDIO_PLAN_SLUG)
        return studio or (await get_plan_by_slug(db, FREE_PLAN_SLUG))

    r = await db.execute(select(User).where(User.id == user_id))
    user = r.scalar_one_or_none()
    if not user:
        raise ValueError("User not found")

    free_plan = await get_plan_by_slug(db, FREE_PLAN_SLUG)
    if not free_plan:
        free_plan = (await db.execute(select(Plan).order_by(Plan.sort_order).limit(1))).scalar_one_or_none()

    # 1. Legacy billing_exempt / plan_override
    if getattr(user, "billing_exempt", False):
        studio = await get_plan_by_slug(db, STUDIO_PLAN_SLUG)
        return studio or free_plan
    if getattr(user, "plan_override_id", None):
        p = await db.get(Plan, user.plan_override_id)
        if p:
            return p

    # 2. Active admin grant with override_stripe=True (overrides Stripe)
    grant_override = await _get_active_grant(db, user_id, override_stripe=True)
    if grant_override:
        await db.refresh(grant_override, ["plan"])
        return grant_override.plan

    # 3. Active Stripe subscription
    sub = await _get_active_subscription(db, user_id)
    if sub and sub.stripe_subscription_id:
        await db.refresh(sub, ["plan"])
        return sub.plan

    # 4. Active admin grant (override_stripe=False) - fills in when no Stripe
    grant_fill = await _get_active_grant(db, user_id, override_stripe=False)
    if grant_fill:
        await db.refresh(grant_fill, ["plan"])
        return grant_fill.plan

    # 5. Lifetime subscription (no Stripe)
    if sub:
        await db.refresh(sub, ["plan"])
        return sub.plan

    # 6. Expired grant fallback - check for most recent expired grant
    r_exp = await db.execute(
        select(EntitlementGrant)
        .where(
            EntitlementGrant.user_id == user_id,
            EntitlementGrant.revoked_at.is_(None),
            EntitlementGrant.expires_at.isnot(None),
            EntitlementGrant.expires_at <= _now_utc(),
        )
        .order_by(EntitlementGrant.expires_at.desc())
        .limit(1)
    )
    expired_grant = r_exp.scalar_one_or_none()
    if expired_grant:
        if expired_grant.on_expiry == "revert_previous":
            sub2 = await _get_active_subscription(db, user_id)
            if sub2:
                await db.refresh(sub2, ["plan"])
                return sub2.plan
        # revert_free or prompt_billing
        return free_plan

    # 7. Free plan
    return free_plan


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
    """Check if user can create another project. Returns (allowed, current, limit). Excludes archived."""
    r = await db.execute(
        select(Project).where(Project.user_id == user_id, Project.deleted_at.is_(None))
    )
    count = len(r.scalars().all())
    limit = await get_limit(db, user_id, "projects")
    if limit < 0:
        return True, count, -1
    return count < limit, count, limit


async def check_book_limit(db: AsyncSession, user_id: UUID) -> tuple[bool, int, int]:
    """Check if user can create another book (total across projects). Excludes archived projects."""
    r = await db.execute(
        select(Book)
        .join(Project)
        .where(Project.user_id == user_id, Project.deleted_at.is_(None), Book.deleted_at.is_(None))
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


async def check_ghostwriter_limit(db: AsyncSession, user_id: UUID) -> tuple[bool, int, int]:
    """Check if user can start another ghostwriter session this month."""
    period = _period_str()
    used = await get_usage(db, user_id, period, "ghostwriter_sessions")
    limit = await get_limit(db, user_id, "ghostwriter_sessions_per_month")
    if limit < 0:
        return True, used, -1
    if limit == 0:
        return False, used, 0
    return used < limit, used, limit


async def check_storage_limit(
    db: AsyncSession, user_id: UUID, additional_mb: int = 0
) -> tuple[bool, int, int]:
    """Check if user has storage headroom. used_mb is approximate (content size)."""
    limit = await get_limit(db, user_id, "storage_mb")
    if limit < 0:
        return True, 0, -1
    import json

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from authora.models import Book, Note

    result = await db.execute(
        select(Book)
        .join(Project, Book.project_id == Project.id)
        .where(Project.user_id == user_id)
        .options(selectinload(Book.chapters))
    )
    books = result.scalars().all()
    used_mb = 0.0
    for b in books:
        for c in b.chapters:
            if c.content:
                used_mb += len(json.dumps(c.content).encode()) / (1024 * 1024)
    notes_result = await db.execute(select(Note).where(Note.user_id == user_id))
    for n in notes_result.scalars().all():
        if n.content:
            used_mb += len(str(n.content).encode()) / (1024 * 1024)
    used_mb = int(used_mb) + 1
    return (used_mb + additional_mb) <= limit, used_mb, limit
