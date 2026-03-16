"""Entitlement grants service - admin manual grants."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import EntitlementAuditLog, EntitlementGrant, Plan, User


GRANT_REASONS = [
    "family",
    "founder",
    "beta_tester",
    "partner",
    "internal_use",
    "scholarship",
    "support_resolution",
    "custom",
]

ON_EXPIRY_OPTIONS = ["revert_previous", "revert_free", "prompt_billing"]

ACCESS_TYPES = ["paid", "discounted", "free"]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


async def create_grant(
    db: AsyncSession,
    user_id: UUID,
    plan_id: UUID,
    granted_by_id: UUID,
    *,
    expires_at: datetime | None = None,
    duration_months: int | None = None,
    duration_years: int | None = None,
    reason: str = "support_resolution",
    reason_custom: str | None = None,
    access_type: str = "free",
    override_stripe: bool = True,
    on_expiry: str = "revert_free",
    internal_notes: str | None = None,
) -> EntitlementGrant:
    """Create an entitlement grant."""
    if expires_at is None and (duration_months or duration_years):
        now = _now_utc()
        if duration_years:
            expires_at = now + timedelta(days=365 * duration_years)
        elif duration_months:
            expires_at = now + timedelta(days=30 * duration_months)

    grant = EntitlementGrant(
        user_id=user_id,
        plan_id=plan_id,
        granted_by_id=granted_by_id,
        expires_at=expires_at,
        reason=reason,
        reason_custom=reason_custom if reason == "custom" else None,
        access_type=access_type,
        override_stripe=override_stripe,
        on_expiry=on_expiry,
        internal_notes=internal_notes,
    )
    db.add(grant)
    await db.flush()

    await _audit(
        db,
        action="grant_created",
        entity_type="grant",
        entity_id=grant.id,
        user_id=user_id,
        performed_by_id=granted_by_id,
        details={
            "plan_id": str(plan_id),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "reason": reason,
            "access_type": access_type,
            "override_stripe": override_stripe,
        },
    )
    return grant


async def revoke_grant(
    db: AsyncSession,
    grant_id: UUID,
    revoked_by_id: UUID,
    reason: str | None = None,
) -> EntitlementGrant | None:
    """Revoke an entitlement grant."""
    grant = await db.get(EntitlementGrant, grant_id)
    if not grant or grant.revoked_at:
        return None
    grant.revoked_at = _now_utc()
    grant.revoke_reason = reason
    await db.flush()

    await _audit(
        db,
        action="grant_revoked",
        entity_type="grant",
        entity_id=grant.id,
        user_id=grant.user_id,
        performed_by_id=revoked_by_id,
        details={"reason": reason},
    )
    return grant


async def extend_grant(
    db: AsyncSession,
    grant_id: UUID,
    extended_by_id: UUID,
    new_expires_at: datetime,
) -> EntitlementGrant | None:
    """Extend a grant's expiry date."""
    grant = await db.get(EntitlementGrant, grant_id)
    if not grant or grant.revoked_at:
        return None
    old_expires = grant.expires_at
    grant.expires_at = new_expires_at
    await db.flush()

    await _audit(
        db,
        action="grant_extended",
        entity_type="grant",
        entity_id=grant.id,
        user_id=grant.user_id,
        performed_by_id=extended_by_id,
        details={
            "old_expires_at": old_expires.isoformat() if old_expires else None,
            "new_expires_at": new_expires_at.isoformat(),
        },
    )
    return grant


async def convert_grant_to_lifetime(
    db: AsyncSession,
    grant_id: UUID,
    converted_by_id: UUID,
) -> EntitlementGrant | None:
    """Convert a time-limited grant to lifetime (remove expiry)."""
    grant = await db.get(EntitlementGrant, grant_id)
    if not grant or grant.revoked_at:
        return None
    grant.expires_at = None
    await db.flush()

    await _audit(
        db,
        action="grant_converted_to_lifetime",
        entity_type="grant",
        entity_id=grant.id,
        user_id=grant.user_id,
        performed_by_id=converted_by_id,
        details={},
    )
    return grant


async def list_grants_for_user(
    db: AsyncSession,
    user_id: UUID,
    include_revoked: bool = False,
) -> list[EntitlementGrant]:
    """List grants for a user."""
    q = select(EntitlementGrant).where(EntitlementGrant.user_id == user_id)
    if not include_revoked:
        q = q.where(EntitlementGrant.revoked_at.is_(None))
    q = q.order_by(EntitlementGrant.granted_at.desc())
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
