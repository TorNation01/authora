"""Reminder and notification service for accountability.

Processes scheduled reminders, sends nudges, and creates recovery plans.
Can be invoked by a cron job or scheduler.
"""

from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.infrastructure.notifications.impl import DefaultNotificationService
from authora.models import (
    AccountabilitySettings,
    Book,
    Chapter,
    Project,
    RecoveryPlan,
    StreakLog,
    UserStats,
    WritingPlan,
)
from authora.services.accountability_engine import (
    get_message,
    get_style,
    suggest_recovery_plan,
)


async def process_daily_reminders(db: AsyncSession) -> int:
    """Process daily reminders for users with reminder_enabled and matching reminder_times.
    Returns count of notifications sent.
    """
    now = datetime.now(timezone.utc)
    current_hour = now.hour
    current_time_str = f"{current_hour:02d}:00"

    result = await db.execute(
        select(AccountabilitySettings).where(
            AccountabilitySettings.reminder_enabled == True,
            AccountabilitySettings.plan_paused == False,
            AccountabilitySettings.daily_word_goal.isnot(None),
        )
    )
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        times = settings.reminder_times or ["09:00"]
        if current_time_str not in times:
            continue

        style = get_style(settings)
        target = settings.daily_word_goal or 500

        result = await db.execute(
            select(StreakLog).where(
                StreakLog.user_id == settings.user_id,
                StreakLog.date == date.today(),
            )
        )
        log = result.scalar_one_or_none()
        words_today = log.words_written if log else 0

        if words_today >= target:
            continue

        msg = get_message(style, "daily_reminder", target=target)
        await svc.send_in_app(
            str(settings.user_id),
            "daily_reminder",
            "Your writing goal today",
            msg,
        )
        sent += 1

    return sent


async def process_weekly_reminders(db: AsyncSession) -> int:
    """Process weekly reminders (e.g., on Monday)."""
    today = date.today()
    if today.weekday() != 0:
        return 0

    week_start = today - timedelta(days=today.weekday())
    result = await db.execute(
        select(AccountabilitySettings).where(
            AccountabilitySettings.reminder_enabled == True,
            AccountabilitySettings.plan_paused == False,
            AccountabilitySettings.weekly_word_goal.isnot(None),
        )
    )
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        result = await db.execute(
            select(StreakLog).where(
                StreakLog.user_id == settings.user_id,
                StreakLog.date >= week_start,
            )
        )
        logs = result.scalars().all()
        words_week = sum(log.words_written for log in logs)
        target = settings.weekly_word_goal or 3500

        if words_week >= target:
            continue

        style = get_style(settings)
        msg = get_message(style, "weekly_reminder", current=words_week, target=target)
        await svc.send_in_app(
            str(settings.user_id),
            "weekly_reminder",
            "Weekly writing check-in",
            msg,
        )
        sent += 1

    return sent


async def process_stuck_detection(db: AsyncSession) -> int:
    """Detect stuck users and send supportive nudge."""
    result = await db.execute(select(AccountabilitySettings).where(AccountabilitySettings.plan_paused == False))
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        result = await db.execute(select(UserStats).where(UserStats.user_id == settings.user_id))
        stats = result.scalar_one_or_none()
        if not stats or not stats.last_writing_date:
            continue

        days_since = (date.today() - stats.last_writing_date).days
        if days_since < 5:
            continue

        style = get_style(settings)
        msg = get_message(style, "stuck")
        await svc.send_in_app(
            str(settings.user_id),
            "stuck_nudge",
            "We miss you",
            msg,
        )
        sent += 1

    return sent


async def process_overdue_and_recovery(db: AsyncSession) -> int:
    """Check for overdue plans and create recovery plans."""
    result = await db.execute(
        select(WritingPlan).where(
            WritingPlan.status == "active",
            WritingPlan.target_finish_date.isnot(None),
            WritingPlan.target_finish_date < date.today(),
        )
    )
    overdue_plans = result.scalars().all()
    created = 0

    for plan in overdue_plans:
        current_words = 0
        if plan.book_id:
            result = await db.execute(select(Chapter).where(Chapter.book_id == plan.book_id))
            chapters = result.scalars().all()
            current_words = sum(c.word_count for c in chapters)

        days_overdue = (date.today() - plan.target_finish_date).days
        days_remaining = -days_overdue
        recovery = suggest_recovery_plan(
            current_words,
            plan.total_target_words,
            max(1, days_overdue + 7),
            "balanced",
        )

        if not recovery.get("needed"):
            continue

        existing = await db.execute(
            select(RecoveryPlan).where(
                RecoveryPlan.user_id == plan.user_id,
                RecoveryPlan.book_id == plan.book_id,
                RecoveryPlan.acknowledged_at.is_(None),
            )
        )
        if existing.scalar_one_or_none():
            continue

        rp = RecoveryPlan(
            user_id=plan.user_id,
            book_id=plan.book_id,
            plan_type="catch_up",
            suggested_daily_words=recovery.get("suggested_daily_words"),
            suggested_schedule=recovery.get("schedule"),
            message=recovery.get("message"),
        )
        db.add(rp)
        created += 1

    return created
