"""Creator API: apply, dashboard, template submissions, performance."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.services.creator_service import (
    apply_as_creator,
    get_creator_by_user,
    get_creator_dashboard,
    is_approved_creator,
)
from authora.services.creator_payout_service import (
    get_creator_earnings_dashboard,
    request_payout,
)
from authora.services.template_submission_service import (
    create_submission,
    get_creator_performance,
    update_submission,
)

router = APIRouter(prefix="/creators", tags=["creators"])


# --- Apply ---


class ApplyRequest(BaseModel):
    application_note: str | None = None


@router.post("/apply")
async def apply_creator(
    data: ApplyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Apply to become a creator."""
    try:
        profile = await apply_as_creator(
            db, current_user.id, application_note=data.application_note
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {
        "id": str(profile.id),
        "status": profile.status,
        "message": "Application submitted. You will be notified when reviewed.",
    }


@router.get("/status")
async def get_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get creator application status."""
    profile = await get_creator_by_user(db, current_user.id)
    if not profile:
        return {"status": None, "is_creator": False}
    return {
        "status": profile.status,
        "is_creator": profile.status == "approved",
        "applied_at": profile.applied_at.isoformat() if profile.applied_at else None,
        "approved_at": profile.approved_at.isoformat() if profile.approved_at else None,
        "rejected_at": profile.rejected_at.isoformat() if profile.rejected_at else None,
        "rejection_reason": profile.rejection_reason,
    }


# --- Dashboard (approved creators only) ---


@router.get("/dashboard")
async def dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get creator dashboard (submissions, approved templates)."""
    data = await get_creator_dashboard(db, current_user.id)
    if "error" in data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a creator")
    if not data.get("can_access_dashboard"):
        return data
    return data


# --- Template submissions ---


class ValidateSubmissionRequest(BaseModel):
    name: str = Field("", max_length=255)
    description: str | None = None
    payload: dict[str, Any] | None = None


@router.post("/submissions/validate")
async def validate_template_submission(
    data: ValidateSubmissionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Validate template payload before submission. Returns errors and warnings."""
    if not await is_approved_creator(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an approved creator",
        )
    from authora.services.template_validation_service import validate_template_payload

    return validate_template_payload(
        data.payload or {},
        name=data.name,
        description=data.description,
    )


class CreateSubmissionRequest(BaseModel):
    slug: str | None = None
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    price_cents: int | None = Field(None, ge=0)
    payload: dict[str, Any] | None = None


@router.post("/submissions")
async def create_template_submission(
    data: CreateSubmissionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Create template submission. Requires approved creator."""
    if not await is_approved_creator(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an approved creator to submit templates",
        )
    try:
        sub = await create_submission(
            db,
            current_user.id,
            slug=data.slug,
            name=data.name,
            description=data.description,
            category=data.category,
            price_cents=data.price_cents,
            payload=data.payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {
        "id": str(sub.id),
        "slug": sub.slug,
        "name": sub.name,
        "status": sub.status,
        "created_at": sub.created_at.isoformat() if sub.created_at else None,
    }


class UpdateSubmissionRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    category: str | None = None
    price_cents: int | None = Field(None, ge=0)
    payload: dict[str, Any] | None = None


@router.patch("/submissions/{submission_id}")
async def update_template_submission(
    submission_id: str,
    data: UpdateSubmissionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Update pending template submission."""
    if not await is_approved_creator(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an approved creator",
        )
    try:
        sid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID")
    try:
        sub = await update_submission(
            db,
            sid,
            current_user.id,
            name=data.name,
            description=data.description,
            category=data.category,
            price_cents=data.price_cents,
            payload=data.payload,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    if not sub:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    await db.commit()
    return {
        "id": str(sub.id),
        "slug": sub.slug,
        "name": sub.name,
        "status": sub.status,
    }


@router.get("/performance")
async def performance(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get performance stats (usage) for creator's approved templates."""
    if not await is_approved_creator(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an approved creator",
        )
    return await get_creator_performance(db, current_user.id)


# --- Earnings & Payouts ---


@router.get("/earnings")
async def earnings_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get earnings dashboard: balance, totals, payout history."""
    if not await is_approved_creator(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an approved creator",
        )
    return await get_creator_earnings_dashboard(db, current_user.id)


class PayoutRequest(BaseModel):
    amount_cents: int = Field(..., ge=1, description="Amount in cents")


@router.post("/payout")
async def request_payout_endpoint(
    data: PayoutRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Request a payout. Requires approved creator and sufficient balance."""
    if not await is_approved_creator(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must be an approved creator",
        )
    try:
        payout = await request_payout(db, current_user.id, data.amount_cents)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {
        "id": str(payout.id),
        "amount_cents": payout.amount_cents,
        "status": payout.status,
        "requested_at": payout.requested_at.isoformat() if payout.requested_at else None,
    }
