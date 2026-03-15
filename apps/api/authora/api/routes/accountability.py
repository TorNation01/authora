"""Accountability engine API routes."""

import logging
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import (
    AccountabilitySettings,
    Book,
    Chapter,
    ChapterTarget,
    Goal,
    Milestone,
    Notification,
    NotificationDeliveryLog,
    Project,
    RecoveryPlan,
    StreakLog,
    User,
    UserStats,
    WritingPlan,
)
from authora.services.reminder_service import (
    process_chapter_target_reminders,
    process_daily_reminders,
    process_failed_email_retries,
    process_finish_date_risk_alerts,
    process_milestone_reminders,
    process_overdue_and_recovery,
    process_overdue_nudges,
    process_resume_reminders,
    process_section_reminders,
    process_streak_reminders,
    process_stuck_detection,
    process_weekly_reminders,
)
from authora.services.accountability_engine import (
    compute_consistency_score,
    detect_stuck,
    forecast_completion,
    get_message,
    get_or_create_settings,
    get_style,
    suggest_recovery_plan,
)
from authora.services.gamification import get_or_create_user_stats

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/accountability", tags=["accountability"])


# --- Schemas ---

class AccountabilitySettingsUpdate(BaseModel):
    daily_word_goal: int | None = None
    weekly_word_goal: int | None = None
    accountability_style: str | None = None
    reminder_enabled: bool | None = None
    reminder_times: list[str] | None = None
    timezone: str | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    email_reminders_enabled: bool | None = None
    reminder_cadence: str | None = None
    reminder_types: list[str] | None = None
    plan_paused: bool | None = None


class AccountabilitySettingsResponse(BaseModel):
    daily_word_goal: int | None
    weekly_word_goal: int | None
    accountability_style: str
    reminder_enabled: bool
    reminder_times: list[str] | None
    timezone: str | None
    quiet_hours_start: str | None
    quiet_hours_end: str | None
    email_reminders_enabled: bool
    reminder_cadence: str
    reminder_types: list[str] | None
    plan_paused: bool
    paused_at: datetime | None

    model_config = {"from_attributes": True}


class WritingPlanCreate(BaseModel):
    book_id: uuid.UUID | None = None
    name: str
    target_finish_date: str | None = None
    total_target_words: int


class ChapterTargetCreate(BaseModel):
    chapter_id: uuid.UUID
    target_words: int
    due_date: str | None = None


class MilestoneCreate(BaseModel):
    book_id: uuid.UUID | None = None
    title: str
    target_words: int
    target_date: str | None = None


# --- Settings ---

@router.get("/settings", response_model=AccountabilitySettingsResponse)
async def get_settings(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get accountability settings."""
    settings = await get_or_create_settings(db, current_user.id)
    await db.refresh(settings)
    return AccountabilitySettingsResponse.model_validate(settings)


@router.patch("/settings", response_model=AccountabilitySettingsResponse)
async def update_settings(
    data: AccountabilitySettingsUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update accountability settings."""
    settings = await get_or_create_settings(db, current_user.id)
    if data.daily_word_goal is not None:
        settings.daily_word_goal = data.daily_word_goal
    if data.weekly_word_goal is not None:
        settings.weekly_word_goal = data.weekly_word_goal
    if data.accountability_style is not None:
        if data.accountability_style not in ("gentle", "balanced", "firm", "coach", "structured"):
            raise HTTPException(status_code=400, detail="Invalid accountability style")
        settings.accountability_style = data.accountability_style
    if data.reminder_enabled is not None:
        settings.reminder_enabled = data.reminder_enabled
    if data.reminder_times is not None:
        settings.reminder_times = data.reminder_times
    if data.timezone is not None:
        settings.timezone = data.timezone
    if data.quiet_hours_start is not None:
        settings.quiet_hours_start = data.quiet_hours_start
    if data.quiet_hours_end is not None:
        settings.quiet_hours_end = data.quiet_hours_end
    if data.email_reminders_enabled is not None:
        settings.email_reminders_enabled = data.email_reminders_enabled
    if data.reminder_cadence is not None:
        if data.reminder_cadence not in ("daily", "weekly", "both"):
            raise HTTPException(status_code=400, detail="Invalid reminder cadence")
        settings.reminder_cadence = data.reminder_cadence
    if data.reminder_types is not None:
        settings.reminder_types = data.reminder_types
    if data.plan_paused is not None:
        settings.plan_paused = data.plan_paused
        settings.paused_at = datetime.now(timezone.utc) if data.plan_paused else None
    await db.flush()
    await db.refresh(settings)
    return AccountabilitySettingsResponse.model_validate(settings)


# --- Dashboard / Overview ---

@router.get("/overview")
async def get_overview(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get accountability overview: goals, progress, consistency, next action."""
    settings = await get_or_create_settings(db, current_user.id)
    stats = await get_or_create_user_stats(db, current_user.id)

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    result = await db.execute(
        select(StreakLog).where(
            StreakLog.user_id == current_user.id,
            StreakLog.date >= week_start - timedelta(days=7 * 4),
        )
    )
    logs = result.scalars().all()

    days_written_last_4_weeks = len({log.date for log in logs if log.words_written > 0})
    days_elapsed = 28
    consistency_score = compute_consistency_score(days_written_last_4_weeks, days_elapsed)

    words_today = sum(log.words_written for log in logs if log.date == today)
    words_this_week = sum(log.words_written for log in logs if log.date >= week_start)

    daily_goal = settings.daily_word_goal
    weekly_goal = settings.weekly_word_goal

    stuck = detect_stuck(stats.last_writing_date)

    result = await db.execute(
        select(Chapter).join(Chapter.book).join(Book.project).where(
            Project.user_id == current_user.id,
        ).order_by(Chapter.updated_at.desc()).limit(1)
    )
    last_chapter = result.scalar_one_or_none()

    from authora.services.accountability_engine import get_next_best_action
    next_action = get_next_best_action(settings, daily_goal, words_today, last_chapter)

    return {
        "daily_goal": daily_goal,
        "weekly_goal": weekly_goal,
        "words_today": words_today,
        "words_this_week": words_this_week,
        "consistency_score": consistency_score,
        "current_streak": stats.current_streak,
        "stuck": stuck,
        "plan_paused": settings.plan_paused,
        "next_action": next_action,
    }


# --- Writing Plans ---

@router.get("/plans")
async def list_plans(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List writing plans."""
    result = await db.execute(
        select(WritingPlan).where(WritingPlan.user_id == current_user.id).order_by(WritingPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "book_id": str(p.book_id) if p.book_id else None,
            "name": p.name,
            "target_finish_date": p.target_finish_date.isoformat() if p.target_finish_date else None,
            "total_target_words": p.total_target_words,
            "status": p.status,
        }
        for p in plans
    ]


@router.post("/plans")
async def create_plan(
    data: WritingPlanCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create writing plan."""
    finish = None
    if data.target_finish_date:
        try:
            finish = date.fromisoformat(data.target_finish_date)
        except ValueError:
            pass

    plan = WritingPlan(
        user_id=current_user.id,
        book_id=data.book_id,
        name=data.name,
        target_finish_date=finish,
        total_target_words=data.total_target_words,
    )
    db.add(plan)
    await db.flush()
    await db.refresh(plan)
    return {"id": str(plan.id), "name": plan.name}


# --- Recovery Plans ---

@router.get("/recovery")
async def list_recovery_plans(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List unacknowledged recovery plans."""
    result = await db.execute(
        select(RecoveryPlan).where(
            RecoveryPlan.user_id == current_user.id,
            RecoveryPlan.acknowledged_at.is_(None),
        ).order_by(RecoveryPlan.created_at.desc())
    )
    plans = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "plan_type": p.plan_type,
            "suggested_daily_words": p.suggested_daily_words,
            "message": p.message,
            "suggested_schedule": p.suggested_schedule,
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ]


@router.post("/recovery/{plan_id}/acknowledge")
async def acknowledge_recovery(
    plan_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Acknowledge a recovery plan."""
    result = await db.execute(
        select(RecoveryPlan).where(
            RecoveryPlan.id == plan_id,
            RecoveryPlan.user_id == current_user.id,
        )
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Recovery plan not found")
    plan.acknowledged_at = datetime.now(timezone.utc)
    await db.flush()
    return {"ok": True}


# --- Forecast ---

@router.get("/forecast")
async def get_forecast(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: uuid.UUID | None = None,
):
    """Get progress forecast for a book or overall."""
    from authora.services.accountability_engine import get_book_word_count, get_words_this_week

    if book_id:
        result = await db.execute(select(Book).join(Book.project).where(
            Book.id == book_id,
            Project.user_id == current_user.id,
        ))
        book = result.scalar_one_or_none()
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        current_words = await get_book_word_count(db, book_id)
        result = await db.execute(
            select(WritingPlan).where(
                WritingPlan.book_id == book_id,
                WritingPlan.user_id == current_user.id,
                WritingPlan.status == "active",
            ).order_by(WritingPlan.created_at.desc()).limit(1)
        )
        plan = result.scalar_one_or_none()
        if plan and plan.target_finish_date:
            days_remaining = (plan.target_finish_date - date.today()).days
            target_words = plan.total_target_words
            words_this_week = await get_words_this_week(db, current_user.id)
            avg_daily = words_this_week / 7 if words_this_week else 0
            forecast = forecast_completion(current_words, target_words, days_remaining, avg_daily)
            return {
                "book_id": str(book_id),
                "current_words": current_words,
                "target_words": target_words,
                "days_remaining": days_remaining,
                **forecast,
            }
        return {"book_id": str(book_id), "current_words": current_words}

    stats = await get_or_create_user_stats(db, current_user.id)
    words_this_week = await get_words_this_week(db, current_user.id)
    avg_daily = words_this_week / 7 if words_this_week else 0
    return {"total_words": stats.total_words, "avg_daily_this_week": round(avg_daily, 0)}


# --- Messages ---

@router.get("/message")
async def get_motivational_message(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    key: str = "motivational",
):
    """Get a supportive message (for testing or display)."""
    settings = await get_or_create_settings(db, current_user.id)
    style = get_style(settings)
    msg = get_message(style, key)
    return {"style": style, "message": msg}


# --- Notifications ---

@router.get("/notifications")
async def list_notifications(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
    unread_only: bool = False,
):
    """List in-app notifications for the current user."""
    q = select(Notification).where(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(limit)
    if unread_only:
        q = q.where(Notification.read_at.is_(None))
    result = await db.execute(q)
    notifications = result.scalars().all()
    return [
        {
            "id": str(n.id),
            "type": n.type,
            "title": n.title,
            "body": n.body,
            "read_at": n.read_at.isoformat() if n.read_at else None,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Mark a notification as read."""
    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
    )
    n = result.scalar_one_or_none()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.read_at = datetime.now(timezone.utc)
    await db.flush()
    return {"ok": True}


@router.post("/notifications/test")
async def send_test_notification(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send a test notification (in-app and optionally email) to verify the flow."""
    from authora.infrastructure.notifications.factory import get_notification_service

    settings = await get_or_create_settings(db, current_user.id)
    user_result = await db.execute(select(User).where(User.id == current_user.id))
    user = user_result.scalar_one_or_none()
    email = user.email if user else ""

    svc = get_notification_service(db)
    msg = "This is a test notification. Your reminder settings are working."
    results = await svc.send_reminder(
        str(current_user.id),
        email,
        "test_notification",
        "Test notification",
        msg,
        in_app=True,
        email=settings.email_reminders_enabled,
    )
    await db.commit()
    return {
        "in_app_sent": results["in_app"],
        "email_sent": results["email"],
        "message": "Test notification sent.",
    }


@router.get("/delivery-logs")
async def list_delivery_logs(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 50,
):
    """List notification delivery logs for the current user."""
    result = await db.execute(
        select(NotificationDeliveryLog)
        .where(NotificationDeliveryLog.user_id == current_user.id)
        .order_by(NotificationDeliveryLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()
    return [
        {
            "id": str(l.id),
            "notification_type": l.notification_type,
            "channel": l.channel,
            "status": l.status,
            "error_message": l.error_message,
            "retry_count": l.retry_count,
            "created_at": l.created_at.isoformat(),
            "sent_at": l.sent_at.isoformat() if l.sent_at else None,
        }
        for l in logs
    ]


# --- Scheduler / Cron endpoint (internal) ---

def _require_cron_secret(request: Request) -> None:
    """Require X-Cron-Secret header when CRON_SECRET is set."""
    from authora.config import get_settings
    secret = get_settings().cron_secret
    if not secret:
        return  # No secret configured: allow (backward compat; set CRON_SECRET in prod)
    provided = request.headers.get("x-cron-secret")
    if provided != secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing cron secret")


@router.post("/cron/reminders")
async def run_reminder_jobs(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Run reminder jobs. Call from cron (e.g. every hour for daily, Mon for weekly).
    When CRON_SECRET is set, requires X-Cron-Secret header."""
    _require_cron_secret(request)

    daily = await process_daily_reminders(db)
    weekly = await process_weekly_reminders(db)
    milestone = await process_milestone_reminders(db)
    streak = await process_streak_reminders(db)
    overdue_nudges = await process_overdue_nudges(db)
    finish_risk = await process_finish_date_risk_alerts(db)
    resume = await process_resume_reminders(db)
    section = await process_section_reminders(db)
    chapter_target = await process_chapter_target_reminders(db)
    stuck = await process_stuck_detection(db)
    recovery = await process_overdue_and_recovery(db)
    retries = await process_failed_email_retries(db)
    await db.commit()

    result = {
        "daily_reminders": daily,
        "weekly_reminders": weekly,
        "milestone_reminders": milestone,
        "streak_reminders": streak,
        "overdue_nudges": overdue_nudges,
        "finish_date_risk_alerts": finish_risk,
        "resume_reminders": resume,
        "section_reminders": section,
        "chapter_target_reminders": chapter_target,
        "stuck_nudges": stuck,
        "recovery_plans_created": recovery,
        "email_retries": retries,
    }
    logger.info(
        "reminder_cron_completed",
        extra={
            "daily": result["daily_reminders"],
            "weekly": result["weekly_reminders"],
            "section": result["section_reminders"],
            "resume": result["resume_reminders"],
            "recovery_plans": result["recovery_plans_created"],
            "email_retries": result["email_retries"],
        },
    )
    return result
