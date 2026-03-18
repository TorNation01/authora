"""Creator payout service: earnings, payout requests, admin approval."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    CreatorBalanceAdjustment,
    CreatorEarning,
    CreatorPayout,
    CreatorProfile,
    ProjectTemplate,
    TemplatePurchase,
    User,
)

PAYOUT_STATUS_PENDING = "pending"
PAYOUT_STATUS_APPROVED = "approved"
PAYOUT_STATUS_PAID = "paid"
PAYOUT_STATUS_REJECTED = "rejected"
EARNING_STATUS_PENDING = "pending"
EARNING_STATUS_PAID = "paid"

DEFAULT_REVENUE_SHARE_PCT = 70
DEFAULT_MIN_PAYOUT_CENTS = 1000


async def get_creator_payout_settings(db: AsyncSession) -> dict[str, Any]:
    """Get creator payout settings (from growth_settings or defaults)."""
    from authora.models import GrowthSetting

    r = await db.execute(select(GrowthSetting).where(GrowthSetting.key == "creator_payout"))
    row = r.scalar_one_or_none()
    if not row:
        return {
            "min_payout_cents": DEFAULT_MIN_PAYOUT_CENTS,
            "default_revenue_share_pct": DEFAULT_REVENUE_SHARE_PCT,
        }
    return row.value


async def get_creator_available_balance(db: AsyncSession, creator_id: uuid.UUID) -> int:
    """Available balance = sum(pending earnings) + sum(adjustments) - sum(pending/approved payouts)."""
    r_earnings = await db.execute(
        select(func.coalesce(func.sum(CreatorEarning.amount_cents), 0)).where(
            CreatorEarning.creator_id == creator_id,
            CreatorEarning.status == EARNING_STATUS_PENDING,
        )
    )
    earnings = r_earnings.scalar() or 0

    r_adj = await db.execute(
        select(func.coalesce(func.sum(CreatorBalanceAdjustment.amount_cents), 0)).where(
            CreatorBalanceAdjustment.creator_id == creator_id
        )
    )
    adjustments = r_adj.scalar() or 0

    r_pending = await db.execute(
        select(func.coalesce(func.sum(CreatorPayout.amount_cents), 0)).where(
            CreatorPayout.creator_id == creator_id,
            CreatorPayout.status.in_([PAYOUT_STATUS_PENDING, PAYOUT_STATUS_APPROVED]),
        )
    )
    pending_payouts = r_pending.scalar() or 0

    return earnings + adjustments - pending_payouts


async def get_creator_earnings_dashboard(
    db: AsyncSession,
    creator_id: uuid.UUID,
) -> dict[str, Any]:
    """Earnings dashboard: balance, pending, paid, payout history."""
    available = await get_creator_available_balance(db, creator_id)

    r_total_earned = await db.execute(
        select(func.coalesce(func.sum(CreatorEarning.amount_cents), 0)).where(
            CreatorEarning.creator_id == creator_id
        )
    )
    total_earned = r_total_earned.scalar() or 0

    r_total_adjustments = await db.execute(
        select(func.coalesce(func.sum(CreatorBalanceAdjustment.amount_cents), 0)).where(
            CreatorBalanceAdjustment.creator_id == creator_id
        )
    )
    total_adjustments = r_total_adjustments.scalar() or 0

    r_total_paid = await db.execute(
        select(func.coalesce(func.sum(CreatorPayout.amount_cents), 0)).where(
            CreatorPayout.creator_id == creator_id,
            CreatorPayout.status == PAYOUT_STATUS_PAID,
        )
    )
    total_paid = r_total_paid.scalar() or 0

    r_payouts = await db.execute(
        select(CreatorPayout)
        .where(CreatorPayout.creator_id == creator_id)
        .order_by(CreatorPayout.created_at.desc())
        .limit(20)
    )
    payouts = list(r_payouts.scalars().all())

    settings = await get_creator_payout_settings(db)
    min_cents = settings.get("min_payout_cents", DEFAULT_MIN_PAYOUT_CENTS)

    return {
        "available_balance_cents": available,
        "total_earned_cents": total_earned,
        "total_adjustments_cents": total_adjustments,
        "total_paid_cents": total_paid,
        "min_payout_cents": min_cents,
        "payouts": [
            {
                "id": str(p.id),
                "amount_cents": p.amount_cents,
                "status": p.status,
                "payment_method": p.payment_method,
                "requested_at": p.requested_at.isoformat() if p.requested_at else None,
                "approved_at": p.approved_at.isoformat() if p.approved_at else None,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
                "rejected_at": p.rejected_at.isoformat() if p.rejected_at else None,
                "rejection_reason": p.rejection_reason,
            }
            for p in payouts
        ],
    }


async def request_payout(
    db: AsyncSession,
    creator_id: uuid.UUID,
    amount_cents: int,
) -> CreatorPayout:
    """Request payout. Validates min amount and available balance."""
    profile = await db.execute(
        select(CreatorProfile).where(
            CreatorProfile.user_id == creator_id,
            CreatorProfile.status == "approved",
        )
    )
    if not profile.scalar_one_or_none():
        raise ValueError("Not an approved creator")

    settings = await get_creator_payout_settings(db)
    min_cents = settings.get("min_payout_cents", DEFAULT_MIN_PAYOUT_CENTS)
    if amount_cents < min_cents:
        raise ValueError(f"Minimum payout is ${min_cents / 100:.2f}")

    available = await get_creator_available_balance(db, creator_id)
    if amount_cents > available:
        raise ValueError(f"Insufficient balance. Available: ${available / 100:.2f}")

    payout = CreatorPayout(
        creator_id=creator_id,
        amount_cents=amount_cents,
        status=PAYOUT_STATUS_PENDING,
        payment_method="manual",
    )
    db.add(payout)
    await db.flush()
    return payout


async def create_earning_from_purchase(
    db: AsyncSession,
    template_purchase_id: uuid.UUID,
    template_id: uuid.UUID,
    amount_cents: int,
) -> CreatorEarning | None:
    """Create creator earning when template is purchased. Called from webhook."""
    r = await db.execute(
        select(ProjectTemplate).where(
            ProjectTemplate.id == template_id,
            ProjectTemplate.creator_id.isnot(None),
        )
    )
    template = r.scalar_one_or_none()
    if not template or not template.creator_id:
        return None

    r_profile = await db.execute(
        select(CreatorProfile).where(
            CreatorProfile.user_id == template.creator_id,
            CreatorProfile.status == "approved",
        )
    )
    profile = r_profile.scalar_one_or_none()
    if not profile:
        return None

    revenue_share = float(profile.revenue_share_pct) if profile.revenue_share_pct is not None else None
    if revenue_share is None:
        settings = await get_creator_payout_settings(db)
        revenue_share = float(settings.get("default_revenue_share_pct", DEFAULT_REVENUE_SHARE_PCT))

    creator_cents = int(amount_cents * (revenue_share / 100))
    if creator_cents <= 0:
        return None

    r_existing = await db.execute(
        select(CreatorEarning).where(
            CreatorEarning.template_purchase_id == template_purchase_id
        )
    )
    if r_existing.scalar_one_or_none():
        return None  # Idempotent

    earning = CreatorEarning(
        creator_id=template.creator_id,
        template_purchase_id=template_purchase_id,
        amount_cents=creator_cents,
        status=EARNING_STATUS_PENDING,
    )
    db.add(earning)
    await db.flush()
    return earning


async def approve_payout(db: AsyncSession, payout_id: uuid.UUID) -> CreatorPayout:
    """Admin: approve payout (ready for payment)."""
    payout = await db.get(CreatorPayout, payout_id)
    if not payout:
        raise ValueError("Payout not found")
    if payout.status != PAYOUT_STATUS_PENDING:
        raise ValueError(f"Payout status is {payout.status}")
    payout.status = PAYOUT_STATUS_APPROVED
    payout.approved_at = datetime.now(timezone.utc)
    payout.rejected_at = None
    payout.rejection_reason = None
    await db.flush()
    return payout


async def reject_payout(
    db: AsyncSession,
    payout_id: uuid.UUID,
    *,
    rejection_reason: str | None = None,
) -> CreatorPayout:
    """Admin: reject payout."""
    payout = await db.get(CreatorPayout, payout_id)
    if not payout:
        raise ValueError("Payout not found")
    if payout.status != PAYOUT_STATUS_PENDING:
        raise ValueError(f"Payout status is {payout.status}")
    payout.status = PAYOUT_STATUS_REJECTED
    payout.rejected_at = datetime.now(timezone.utc)
    payout.rejection_reason = rejection_reason
    await db.flush()
    return payout


async def mark_payout_paid(
    db: AsyncSession,
    payout_id: uuid.UUID,
    *,
    stripe_payout_id: str | None = None,
    payment_method: str = "manual",
    payment_details: dict[str, Any] | None = None,
) -> CreatorPayout:
    """Admin: mark payout as paid. Allocates pending earnings to this payout."""
    payout = await db.get(CreatorPayout, payout_id)
    if not payout:
        raise ValueError("Payout not found")
    if payout.status not in (PAYOUT_STATUS_PENDING, PAYOUT_STATUS_APPROVED):
        raise ValueError(f"Cannot mark paid: status is {payout.status}")

    payout.status = PAYOUT_STATUS_PAID
    payout.paid_at = datetime.now(timezone.utc)
    if stripe_payout_id:
        payout.stripe_payout_id = stripe_payout_id
        payout.payment_method = "stripe_connect"
    else:
        payout.payment_method = payment_method
    if payment_details:
        payout.payment_details = payment_details

    r = await db.execute(
        select(CreatorEarning)
        .where(
            CreatorEarning.creator_id == payout.creator_id,
            CreatorEarning.status == EARNING_STATUS_PENDING,
        )
        .order_by(CreatorEarning.created_at.asc())
    )
    earnings = list(r.scalars().all())
    remaining = payout.amount_cents
    for e in earnings:
        if remaining <= 0:
            break
        if e.amount_cents <= remaining:
            e.status = EARNING_STATUS_PAID
            e.payout_id = payout.id
            remaining -= e.amount_cents
        else:
            break
    await db.flush()
    return payout


async def adjust_creator_balance(
    db: AsyncSession,
    creator_id: uuid.UUID,
    amount_cents: int,
    *,
    reason: str | None = None,
    admin_user_id: uuid.UUID | None = None,
) -> CreatorBalanceAdjustment:
    """Admin: adjust creator balance (credit or debit)."""
    adj = CreatorBalanceAdjustment(
        creator_id=creator_id,
        amount_cents=amount_cents,
        reason=reason,
        admin_user_id=admin_user_id,
    )
    db.add(adj)
    await db.flush()
    return adj


async def list_creator_payouts_admin(
    db: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[tuple[CreatorPayout, str | None]]:
    """Admin: list creator payouts with creator email."""
    q = (
        select(CreatorPayout, User.email)
        .join(User, CreatorPayout.creator_id == User.id)
        .order_by(CreatorPayout.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status:
        q = q.where(CreatorPayout.status == status)
    r = await db.execute(q)
    return list(r.all())
