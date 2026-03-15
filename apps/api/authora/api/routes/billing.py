"""Billing API - plan status, usage, admin override. Stripe hooks placeholder."""

import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import Plan, User
from authora.services.billing_service import (
    _period_str,
    check_ai_action_limit,
    check_book_limit,
    check_export_limit,
    check_project_limit,
    get_usage,
    get_user_plan,
    has_feature,
    record_usage,
)

router = APIRouter(prefix="/billing", tags=["billing"])


class PlanResponse(BaseModel):
    id: str
    slug: str
    name: str
    limits: dict
    features: list[str]


class UsageResponse(BaseModel):
    ai_actions: int
    ai_actions_limit: int
    exports: int
    exports_limit: int
    projects: int
    projects_limit: int
    books: int
    books_limit: int


class BillingStatusResponse(BaseModel):
    plan: PlanResponse
    usage: UsageResponse
    billing_exempt: bool
    can_upgrade: bool


async def _get_usage_summary(db: AsyncSession, user_id: uuid.UUID, plan: Plan) -> dict:
    """Build usage summary for user."""
    period = _period_str()
    ai_used = await get_usage(db, user_id, period, "ai_actions")
    ai_limit = plan.limits.get("ai_actions_per_month", -1)
    exp_used = await get_usage(db, user_id, period, "exports")
    exp_limit = plan.limits.get("exports_per_month", -1)
    _, proj_count, proj_limit = await check_project_limit(db, user_id)
    _, book_count, book_limit = await check_book_limit(db, user_id)
    return {
        "ai_actions": ai_used,
        "ai_actions_limit": ai_limit if ai_limit >= 0 else 999999,
        "exports": exp_used,
        "exports_limit": exp_limit if exp_limit >= 0 else 999999,
        "projects": proj_count,
        "projects_limit": proj_limit if proj_limit >= 0 else 999999,
        "books": book_count,
        "books_limit": book_limit if book_limit >= 0 else 999999,
    }


@router.get("/status", response_model=BillingStatusResponse)
async def get_billing_status(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current user's plan, usage, and limits."""
    plan = await get_user_plan(db, current_user.id)
    usage = await _get_usage_summary(db, current_user.id, plan)
    r = await db.execute(select(User).where(User.id == current_user.id))
    user = r.scalar_one_or_none()
    billing_exempt = getattr(user, "billing_exempt", False) or bool(getattr(user, "plan_override_id", None))
    return BillingStatusResponse(
        plan=PlanResponse(
            id=str(plan.id),
            slug=plan.slug,
            name=plan.name,
            limits=plan.limits or {},
            features=plan.features or [],
        ),
        usage=UsageResponse(**usage),
        billing_exempt=billing_exempt,
        can_upgrade=plan.slug == "free",
    )


@router.get("/plans", response_model=list[PlanResponse])
async def list_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List available plans (public)."""
    from sqlalchemy import asc

    r = await db.execute(select(Plan).order_by(asc(Plan.sort_order)))
    plans = r.scalars().all()
    return [
        PlanResponse(
            id=str(p.id),
            slug=p.slug,
            name=p.name,
            limits=p.limits or {},
            features=p.features or [],
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


# --- Stripe webhook placeholder (for future integration) ---

@router.post("/webhooks/stripe")
async def stripe_webhook():
    """Stripe webhook endpoint. Placeholder for future integration."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Stripe webhook not configured. Set STRIPE_WEBHOOK_SECRET to enable.",
    )


@router.post("/checkout/create")
async def create_checkout_session():
    """Create Stripe checkout session. Placeholder for future integration."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Stripe checkout not configured. Set STRIPE_SECRET_KEY to enable.",
    )
