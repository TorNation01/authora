"""Accountability engine API routes."""

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
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
    Project,
    RecoveryPlan,
    StreakLog,
    UserStats,
    WritingPlan,
)
from authora.services.reminder_service import (
    process_daily_reminders,
    process_overdue_and_recovery,
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

router = APIRouter(prefix="/accountability", tags=["accountability"])


# --- Schemas ---

class AccountabilitySettingsUpdate(BaseModel):
    daily_word_goal: int | None = None
    weekly_word_goal: int | None = None
    accountability_style: str | None = None
    reminder_enabled: bool | None = None
    reminder_times: list[str] | None = None
    plan_paused: bool | None = None


class AccountabilitySettingsResponse(BaseModel):
    daily_word_goal: int | None
    weekly_word_goal: int | None
    accountability_style: str
    reminder_enabled: bool
    reminder_times: list[str] | None
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


# --- Scheduler / Cron endpoint (internal) ---

@router.post("/cron/reminders")
async def run_reminder_jobs(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Run reminder jobs. Call from cron (e.g. every hour for daily, Mon for weekly)."""

    daily = await process_daily_reminders(db)
    weekly = await process_weekly_reminders(db)
    stuck = await process_stuck_detection(db)
    recovery = await process_overdue_and_recovery(db)
    await db.commit()

    return {
        "daily_reminders": daily,
        "weekly_reminders": weekly,
        "stuck_nudges": stuck,
        "recovery_plans_created": recovery,
    }
