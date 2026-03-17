"""Affiliate API: apply, dashboard, payouts, tracking, admin."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import AdminUser, CurrentUser
from authora.config import get_settings
from authora.database import get_db
from authora.services.affiliate_service import (
    apply_as_affiliate,
    approve_affiliate,
    approve_payout,
    export_affiliate_report,
    flag_conversion_fraud,
    get_affiliate_by_user,
    get_affiliate_dashboard,
    get_affiliate_settings,
    get_top_performers,
    list_affiliates_admin,
    list_payouts_admin,
    mark_payout_paid,
    record_click,
    reject_affiliate,
    reject_payout,
    request_payout,
)
from authora.services.growth_service import update_growth_setting

router = APIRouter(prefix="/affiliates", tags=["affiliates"])


def _affiliate_enabled() -> None:
    if not get_settings().feature_affiliate:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Affiliate system disabled")


# --- Affiliate (authenticated) ---


class ApplyRequest(BaseModel):
    application_note: str | None = None


@router.post("/apply")
async def apply_affiliate(
    data: ApplyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Apply to become an affiliate."""
    _affiliate_enabled()
    try:
        profile = await apply_as_affiliate(db, current_user.id, application_note=data.application_note)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {
        "id": str(profile.id),
        "code": profile.code,
        "status": profile.status,
        "message": "Application submitted. You will be notified when reviewed.",
    }


@router.get("/dashboard")
async def dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Get affiliate dashboard (link, clicks, conversions, earnings, payouts)."""
    _affiliate_enabled()
    data = await get_affiliate_dashboard(db, current_user.id)
    if "error" in data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not an affiliate")
    return data


class PayoutRequest(BaseModel):
    amount_cents: int = Field(..., ge=100)


@router.post("/payout")
async def payout_request(
    data: PayoutRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    """Request payout."""
    _affiliate_enabled()
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


# --- Tracking (public) ---


@router.get("/track")
async def track_click(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    aff: str = Query(..., alias="aff", description="Affiliate code"),
    landing: str | None = Query(None, description="Landing path (e.g. /pricing)"),
):
    """Record affiliate link click. Public, no auth. Use: GET /affiliates/track?aff=CODE"""
    _affiliate_enabled()
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    landing_path = landing or "/"
    referrer = request.headers.get("referer")
    click = await record_click(
        db, aff, ip=ip, user_agent=user_agent, landing_path=landing_path, referrer=referrer
    )
    await db.commit()
    if not click:
        return {"recorded": False, "reason": "invalid_or_inactive"}
    return {"recorded": True, "click_id": str(click.id)}


# --- Admin ---


@router.get("/admin/list")
async def admin_list_affiliates(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Admin: list affiliates with stats."""
    _affiliate_enabled()
    rows = await list_affiliates_admin(db, status=status_filter, limit=limit, offset=offset)
    return [
        {
            "id": str(p.id),
            "user_id": str(p.user_id),
            "code": p.code,
            "status": p.status,
            "commission_rate_pct": float(p.commission_rate_pct),
            "clicks": clicks,
            "conversions": convs,
            "applied_at": p.applied_at.isoformat() if p.applied_at else None,
        }
        for p, clicks, convs in rows
    ]


@router.post("/admin/{profile_id}/approve")
async def admin_approve(
    profile_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
    commission_rate_pct: float | None = Query(None),
    commission_recurring_pct: float | None = Query(None),
):
    """Admin: approve affiliate."""
    _affiliate_enabled()
    import uuid
    try:
        pid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid profile ID")
    try:
        profile = await approve_affiliate(
            db, pid,
            commission_rate_pct=commission_rate_pct,
            commission_recurring_pct=commission_recurring_pct,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {"id": str(profile.id), "status": profile.status}


class RejectRequest(BaseModel):
    rejection_reason: str | None = None


@router.post("/admin/{profile_id}/reject")
async def admin_reject(
    profile_id: str,
    data: RejectRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: reject affiliate."""
    _affiliate_enabled()
    import uuid
    try:
        pid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid profile ID")
    try:
        profile = await reject_affiliate(db, pid, rejection_reason=data.rejection_reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {"id": str(profile.id), "status": profile.status}


@router.get("/admin/top")
async def admin_top_performers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
    limit: int = Query(10, ge=1, le=50),
):
    """Admin: top affiliates by commission."""
    _affiliate_enabled()
    return await get_top_performers(db, limit=limit)


@router.get("/admin/payouts")
async def admin_list_payouts(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Admin: list payout requests."""
    _affiliate_enabled()
    payouts = await list_payouts_admin(db, status=status_filter, limit=limit, offset=offset)
    return [
        {
            "id": str(p.id),
            "affiliate_id": str(p.affiliate_id),
            "amount_cents": p.amount_cents,
            "status": p.status,
            "requested_at": p.requested_at.isoformat() if p.requested_at else None,
            "approved_at": p.approved_at.isoformat() if p.approved_at else None,
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
        }
        for p in payouts
    ]


class MarkPaidRequest(BaseModel):
    stripe_payout_id: str | None = None
    payment_details: dict[str, Any] | None = None


@router.post("/admin/payouts/{payout_id}/approve")
async def admin_approve_payout(
    payout_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: approve payout request."""
    _affiliate_enabled()
    import uuid
    try:
        pid = uuid.UUID(payout_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payout ID")
    try:
        payout = await approve_payout(db, pid)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {"id": str(payout.id), "status": payout.status}


@router.post("/admin/payouts/{payout_id}/reject")
async def admin_reject_payout(
    payout_id: str,
    data: RejectRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: reject payout request."""
    _affiliate_enabled()
    import uuid
    try:
        pid = uuid.UUID(payout_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payout ID")
    try:
        payout = await reject_payout(db, pid, rejection_reason=data.rejection_reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {"id": str(payout.id), "status": payout.status}


@router.post("/admin/payouts/{payout_id}/mark-paid")
async def admin_mark_payout_paid(
    payout_id: str,
    data: MarkPaidRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: mark payout as paid (manual or Stripe)."""
    _affiliate_enabled()
    import uuid
    try:
        pid = uuid.UUID(payout_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payout ID")
    try:
        payout = await mark_payout_paid(
            db, pid,
            stripe_payout_id=data.stripe_payout_id,
            payment_details=data.payment_details,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {"id": str(payout.id), "status": payout.status}


@router.get("/admin/settings")
async def admin_get_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: get affiliate settings."""
    _affiliate_enabled()
    return await get_affiliate_settings(db)


class AffiliateSettingsUpdate(BaseModel):
    enabled: bool | None = None
    default_commission_pct: float | None = None
    recurring_commission_pct: float | None = None
    min_payout_cents: int | None = None
    cookie_days: int | None = None


@router.get("/admin/export")
async def admin_export_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
    from_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
    to_date: str | None = Query(None, description="ISO date YYYY-MM-DD"),
):
    """Admin: export affiliate report (conversions, commissions)."""
    _affiliate_enabled()
    from datetime import datetime, timezone
    fd = datetime.fromisoformat(from_date.replace("Z", "+00:00")) if from_date else None
    td = datetime.fromisoformat(to_date.replace("Z", "+00:00")) if to_date else None
    return await export_affiliate_report(db, from_date=fd, to_date=td)


class FlagFraudRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=255)


@router.post("/admin/conversions/{conversion_id}/flag-fraud")
async def admin_flag_fraud(
    conversion_id: str,
    data: FlagFraudRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: flag conversion as fraud."""
    _affiliate_enabled()
    import uuid
    try:
        cid = uuid.UUID(conversion_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversion ID")
    try:
        conv = await flag_conversion_fraud(db, cid, data.reason)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await db.commit()
    return {"id": str(conv.id), "fraud_flagged": True}


@router.patch("/admin/settings")
async def admin_update_settings(
    data: AffiliateSettingsUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: AdminUser,
):
    """Admin: update affiliate settings."""
    _affiliate_enabled()
    settings = await get_affiliate_settings(db)
    updates: dict[str, Any] = {}
    if data.enabled is not None:
        updates["enabled"] = data.enabled
    if data.default_commission_pct is not None:
        updates["default_commission_pct"] = data.default_commission_pct
    if data.recurring_commission_pct is not None:
        updates["recurring_commission_pct"] = data.recurring_commission_pct
    if data.min_payout_cents is not None:
        updates["min_payout_cents"] = data.min_payout_cents
    if data.cookie_days is not None:
        updates["cookie_days"] = data.cookie_days
    if updates:
        await update_growth_setting(db, "affiliate", updates)
    await db.commit()
    return await get_affiliate_settings(db)
