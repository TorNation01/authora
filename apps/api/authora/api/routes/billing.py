"""Billing API - plan status, usage, admin override, grants, promo codes. Stripe-ready."""

import uuid
from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import EntitlementAuditLog, EntitlementGrant, Plan, ProjectTemplate, PromoCode, TemplatePack, TemplatePackPurchase, TemplatePurchase, User
from authora.config import get_settings
from authora.services.billing_service import (
    _period_str,
    check_ai_action_limit,
    check_book_limit,
    check_export_limit,
    check_ghostwriter_limit,
    check_project_limit,
    check_storage_limit,
    get_usage,
    get_user_plan,
    has_feature,
    record_usage,
)
from authora.services.entitlement_grants_service import (
    ON_EXPIRY_OPTIONS,
    ACCESS_TYPES,
    GRANT_REASONS,
    convert_grant_to_lifetime,
    create_grant,
    extend_grant,
    list_grants_for_user,
    revoke_grant,
)
from authora.services.promo_codes_service import (
    create_promo_code,
    list_promo_codes,
    redeem_promo_code,
    revoke_promo_code,
)

router = APIRouter(prefix="/billing", tags=["billing"])


class PlanPriceResponse(BaseModel):
    monthly_cents: int | None = None
    yearly_cents: int | None = None
    lifetime_cents: int | None = None


class PlanResponse(BaseModel):
    id: str
    slug: str
    name: str
    limits: dict
    features: list[str]
    price: PlanPriceResponse | None = None


class UsageResponse(BaseModel):
    ai_actions: int
    ai_actions_limit: int
    exports: int
    exports_limit: int
    projects: int
    projects_limit: int
    books: int
    books_limit: int
    storage_mb: int = 0
    storage_mb_limit: int = -1
    ghostwriter_sessions: int = 0
    ghostwriter_sessions_limit: int = -1


class SubscriptionInfoResponse(BaseModel):
    period_end: str | None = None
    cancel_at_period_end: bool = False
    billing_interval: str | None = None
    is_lifetime: bool = False
    has_stripe_customer: bool = False


class BillingStatusResponse(BaseModel):
    plan: PlanResponse
    usage: UsageResponse
    billing_exempt: bool
    can_upgrade: bool
    feature_billing_enabled: bool = False
    subscription: SubscriptionInfoResponse | None = None
    access_source: str = "free"  # stripe | grant | override | free


async def _get_usage_summary(db: AsyncSession, user_id: uuid.UUID, plan: Plan) -> dict:
    """Build usage summary for user."""
    period = _period_str()
    ai_used = await get_usage(db, user_id, period, "ai_actions")
    ai_limit = plan.limits.get("ai_actions_per_month", -1)
    exp_used = await get_usage(db, user_id, period, "exports")
    exp_limit = plan.limits.get("exports_per_month", -1)
    gw_used = await get_usage(db, user_id, period, "ghostwriter_sessions")
    gw_limit = plan.limits.get("ghostwriter_sessions_per_month", -1)
    _, proj_count, proj_limit = await check_project_limit(db, user_id)
    _, book_count, book_limit = await check_book_limit(db, user_id)
    _, storage_mb, storage_limit = await check_storage_limit(db, user_id)
    return {
        "ai_actions": ai_used,
        "ai_actions_limit": ai_limit if ai_limit >= 0 else 999999,
        "exports": exp_used,
        "exports_limit": exp_limit if exp_limit >= 0 else 999999,
        "projects": proj_count,
        "projects_limit": proj_limit if proj_limit >= 0 else 999999,
        "books": book_count,
        "books_limit": book_limit if book_limit >= 0 else 999999,
        "storage_mb": storage_mb,
        "storage_mb_limit": storage_limit if storage_limit >= 0 else 999999,
        "ghostwriter_sessions": gw_used,
        "ghostwriter_sessions_limit": gw_limit if gw_limit >= 0 else 999999,
    }


@router.get("/status", response_model=BillingStatusResponse)
async def get_billing_status(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current user's plan, usage, subscription, and limits."""
    from authora.services.billing_service import _get_active_grant, _get_active_subscription

    plan = await get_user_plan(db, current_user.id)
    usage = await _get_usage_summary(db, current_user.id, plan)
    r = await db.execute(select(User).where(User.id == current_user.id))
    user = r.scalar_one_or_none()
    billing_exempt = getattr(user, "billing_exempt", False) or bool(getattr(user, "plan_override_id", None))
    settings = get_settings()

    # Resolve access source and subscription info (match get_user_plan precedence)
    access_source = "free"
    subscription_info = None
    grant_override = await _get_active_grant(db, current_user.id, override_stripe=True)
    sub = await _get_active_subscription(db, current_user.id)
    grant_fill = await _get_active_grant(db, current_user.id, override_stripe=False)
    grant = grant_override or grant_fill

    if getattr(user, "plan_override_id", None):
        access_source = "override"
    elif grant_override:
        access_source = "grant"
        subscription_info = SubscriptionInfoResponse(
            period_end=grant_override.expires_at.isoformat() if grant_override.expires_at else None,
            cancel_at_period_end=False,
            billing_interval=None,
            is_lifetime=grant_override.expires_at is None,
            has_stripe_customer=False,
        )
    elif sub and sub.stripe_subscription_id:
        access_source = "stripe"
        subscription_info = SubscriptionInfoResponse(
            period_end=sub.period_end.isoformat() if sub.period_end else None,
            cancel_at_period_end=sub.cancel_at_period_end or False,
            billing_interval=sub.billing_interval,
            is_lifetime=sub.is_lifetime or False,
            has_stripe_customer=bool(sub.stripe_customer_id),
        )
    elif sub and sub.is_lifetime:
        access_source = "stripe"
        subscription_info = SubscriptionInfoResponse(
            period_end=None,
            cancel_at_period_end=False,
            billing_interval=None,
            is_lifetime=True,
            has_stripe_customer=bool(sub.stripe_customer_id),
        )
    elif grant_fill:
        access_source = "grant"
        subscription_info = SubscriptionInfoResponse(
            period_end=grant_fill.expires_at.isoformat() if grant_fill.expires_at else None,
            cancel_at_period_end=False,
            billing_interval=None,
            is_lifetime=grant_fill.expires_at is None,
            has_stripe_customer=False,
        )

    return BillingStatusResponse(
        plan=PlanResponse(
            id=str(plan.id),
            slug=plan.slug,
            name=plan.name,
            limits=plan.limits or {},
            features=plan.features or [],
            price=PlanPriceResponse(
                monthly_cents=getattr(plan, "price_monthly_cents", None),
                yearly_cents=getattr(plan, "price_yearly_cents", None),
                lifetime_cents=getattr(plan, "price_lifetime_cents", None),
            ) if any([getattr(plan, "price_monthly_cents", None), getattr(plan, "price_yearly_cents", None), getattr(plan, "price_lifetime_cents", None)]) else None,
        ),
        usage=UsageResponse(**usage),
        billing_exempt=billing_exempt,
        can_upgrade=plan.slug in ("free", "starter", "pro"),
        feature_billing_enabled=getattr(settings, "feature_billing", False),
        subscription=subscription_info,
        access_source=access_source,
    )


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List available plans (public)."""
    r = await db.execute(select(Plan).order_by(asc(Plan.sort_order)))
    plans = r.scalars().all()
    return [
        PlanResponse(
            id=str(p.id),
            slug=p.slug,
            name=p.name,
            limits=p.limits or {},
            features=p.features or [],
            price=PlanPriceResponse(
                monthly_cents=getattr(p, "price_monthly_cents", None),
                yearly_cents=getattr(p, "price_yearly_cents", None),
                lifetime_cents=getattr(p, "price_lifetime_cents", None),
            ) if any([getattr(p, "price_monthly_cents", None), getattr(p, "price_yearly_cents", None), getattr(p, "price_lifetime_cents", None)]) else None,
        )
        for p in plans
    ]


# --- Admin override ---

class AdminPlanOverride(BaseModel):
    plan_slug: str | None = None
    billing_exempt: bool | None = None


async def _require_admin(current_user: CurrentUser, db: AsyncSession) -> User:
    r = await db.execute(select(User).where(User.id == current_user.id))
    user = r.scalar_one_or_none()
    if not user or not getattr(user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin required")
    return user


@router.patch("/admin/users/{user_id}/plan")
async def admin_set_user_plan(
    user_id: uuid.UUID,
    data: AdminPlanOverride,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: set plan override or billing exempt for a user."""
    await _require_admin(current_user, db)
    r = await db.execute(select(User).where(User.id == user_id))
    target = r.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.plan_slug is not None:
        if data.plan_slug == "":
            target.plan_override_id = None
        else:
            r2 = await db.execute(select(Plan).where(Plan.slug == data.plan_slug))
            plan = r2.scalar_one_or_none()
            if not plan:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
            target.plan_override_id = plan.id

    if data.billing_exempt is not None:
        target.billing_exempt = data.billing_exempt

    await db.commit()
    return {"ok": True}


# --- Admin entitlement grants ---

class GrantCreateRequest(BaseModel):
    user_id: uuid.UUID
    plan_slug: str
    expires_at: datetime | None = None
    duration_months: int | None = None
    duration_years: int | None = None
    reason: str = "support_resolution"
    reason_custom: str | None = None
    access_type: str = "free"
    override_stripe: bool = True
    on_expiry: str = "revert_free"
    internal_notes: str | None = None


class GrantResponse(BaseModel):
    id: str
    user_id: str
    plan_slug: str
    granted_at: str
    expires_at: str | None
    reason: str
    access_type: str
    override_stripe: bool
    on_expiry: str
    revoked_at: str | None


@router.post("/admin/grants", response_model=GrantResponse)
async def admin_create_grant(
    data: GrantCreateRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: create entitlement grant for a user."""
    admin_user = await _require_admin(current_user, db)
    r = await db.execute(select(Plan).where(Plan.slug == data.plan_slug))
    plan = r.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    r2 = await db.execute(select(User).where(User.id == data.user_id))
    target = r2.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if data.reason not in GRANT_REASONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reason")
    if data.on_expiry not in ON_EXPIRY_OPTIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid on_expiry")
    if data.access_type not in ACCESS_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access_type")

    grant = await create_grant(
        db,
        data.user_id,
        plan.id,
        admin_user.id,
        expires_at=data.expires_at,
        duration_months=data.duration_months,
        duration_years=data.duration_years,
        reason=data.reason,
        reason_custom=data.reason_custom,
        access_type=data.access_type,
        override_stripe=data.override_stripe,
        on_expiry=data.on_expiry,
        internal_notes=data.internal_notes,
    )
    await db.commit()
    await db.refresh(grant)
    return GrantResponse(
        id=str(grant.id),
        user_id=str(grant.user_id),
        plan_slug=plan.slug,
        granted_at=grant.granted_at.isoformat(),
        expires_at=grant.expires_at.isoformat() if grant.expires_at else None,
        reason=grant.reason,
        access_type=grant.access_type,
        override_stripe=grant.override_stripe,
        on_expiry=grant.on_expiry,
        revoked_at=grant.revoked_at.isoformat() if grant.revoked_at else None,
    )


@router.get("/admin/grants/{user_id}", response_model=list[GrantResponse])
async def admin_list_grants(
    user_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_revoked: bool = False,
):
    """Admin: list entitlement grants for a user."""
    await _require_admin(current_user, db)
    grants = await list_grants_for_user(db, user_id, include_revoked=include_revoked)
    result = []
    for g in grants:
        await db.refresh(g, ["plan"])
        result.append(GrantResponse(
            id=str(g.id),
            user_id=str(g.user_id),
            plan_slug=g.plan.slug,
            granted_at=g.granted_at.isoformat(),
            expires_at=g.expires_at.isoformat() if g.expires_at else None,
            reason=g.reason,
            access_type=g.access_type,
            override_stripe=g.override_stripe,
            on_expiry=g.on_expiry,
            revoked_at=g.revoked_at.isoformat() if g.revoked_at else None,
        ))
    return result


@router.post("/admin/grants/{grant_id}/revoke")
async def admin_revoke_grant(
    grant_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    reason: str | None = None,
):
    """Admin: revoke an entitlement grant."""
    await _require_admin(current_user, db)
    grant = await revoke_grant(db, grant_id, current_user.id, reason=reason)
    if not grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found or already revoked")
    await db.commit()
    return {"ok": True}


class GrantExtendRequest(BaseModel):
    new_expires_at: datetime


@router.post("/admin/grants/{grant_id}/extend")
async def admin_extend_grant(
    grant_id: uuid.UUID,
    data: GrantExtendRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: extend a grant's expiry date."""
    await _require_admin(current_user, db)
    grant = await extend_grant(db, grant_id, current_user.id, data.new_expires_at)
    if not grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found or revoked")
    await db.commit()
    return {"ok": True}


@router.post("/admin/grants/{grant_id}/convert-lifetime")
async def admin_convert_grant_to_lifetime(
    grant_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: convert a time-limited grant to lifetime."""
    await _require_admin(current_user, db)
    grant = await convert_grant_to_lifetime(db, grant_id, current_user.id)
    if not grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Grant not found or revoked")
    await db.commit()
    return {"ok": True}


# --- Admin promo codes ---

class PromoCodeCreateRequest(BaseModel):
    code: str
    plan_slug: str
    discount_type: str = "free"
    discount_value: int | None = None
    duration_months: int | None = None
    duration_years: int | None = None
    expires_at: datetime | None = None
    max_uses: int | None = None
    valid_from: datetime | None = None
    valid_until: datetime | None = None
    internal_note: str | None = None
    is_stripe_compatible: bool = False
    allowed_user_ids: list[uuid.UUID] | None = None


class PromoCodeResponse(BaseModel):
    id: str
    code: str
    plan_slug: str
    discount_type: str
    use_count: int
    max_uses: int | None
    revoked_at: str | None


@router.post("/admin/promo-codes", response_model=PromoCodeResponse)
async def admin_create_promo_code(
    data: PromoCodeCreateRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: create a promo code."""
    await _require_admin(current_user, db)
    r = await db.execute(select(Plan).where(Plan.slug == data.plan_slug))
    plan = r.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found")
    pc = await create_promo_code(
        db,
        data.code,
        plan.id,
        current_user.id,
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        duration_months=data.duration_months,
        duration_years=data.duration_years,
        expires_at=data.expires_at,
        max_uses=data.max_uses,
        valid_from=data.valid_from,
        valid_until=data.valid_until,
        internal_note=data.internal_note,
        is_stripe_compatible=data.is_stripe_compatible,
        allowed_user_ids=data.allowed_user_ids,
    )
    await db.commit()
    await db.refresh(pc, ["plan"])
    return PromoCodeResponse(
        id=str(pc.id),
        code=pc.code,
        plan_slug=pc.plan.slug,
        discount_type=pc.discount_type,
        use_count=pc.use_count,
        max_uses=pc.max_uses,
        revoked_at=pc.revoked_at.isoformat() if pc.revoked_at else None,
    )


@router.get("/admin/promo-codes", response_model=list[PromoCodeResponse])
async def admin_list_promo_codes(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_revoked: bool = False,
):
    """Admin: list promo codes."""
    await _require_admin(current_user, db)
    codes = await list_promo_codes(db, include_revoked=include_revoked)
    result = []
    for pc in codes:
        await db.refresh(pc, ["plan"])
        result.append(PromoCodeResponse(
            id=str(pc.id),
            code=pc.code,
            plan_slug=pc.plan.slug,
            discount_type=pc.discount_type,
            use_count=pc.use_count,
            max_uses=pc.max_uses,
            revoked_at=pc.revoked_at.isoformat() if pc.revoked_at else None,
        ))
    return result


@router.post("/admin/promo-codes/{code_id}/revoke")
async def admin_revoke_promo_code(
    code_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: revoke a promo code."""
    await _require_admin(current_user, db)
    pc = await revoke_promo_code(db, code_id, current_user.id)
    if not pc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code not found or already revoked")
    await db.commit()
    return {"ok": True}


# --- Redeem promo code (user or admin) ---

class RedeemCodeRequest(BaseModel):
    code: str


@router.post("/redeem-code")
async def redeem_code(
    data: RedeemCodeRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Redeem a promo code for the current user."""
    pc, grant, err = await redeem_promo_code(
        db,
        data.code,
        current_user.id,
        create_grant=True,
        granted_by_id=current_user.id,
    )
    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    await db.commit()
    if pc:
        await db.refresh(pc, ["plan"])
    return {"ok": True, "plan_slug": pc.plan.slug if pc else None}


# --- Admin: apply code to another user ---

@router.post("/admin/redeem-code/{user_id}")
async def admin_redeem_code_for_user(
    user_id: uuid.UUID,
    data: RedeemCodeRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: redeem a promo code on behalf of a user."""
    await _require_admin(current_user, db)
    pc, grant, err = await redeem_promo_code(
        db,
        data.code,
        user_id,
        create_grant=True,
        granted_by_id=current_user.id,
    )
    if err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    await db.commit()
    if pc:
        await db.refresh(pc, ["plan"])
    return {"ok": True, "plan_slug": pc.plan.slug if pc else None}


# --- Entitlement audit log ---

class AuditLogEntryResponse(BaseModel):
    id: str
    user_id: str | None
    action: str
    entity_type: str
    entity_id: str | None
    details: dict | None
    performed_by_id: str
    created_at: str


@router.get("/admin/audit-log", response_model=list[AuditLogEntryResponse])
async def admin_entitlement_audit_log(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: uuid.UUID | None = None,
    action: str | None = None,
    limit: int = Query(100, le=500),
):
    """Admin: view entitlement audit log."""
    await _require_admin(current_user, db)
    q = select(EntitlementAuditLog).order_by(EntitlementAuditLog.created_at.desc()).limit(limit)
    if user_id:
        q = q.where(EntitlementAuditLog.user_id == user_id)
    if action:
        q = q.where(EntitlementAuditLog.action == action)
    r = await db.execute(q)
    entries = r.scalars().all()
    return [
        AuditLogEntryResponse(
            id=str(e.id),
            user_id=str(e.user_id) if e.user_id else None,
            action=e.action,
            entity_type=e.entity_type,
            entity_id=str(e.entity_id) if e.entity_id else None,
            details=e.details,
            performed_by_id=str(e.performed_by_id),
            created_at=e.created_at.isoformat(),
        )
        for e in entries
    ]


# --- Billing health (admin) ---


@router.get("/admin/health")
async def admin_billing_health(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Admin: billing/Stripe health check. Verifies config, webhook secret, plan data."""
    await _require_admin(current_user, db)
    from authora.services.stripe_service import _stripe_available, is_stripe_live_mode, _get_webhook_secret

    s = get_settings()
    stripe_configured = _stripe_available()
    webhook_secret_set = bool(_get_webhook_secret()) if stripe_configured else False
    live_mode = is_stripe_live_mode() if stripe_configured else None

    # Plan count
    r = await db.execute(select(Plan))
    plans = r.scalars().all()
    plans_with_stripe = sum(1 for p in plans if getattr(p, "stripe_price_id_monthly", None) or getattr(p, "stripe_price_id_yearly", None) or getattr(p, "stripe_price_id_lifetime", None))

    return {
        "stripe_configured": stripe_configured,
        "webhook_secret_set": webhook_secret_set,
        "live_mode": live_mode,
        "feature_billing": getattr(s, "feature_billing", False),
        "plans_count": len(plans),
        "plans_with_stripe_prices": plans_with_stripe,
        "status": "ok" if (not stripe_configured or webhook_secret_set) else "degraded",
    }


# --- Stripe checkout and webhooks ---

class CheckoutCreateRequest(BaseModel):
    plan_slug: str
    billing_interval: str  # monthly | yearly | lifetime
    success_url: str | None = None
    cancel_url: str | None = None
    promo_code: str | None = None


class TemplatePackCheckoutRequest(BaseModel):
    pack_slug: str
    success_url: str | None = None
    cancel_url: str | None = None


@router.post("/checkout/template-pack")
async def create_template_pack_checkout(
    data: TemplatePackCheckoutRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create Stripe Checkout session for a template pack (one-time purchase)."""
    from authora.services.stripe_service import create_template_pack_checkout_session

    r = await db.execute(select(TemplatePack).where(TemplatePack.slug == data.pack_slug, TemplatePack.is_active.is_(True)))
    pack = r.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template pack not found")

    r2 = await db.execute(
        select(TemplatePackPurchase).where(
            TemplatePackPurchase.user_id == current_user.id,
            TemplatePackPurchase.pack_slug == data.pack_slug,
        )
    )
    if r2.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already own this pack")

    if not pack.stripe_price_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Template pack purchase not configured. Contact support.",
        )

    result = await create_template_pack_checkout_session(
        db,
        current_user.id,
        data.pack_slug,
        success_url=data.success_url,
        cancel_url=data.cancel_url,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe checkout not configured. Set STRIPE_SECRET_KEY to enable.",
        )
    return result


@router.post("/checkout/create")
async def create_checkout(
    data: CheckoutCreateRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create Stripe Checkout session. Returns url and session_id when Stripe configured."""
    from authora.services.stripe_service import create_checkout_session

    result = await create_checkout_session(
        db,
        current_user.id,
        data.plan_slug,
        data.billing_interval,
        success_url=data.success_url,
        cancel_url=data.cancel_url,
        promo_code=data.promo_code,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe checkout not configured. Set STRIPE_SECRET_KEY to enable.",
        )
    return result


class TemplateCheckoutRequest(BaseModel):
    template_id: uuid.UUID
    success_url: str | None = None
    cancel_url: str | None = None


@router.post("/checkout/template")
async def create_template_checkout(
    data: TemplateCheckoutRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create Stripe Checkout session for a single creator template (one-time purchase)."""
    from authora.services.stripe_service import create_template_checkout_session

    r = await db.execute(
        select(ProjectTemplate).where(
            ProjectTemplate.id == data.template_id,
            ProjectTemplate.is_disabled.is_(False),
            ProjectTemplate.is_paid.is_(True),
        )
    )
    template = r.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    if not template.price_cents or template.price_cents <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Template is not for sale")

    r2 = await db.execute(
        select(TemplatePurchase).where(
            TemplatePurchase.user_id == current_user.id,
            TemplatePurchase.template_id == data.template_id,
        )
    )
    if r2.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You already own this template")

    result = await create_template_checkout_session(
        db,
        current_user.id,
        data.template_id,
        success_url=data.success_url,
        cancel_url=data.cancel_url,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Stripe checkout not configured. Set STRIPE_SECRET_KEY to enable.",
        )
    return result


class CustomerPortalRequest(BaseModel):
    return_url: str | None = None


@router.post("/customer-portal")
async def create_customer_portal(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    data: CustomerPortalRequest | None = None,
):
    """Create Stripe Customer Portal session for managing subscription."""
    from authora.services.stripe_service import create_customer_portal_session

    result = await create_customer_portal_session(
        db,
        current_user.id,
        return_url=data.return_url if data else None,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Stripe customer found or Stripe not configured.",
        )
    return result


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Stripe webhook. Requires raw body for signature verification. Handle subscription and invoice events."""
    from authora.services.stripe_service import handle_webhook

    body = await request.body()
    sig = request.headers.get("stripe-signature", "")
    result = await handle_webhook(db, body, sig)
    if result and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result or {"handled": True}
