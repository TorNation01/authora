"""Creator service: apply, approve, dashboard, template submissions."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import CreatorProfile, TemplateSubmission, User
from authora.models.template_marketplace import (
    SUBMISSION_STATUS_CHANGES_REQUESTED,
    SUBMISSION_STATUS_PENDING,
)

CREATOR_STATUS_PENDING = "pending"
CREATOR_STATUS_APPROVED = "approved"
CREATOR_STATUS_REJECTED = "rejected"


async def apply_as_creator(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    application_note: str | None = None,
) -> CreatorProfile:
    """Apply to become a creator. Creates pending profile or re-applies if rejected."""
    r = await db.execute(select(CreatorProfile).where(CreatorProfile.user_id == user_id))
    existing = r.scalar_one_or_none()
    if existing:
        if existing.status == CREATOR_STATUS_APPROVED:
            raise ValueError("Already an approved creator")
        if existing.status == CREATOR_STATUS_PENDING:
            raise ValueError("Application already pending")
        existing.status = CREATOR_STATUS_PENDING
        existing.application_note = application_note
        existing.rejection_reason = None
        existing.rejected_at = None
        existing.applied_at = datetime.now(timezone.utc)
        await db.flush()
        return existing

    profile = CreatorProfile(
        user_id=user_id,
        status=CREATOR_STATUS_PENDING,
        application_note=application_note,
    )
    db.add(profile)
    await db.flush()
    return profile


async def get_creator_by_user(db: AsyncSession, user_id: uuid.UUID) -> CreatorProfile | None:
    """Get creator profile for user."""
    r = await db.execute(select(CreatorProfile).where(CreatorProfile.user_id == user_id))
    return r.scalar_one_or_none()


async def is_approved_creator(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Check if user is an approved creator."""
    r = await db.execute(
        select(CreatorProfile).where(
            CreatorProfile.user_id == user_id,
            CreatorProfile.status == CREATOR_STATUS_APPROVED,
        )
    )
    return r.scalar_one_or_none() is not None


async def approve_creator(
    db: AsyncSession,
    profile_id: uuid.UUID,
) -> CreatorProfile:
    """Admin: approve creator."""
    profile = await db.get(CreatorProfile, profile_id)
    if not profile:
        raise ValueError("Creator profile not found")
    if profile.status != CREATOR_STATUS_PENDING:
        raise ValueError(f"Cannot approve: status is {profile.status}")
    profile.status = CREATOR_STATUS_APPROVED
    profile.approved_at = datetime.now(timezone.utc)
    profile.rejection_reason = None
    profile.rejected_at = None
    await db.flush()
    return profile


async def reject_creator(
    db: AsyncSession,
    profile_id: uuid.UUID,
    *,
    rejection_reason: str | None = None,
) -> CreatorProfile:
    """Admin: reject creator."""
    profile = await db.get(CreatorProfile, profile_id)
    if not profile:
        raise ValueError("Creator profile not found")
    if profile.status != CREATOR_STATUS_PENDING:
        raise ValueError(f"Cannot reject: status is {profile.status}")
    profile.status = CREATOR_STATUS_REJECTED
    profile.rejected_at = datetime.now(timezone.utc)
    profile.rejection_reason = rejection_reason
    await db.flush()
    return profile


async def get_creator_dashboard(db: AsyncSession, user_id: uuid.UUID) -> dict[str, Any]:
    """Get creator dashboard: profile, submissions, approved templates, performance."""
    profile = await get_creator_by_user(db, user_id)
    if not profile:
        return {"error": "not_creator"}

    if profile.status != CREATOR_STATUS_APPROVED:
        return {
            "profile": {
                "id": str(profile.id),
                "status": profile.status,
                "applied_at": profile.applied_at.isoformat() if profile.applied_at else None,
                "approved_at": profile.approved_at.isoformat() if profile.approved_at else None,
                "rejected_at": profile.rejected_at.isoformat() if profile.rejected_at else None,
                "rejection_reason": profile.rejection_reason,
            },
            "can_access_dashboard": False,
        }

    r_sub = await db.execute(
        select(TemplateSubmission)
        .where(TemplateSubmission.creator_id == user_id)
        .order_by(TemplateSubmission.created_at.desc())
    )
    submissions = list(r_sub.scalars().all())

    return {
        "profile": {
            "id": str(profile.id),
            "status": profile.status,
            "applied_at": profile.applied_at.isoformat() if profile.applied_at else None,
            "approved_at": profile.approved_at.isoformat() if profile.approved_at else None,
        },
        "can_access_dashboard": True,
        "submissions": [
            {
                "id": str(s.id),
                "slug": s.slug,
                "name": s.name,
                "description": s.description,
                "category": s.category,
                "price_cents": s.price_cents,
                "status": s.status,
                "approved_template_id": str(s.approved_template_id) if s.approved_template_id else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "reviewed_at": s.reviewed_at.isoformat() if s.reviewed_at else None,
                "rejected_reason": s.rejected_reason,
                "change_request_reason": getattr(s, "change_request_reason", None),
                "payload": s.payload if s.status in (SUBMISSION_STATUS_PENDING, SUBMISSION_STATUS_CHANGES_REQUESTED) else None,
            }
            for s in submissions
        ],
    }


async def list_creators_admin(
    db: AsyncSession,
    *,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[tuple[CreatorProfile, str | None]]:
    """Admin: list creators with user email."""
    q = select(CreatorProfile, User.email).join(User, CreatorProfile.user_id == User.id)
    if status:
        q = q.where(CreatorProfile.status == status)
    q = q.order_by(CreatorProfile.created_at.desc()).limit(limit).offset(offset)
    r = await db.execute(q)
    return list(r.all())
