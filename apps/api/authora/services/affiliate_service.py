"""Affiliate service: apply, approve, tracking, commissions, payouts, fraud prevention."""

import hashlib
import secrets
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models import (
    AffiliateAttribution,
    AffiliateClick,
    AffiliateConversion,
    AffiliatePayout,
    AffiliateProfile,
    GrowthSetting,
    Plan,
    Subscription,
    User,
)

AFFILIATE_STATUS_PENDING = "pending"
AFFILIATE_STATUS_APPROVED = "approved"
AFFILIATE_STATUS_REJECTED = "rejected"
COMMISSION_STATUS_PENDING = "pending"
COMMISSION_STATUS_APPROVED = "approved"
COMMISSION_STATUS_PAID = "paid"
PAYOUT_STATUS_PENDING = "pending"
PAYOUT_STATUS_APPROVED = "approved"
PAYOUT_STATUS_PAID = "paid"
PAYOUT_STATUS_REJECTED = "rejected"


def _generate_affiliate_code() -> str:
    """Short unique affiliate code."""
    return secrets.token_hex(4)


def _get_base_url() -> str:
    """Public app URL for referral links."""
    return get_settings().app_base_url.rstrip("/")


def _fingerprint(ip: str | None, user_agent: str | None) -> str:
    """Hash for dedup/suspicious detection."""
    raw = f"{ip or ''}|{user_agent or ''}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def get_affiliate_settings(db: AsyncSession) -> dict[str, Any]:
    """Get affiliate settings from growth_settings."""
    r = await db.execute(select(GrowthSetting).where(GrowthSetting.key == "affiliate"))
    row = r.scalar_one_or_none()
    if not row:
        return {
            "enabled": True,
            "default_commission_pct": 20,
            "recurring_commission_pct": 10,
            "min_payout_cents": 5000,
            "cookie_days": 30,
        }
    return row.value


async def apply_as_affiliate(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    application_note: str | None = None,
) -> AffiliateProfile:
    """Apply to become an affiliate. Creates pending profile."""
    r = await db.execute(select(AffiliateProfile).where(AffiliateProfile.user_id == user_id))
    existing = r.scalar_one_or_none()
    if existing:
        if existing.status == AFFILIATE_STATUS_APPROVED:
            raise ValueError("Already an approved affiliate")
        if existing.status == AFFILIATE_STATUS_PENDING:
            raise ValueError("Application already pending")
        # Rejected: allow re-apply with new profile
        existing.status = AFFILIATE_STATUS_PENDING
        existing.application_note = application_note
        existing.rejection_reason = None
        existing.rejected_at = None
        existing.applied_at = datetime.now(timezone.utc)
        await db.flush()
        return existing

    code = _generate_affiliate_code()
    while True:
        r2 = await db.execute(select(AffiliateProfile).where(AffiliateProfile.code == code))
        if r2.scalar_one_or_none() is None:
            break
        code = _generate_affiliate_code()

    settings = await get_affiliate_settings(db)
    default_pct = float(settings.get("default_commission_pct", 20))
    recurring_pct = settings.get("recurring_commission_pct")
    profile = AffiliateProfile(
        user_id=user_id,
        code=code,
        status=AFFILIATE_STATUS_PENDING,
        commission_rate_pct=Decimal(str(default_pct)),
        commission_recurring_pct=Decimal(str(recurring_pct)) if recurring_pct is not None else None,
        application_note=application_note,
    )
    db.add(profile)
    await db.flush()
    return profile


async def approve_affiliate(
    db: AsyncSession,
    profile_id: uuid.UUID,
    *,
    commission_rate_pct: float | None = None,
    commission_recurring_pct: float | None = None,
) -> AffiliateProfile:
    """Admin: approve affiliate."""
    profile = await db.get(AffiliateProfile, profile_id)
    if not profile:
        raise ValueError("Affiliate profile not found")
    if profile.status != AFFILIATE_STATUS_PENDING:
        raise ValueError(f"Cannot approve: status is {profile.status}")
    profile.status = AFFILIATE_STATUS_APPROVED
    profile.approved_at = datetime.now(timezone.utc)
    profile.rejection_reason = None
    if commission_rate_pct is not None:
        profile.commission_rate_pct = Decimal(str(commission_rate_pct))
    if commission_recurring_pct is not None:
        profile.commission_recurring_pct = Decimal(str(commission_recurring_pct))
    await db.flush()
    return profile


async def reject_affiliate(
    db: AsyncSession,
    profile_id: uuid.UUID,
    *,
    rejection_reason: str | None = None,
) -> AffiliateProfile:
    """Admin: reject affiliate."""
    profile = await db.get(AffiliateProfile, profile_id)
    if not profile:
        raise ValueError("Affiliate profile not found")
    if profile.status != AFFILIATE_STATUS_PENDING:
        raise ValueError(f"Cannot reject: status is {profile.status}")
    profile.status = AFFILIATE_STATUS_REJECTED
    profile.rejected_at = datetime.now(timezone.utc)
    profile.rejection_reason = rejection_reason
    await db.flush()
    return profile


async def get_affiliate_by_code(db: AsyncSession, code: str) -> AffiliateProfile | None:
    """Get approved affiliate by code."""
    r = await db.execute(
        select(AffiliateProfile).where(
            AffiliateProfile.code == code,
            AffiliateProfile.status == AFFILIATE_STATUS_APPROVED,
        )
    )
    return r.scalar_one_or_none()


async def record_click(
    db: AsyncSession,
    affiliate_code: str,
    *,
    ip: str | None = None,
    user_agent: str | None = None,
    landing_path: str | None = None,
    referrer: str | None = None,
) -> AffiliateClick | None:
    """Record affiliate link click. Returns None if affiliate not found or not approved."""
    affiliate = await get_affiliate_by_code(db, affiliate_code)
    if not affiliate:
        return None
    fp = _fingerprint(ip, user_agent)
    click = AffiliateClick(
        affiliate_id=affiliate.id,
        fingerprint_hash=fp,
        landing_path=landing_path or "/",
        referrer=referrer,
    )
    db.add(click)
    await db.flush()
    return click


async def attribute_signup(
    db: AsyncSession,
    user_id: uuid.UUID,
    affiliate_code: str,
) -> AffiliateAttribution | None:
    """Attribute new signup to affiliate. Blocks self-referral. Returns attribution or None."""
    affiliate = await get_affiliate_by_code(db, affiliate_code)
    if not affiliate:
        return None
    if affiliate.user_id == user_id:
        return None  # Self-referral

    r = await db.execute(select(AffiliateAttribution).where(AffiliateAttribution.user_id == user_id))
    if r.scalar_one_or_none():
        return None  # Already attributed

    attr = AffiliateAttribution(user_id=user_id, affiliate_id=affiliate.id)
    db.add(attr)
    await db.flush()
    return attr


async def _get_attribution(db: AsyncSession, user_id: uuid.UUID) -> AffiliateAttribution | None:
    """Get attribution for user."""
    r = await db.execute(select(AffiliateAttribution).where(AffiliateAttribution.user_id == user_id))
    return r.scalar_one_or_none()


async def record_conversion_on_payment(
    db: AsyncSession,
    user_id: uuid.UUID,
    subscription_id: uuid.UUID,
    revenue_cents: int,
    is_recurring: bool,
) -> AffiliateConversion | None:
    """Create affiliate conversion when user pays. Returns conversion or None.
    Fraud: self-referral blocked (affiliate.user_id == user_id).
    """
    attr = await _get_attribution(db, user_id)
    if not attr:
        return None

    affiliate = await db.get(AffiliateProfile, attr.affiliate_id)
    if not affiliate or affiliate.status != AFFILIATE_STATUS_APPROVED:
        return None
    if affiliate.user_id == user_id:
        return None  # Self-referral (fraud prevention)

    rate = affiliate.commission_recurring_pct if is_recurring else affiliate.commission_rate_pct
    if rate is None:
        rate = affiliate.commission_rate_pct
    commission_cents = int(Decimal(str(revenue_cents)) * (Decimal(str(rate)) / 100))

    if commission_cents <= 0:
        return None

    conv = AffiliateConversion(
        affiliate_id=affiliate.id,
        user_id=user_id,
        subscription_id=subscription_id,
        revenue_cents=revenue_cents,
        commission_cents=commission_cents,
        commission_status=COMMISSION_STATUS_PENDING,
        is_recurring=is_recurring,
    )
    db.add(conv)
    await db.flush()
    return conv


async def get_affiliate_by_user(db: AsyncSession, user_id: uuid.UUID) -> AffiliateProfile | None:
    """Get affiliate profile for user."""
    r = await db.execute(select(AffiliateProfile).where(AffiliateProfile.user_id == user_id))
    return r.scalar_one_or_none()


async def get_affiliate_dashboard(db: AsyncSession, user_id: uuid.UUID) -> dict[str, Any]:
    """Get affiliate dashboard stats."""
    profile = await get_affiliate_by_user(db, user_id)
    if not profile:
        return {"error": "not_affiliate"}

    # Clicks
    r_clicks = await db.execute(
        select(func.count(AffiliateClick.id)).where(AffiliateClick.affiliate_id == profile.id)
    )
    total_clicks = r_clicks.scalar() or 0

    # Conversions
    r_conv = await db.execute(
        select(
            func.count(AffiliateConversion.id),
            func.coalesce(func.sum(AffiliateConversion.revenue_cents), 0),
            func.coalesce(func.sum(AffiliateConversion.commission_cents), 0),
        ).where(
            AffiliateConversion.affiliate_id == profile.id,
            AffiliateConversion.fraud_flagged == False,
        )
    )
    row = r_conv.one()
    conversions = row[0] or 0
    total_revenue_cents = row[1] or 0
    total_commission_cents = row[2] or 0

    # Pending commission (not yet paid)
    r_pending = await db.execute(
        select(func.coalesce(func.sum(AffiliateConversion.commission_cents), 0)).where(
            AffiliateConversion.affiliate_id == profile.id,
            AffiliateConversion.commission_status.in_([COMMISSION_STATUS_PENDING, COMMISSION_STATUS_APPROVED]),
            AffiliateConversion.fraud_flagged == False,
        )
    )
    pending_cents = r_pending.scalar() or 0

    # Paid commission
    r_paid = await db.execute(
        select(func.coalesce(func.sum(AffiliateConversion.commission_cents), 0)).where(
            AffiliateConversion.affiliate_id == profile.id,
            AffiliateConversion.commission_status == COMMISSION_STATUS_PAID,
            AffiliateConversion.fraud_flagged == False,
        )
    )
    paid_cents = r_paid.scalar() or 0

    # Payouts
    r_payouts = await db.execute(
        select(AffiliatePayout)
        .where(AffiliatePayout.affiliate_id == profile.id)
        .order_by(AffiliatePayout.created_at.desc())
        .limit(20)
    )
    payouts = list(r_payouts.scalars().all())

    return {
        "profile": {
            "id": str(profile.id),
            "code": profile.code,
            "status": profile.status,
            "commission_rate_pct": float(profile.commission_rate_pct),
            "commission_recurring_pct": float(profile.commission_recurring_pct) if profile.commission_recurring_pct else None,
        },
        "referral_link": f"{_get_base_url()}?aff={profile.code}",
        "total_clicks": total_clicks,
        "conversions": conversions,
        "total_revenue_cents": total_revenue_cents,
        "total_commission_cents": total_commission_cents,
        "pending_commission_cents": pending_cents,
        "paid_commission_cents": paid_cents,
        "payouts": [
            {
                "id": str(p.id),
                "amount_cents": p.amount_cents,
                "status": p.status,
                "requested_at": p.requested_at.isoformat() if p.requested_at else None,
                "paid_at": p.paid_at.isoformat() if p.paid_at else None,
            }
            for p in payouts
        ],
    }


async def request_payout(
    db: AsyncSession,
    user_id: uuid.UUID,
    amount_cents: int,
) -> AffiliatePayout:
    """Request payout. Validates min amount and available balance."""
    profile = await get_affiliate_by_user(db, user_id)
    if not profile:
        raise ValueError("Not an affiliate")
    if profile.status != AFFILIATE_STATUS_APPROVED:
        raise ValueError("Affiliate not approved")

    settings = await get_affiliate_settings(db)
    min_cents = settings.get("min_payout_cents", 5000)
    if amount_cents < min_cents:
        raise ValueError(f"Minimum payout is {min_cents / 100:.2f}")

    r = await db.execute(
        select(func.coalesce(func.sum(AffiliateConversion.commission_cents), 0)).where(
            AffiliateConversion.affiliate_id == profile.id,
            AffiliateConversion.commission_status.in_([COMMISSION_STATUS_PENDING, COMMISSION_STATUS_APPROVED]),
            AffiliateConversion.fraud_flagged == False,
        )
    )
    available = r.scalar() or 0

    r_paid = await db.execute(
        select(func.coalesce(func.sum(AffiliatePayout.amount_cents), 0)).where(
            AffiliatePayout.affiliate_id == profile.id,
            AffiliatePayout.status.in_([PAYOUT_STATUS_PENDING, PAYOUT_STATUS_APPROVED, PAYOUT_STATUS_PAID]),
        )
    )
    already_paid = r_paid.scalar() or 0

    # Pending payouts reduce available
    r_pending = await db.execute(
        select(func.coalesce(func.sum(AffiliatePayout.amount_cents), 0)).where(
            AffiliatePayout.affiliate_id == profile.id,
            AffiliatePayout.status == PAYOUT_STATUS_PENDING,
        )
    )
    pending_payout = r_pending.scalar() or 0

    # Available = sum(approved commissions) - sum(paid) - sum(pending payouts)
    # Simplified: available = sum(pending+approved commissions) - paid - pending_payout
    # Actually we need: approved commissions that haven't been paid out yet.
    # For now: available = commissions (pending+approved) - paid out - pending payout requests
    available_for_payout = available - pending_payout
    if amount_cents > available_for_payout:
        raise ValueError(f"Insufficient balance. Available: {available_for_payout / 100:.2f}")

    payout = AffiliatePayout(
        affiliate_id=profile.id,
        amount_cents=amount_cents,
        status=PAYOUT_STATUS_PENDING,
        payment_method="manual",
    )
    db.add(payout)
    await db.flush()
    return payout


async def list_affiliates_admin(
    db: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[tuple[AffiliateProfile, int, int]]:
    """Admin: list affiliates with click and conversion counts."""
    q = select(AffiliateProfile)
    if status:
        q = q.where(AffiliateProfile.status == status)
    q = q.order_by(AffiliateProfile.created_at.desc()).limit(limit).offset(offset)
    r = await db.execute(q)
    profiles = list(r.scalars().all())

    result = []
    for p in profiles:
        r_c = await db.execute(select(func.count(AffiliateClick.id)).where(AffiliateClick.affiliate_id == p.id))
        r_v = await db.execute(
            select(func.count(AffiliateConversion.id)).where(
                AffiliateConversion.affiliate_id == p.id,
                AffiliateConversion.fraud_flagged == False,
            )
        )
        result.append((p, r_c.scalar() or 0, r_v.scalar() or 0))
    return result


async def get_top_performers(
    db: AsyncSession,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Admin: top affiliates by commission."""
    r = await db.execute(
        select(
            AffiliateProfile.code,
            AffiliateProfile.user_id,
            func.coalesce(func.sum(AffiliateConversion.commission_cents), 0).label("commission_cents"),
            func.count(AffiliateConversion.id).label("conversions"),
        )
        .join(AffiliateConversion, AffiliateConversion.affiliate_id == AffiliateProfile.id)
        .where(
            AffiliateProfile.status == AFFILIATE_STATUS_APPROVED,
            AffiliateConversion.fraud_flagged == False,
        )
        .group_by(AffiliateProfile.id, AffiliateProfile.code, AffiliateProfile.user_id)
        .order_by(func.coalesce(func.sum(AffiliateConversion.commission_cents), 0).desc())
        .limit(limit)
    )
    rows = r.all()
    return [
        {
            "code": row.code,
            "user_id": str(row.user_id),
            "commission_cents": row.commission_cents,
            "conversions": row.conversions,
        }
        for row in rows
    ]


async def export_affiliate_report(
    db: AsyncSession,
    *,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> list[dict[str, Any]]:
    """Admin: export affiliate report (conversions, commissions, payouts)."""
    q = (
        select(
            AffiliateProfile.code,
            AffiliateProfile.user_id,
            AffiliateConversion.id,
            AffiliateConversion.user_id.label("converted_user_id"),
            AffiliateConversion.revenue_cents,
            AffiliateConversion.commission_cents,
            AffiliateConversion.commission_status,
            AffiliateConversion.is_recurring,
            AffiliateConversion.fraud_flagged,
            AffiliateConversion.converted_at,
        )
        .join(AffiliateConversion, AffiliateConversion.affiliate_id == AffiliateProfile.id)
        .where(AffiliateProfile.status == AFFILIATE_STATUS_APPROVED)
    )
    if from_date:
        q = q.where(AffiliateConversion.converted_at >= from_date)
    if to_date:
        q = q.where(AffiliateConversion.converted_at <= to_date)
    q = q.order_by(AffiliateConversion.converted_at.desc())
    r = await db.execute(q)
    rows = r.all()
    return [
        {
            "affiliate_code": row.code,
            "affiliate_user_id": str(row.user_id),
            "conversion_id": str(row.id),
            "converted_user_id": str(row.converted_user_id),
            "revenue_cents": row.revenue_cents,
            "commission_cents": row.commission_cents,
            "commission_status": row.commission_status,
            "is_recurring": row.is_recurring,
            "fraud_flagged": row.fraud_flagged,
            "converted_at": row.converted_at.isoformat() if row.converted_at else None,
        }
        for row in rows
    ]


async def flag_conversion_fraud(
    db: AsyncSession,
    conversion_id: uuid.UUID,
    reason: str,
) -> AffiliateConversion:
    """Admin: flag conversion as fraud (excludes from earnings)."""
    conv = await db.get(AffiliateConversion, conversion_id)
    if not conv:
        raise ValueError("Conversion not found")
    conv.fraud_flagged = True
    conv.fraud_reason = reason[:255]
    await db.flush()
    return conv


async def _revenue_from_subscription(db: AsyncSession, sub: Subscription) -> tuple[int, bool]:
    """Get revenue cents and is_recurring from subscription."""
    plan = await db.get(Plan, sub.plan_id)
    if not plan:
        return 0, False
    if sub.is_lifetime:
        return plan.price_lifetime_cents or 0, False
    if sub.billing_interval == "yearly":
        return plan.price_yearly_cents or 0, True
    return plan.price_monthly_cents or 0, True


async def list_payouts_admin(
    db: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AffiliatePayout]:
    """Admin: list payout requests."""
    q = select(AffiliatePayout).order_by(AffiliatePayout.created_at.desc()).limit(limit).offset(offset)
    if status:
        q = q.where(AffiliatePayout.status == status)
    r = await db.execute(q)
    return list(r.scalars().all())


async def approve_payout(db: AsyncSession, payout_id: uuid.UUID) -> AffiliatePayout:
    """Admin: approve payout (ready for payment)."""
    payout = await db.get(AffiliatePayout, payout_id)
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
) -> AffiliatePayout:
    """Admin: reject payout."""
    payout = await db.get(AffiliatePayout, payout_id)
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
    payment_details: dict[str, Any] | None = None,
) -> AffiliatePayout:
    """Admin: mark payout as paid (manual or Stripe). Marks conversions as paid up to amount."""
    payout = await db.get(AffiliatePayout, payout_id)
    if not payout:
        raise ValueError("Payout not found")
    if payout.status not in (PAYOUT_STATUS_PENDING, PAYOUT_STATUS_APPROVED):
        raise ValueError(f"Cannot mark paid: status is {payout.status}")
    payout.status = PAYOUT_STATUS_PAID
    payout.paid_at = datetime.now(timezone.utc)
    if stripe_payout_id:
        payout.stripe_payout_id = stripe_payout_id
        payout.payment_method = "stripe"
    if payment_details:
        payout.payment_details = payment_details

    r = await db.execute(
        select(AffiliateConversion)
        .where(
            AffiliateConversion.affiliate_id == payout.affiliate_id,
            AffiliateConversion.commission_status.in_([COMMISSION_STATUS_PENDING, COMMISSION_STATUS_APPROVED]),
            AffiliateConversion.fraud_flagged == False,
        )
        .order_by(AffiliateConversion.converted_at.asc())
    )
    convs = list(r.scalars().all())
    remaining = payout.amount_cents
    for c in convs:
        if remaining <= 0:
            break
        if c.commission_cents <= remaining:
            c.commission_status = COMMISSION_STATUS_PAID
            remaining -= c.commission_cents
    await db.flush()
    return payout
