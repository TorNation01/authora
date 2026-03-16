"""Promo codes service - admin access codes."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import EntitlementAuditLog, EntitlementGrant, PromoCode, PromoCodeRedemption, User


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def create_promo_code(
    db: AsyncSession,
    code: str,
    plan_id: UUID,
    created_by_id: UUID,
    *,
    discount_type: str = "free",
    discount_value: int | None = None,
    duration_months: int | None = None,
    duration_years: int | None = None,
    expires_at: datetime | None = None,
    max_uses: int | None = None,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
    internal_note: str | None = None,
    is_stripe_compatible: bool = False,
    allowed_user_ids: list[UUID] | None = None,
) -> PromoCode:
    """Create a promo code."""
    pc = PromoCode(
        code=code.strip().upper(),
        plan_id=plan_id,
        discount_type=discount_type,
        discount_value=discount_value,
        duration_months=duration_months,
        duration_years=duration_years,
        expires_at=expires_at,
        max_uses=max_uses,
        created_by_id=created_by_id,
        valid_from=valid_from,
        valid_until=valid_until,
        internal_note=internal_note,
        is_stripe_compatible=is_stripe_compatible,
        allowed_user_ids=allowed_user_ids,
    )
    db.add(pc)
    await db.flush()

    await _audit(
        db,
        action="code_created",
        entity_type="promo_code",
        entity_id=pc.id,
        user_id=None,
        performed_by_id=created_by_id,
        details={"code": pc.code, "plan_id": str(plan_id)},
    )
    return pc


async def redeem_promo_code(
    db: AsyncSession,
    code: str,
    user_id: UUID,
    *,
    create_grant: bool = True,
    granted_by_id: UUID | None = None,
) -> tuple[PromoCode | None, EntitlementGrant | None, str | None]:
    """
    Redeem a promo code for a user.
    Returns (promo_code, grant_or_none, error_message).
    If create_grant=True and not is_stripe_compatible, creates an EntitlementGrant.
    """
    now = _now_utc()
    r = await db.execute(
        select(PromoCode).where(
            PromoCode.code == code.strip().upper(),
            PromoCode.revoked_at.is_(None),
        )
    )
    pc = r.scalar_one_or_none()
    if not pc:
        return None, None, "Invalid or revoked code"

    if pc.valid_from and now < pc.valid_from:
        return None, None, "Code not yet valid"
    if pc.valid_until and now > pc.valid_until:
        return None, None, "Code has expired"
    if pc.expires_at and now > pc.expires_at:
        return None, None, "Code has expired"
    if pc.max_uses is not None and pc.use_count >= pc.max_uses:
        return None, None, "Code has reached max redemptions"
    if pc.allowed_user_ids and user_id not in pc.allowed_user_ids:
        return None, None, "Code not valid for this account"

    # Check if user already redeemed
    r2 = await db.execute(
        select(PromoCodeRedemption).where(
            PromoCodeRedemption.promo_code_id == pc.id,
            PromoCodeRedemption.user_id == user_id,
        )
    )
    if r2.scalar_one_or_none():
        return None, None, "Code already redeemed by this account"

    grant = None
    if create_grant and not pc.is_stripe_compatible and granted_by_id:
        expires_at = None
        if pc.duration_years:
            expires_at = now + timedelta(days=365 * pc.duration_years)
        elif pc.duration_months:
            expires_at = now + timedelta(days=30 * pc.duration_months)
        elif pc.expires_at:
            expires_at = pc.expires_at

        grant = EntitlementGrant(
            user_id=user_id,
            plan_id=pc.plan_id,
            granted_by_id=granted_by_id or user_id,
            expires_at=expires_at,
            reason="promo_code",
            reason_custom=pc.code,
            access_type="free" if pc.discount_type == "free" else "discounted",
            override_stripe=True,
            on_expiry="revert_free",
        )
        db.add(grant)
        await db.flush()

    redemption = PromoCodeRedemption(
        promo_code_id=pc.id,
        user_id=user_id,
        entitlement_grant_id=grant.id if grant else None,
    )
    db.add(redemption)
    pc.use_count += 1
    await db.flush()

    await _audit(
        db,
        action="code_redeemed",
        entity_type="promo_code",
        entity_id=pc.id,
        user_id=user_id,
        performed_by_id=granted_by_id or user_id,
        details={"code": pc.code, "grant_id": str(grant.id) if grant else None},
    )
    return pc, grant, None


async def revoke_promo_code(
    db: AsyncSession,
    code_id: UUID,
    revoked_by_id: UUID,
) -> PromoCode | None:
    """Revoke a promo code (disable future redemptions)."""
    pc = await db.get(PromoCode, code_id)
    if not pc or pc.revoked_at:
        return None
    pc.revoked_at = _now_utc()
    await db.flush()

    await _audit(
        db,
        action="code_revoked",
        entity_type="promo_code",
        entity_id=pc.id,
        user_id=None,
        performed_by_id=revoked_by_id,
        details={"code": pc.code},
    )
    return pc


async def list_promo_codes(
    db: AsyncSession,
    include_revoked: bool = False,
) -> list[PromoCode]:
    """List all promo codes."""
    q = select(PromoCode).order_by(PromoCode.created_at.desc())
    if not include_revoked:
        q = q.where(PromoCode.revoked_at.is_(None))
    r = await db.execute(q)
    return list(r.scalars().all())


async def _audit(
    db: AsyncSession,
    *,
    action: str,
    entity_type: str,
    entity_id: UUID | None,
    user_id: UUID | None,
    performed_by_id: UUID,
    details: dict | None = None,
) -> None:
    """Write audit log entry."""
    log = EntitlementAuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        performed_by_id=performed_by_id,
    )
    db.add(log)
    await db.flush()
