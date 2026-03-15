"""Reminder and notification service for accountability.

Processes scheduled reminders, sends nudges, and creates recovery plans.
Timezone-aware, respects quiet hours, supports in-app and email.
Can be invoked by a cron job or scheduler.
"""

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.infrastructure.notifications.impl import DefaultNotificationService
from authora.models import (
    AccountabilitySettings,
    Book,
    Chapter,
    ChapterTarget,
    Milestone,
    Project,
    RecoveryPlan,
    StreakLog,
    User,
    UserStats,
    WritingPlan,
)
from authora.services.accountability_engine import (
    forecast_completion,
    get_message,
    get_style,
    suggest_recovery_plan,
)

REMINDER_TYPES = [
    "daily_reminder",
    "weekly_reminder",
    "milestone_reminder",
    "streak_reminder",
    "overdue_nudge",
    "finish_date_risk",
    "resume_reminder",
    "chapter_target_reminder",
    "stuck_nudge",
]


def _is_reminder_type_enabled(settings: AccountabilitySettings, reminder_type: str) -> bool:
    """Check if reminder type is enabled. None = all enabled."""
    if not settings.reminder_types:
        return True
    return reminder_type in settings.reminder_types


def _user_now(settings: AccountabilitySettings) -> datetime:
    """Current time in user's timezone."""
    tz_name = settings.timezone or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    return datetime.now(tz)


def _in_quiet_hours(settings: AccountabilitySettings, dt: datetime | None = None) -> bool:
    """Check if given time (or now) falls in user's quiet hours."""
    if not settings.quiet_hours_start or not settings.quiet_hours_end:
        return False
    tz_name = settings.timezone or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    now = dt or datetime.now(tz)
    try:
        start_h, start_m = map(int, settings.quiet_hours_start.split(":"))
        end_h, end_m = map(int, settings.quiet_hours_end.split(":"))
        start_min = start_h * 60 + start_m
        end_min = end_h * 60 + end_m
        now_min = now.hour * 60 + now.minute
        if start_min <= end_min:
            return start_min <= now_min < end_min
        return now_min >= start_min or now_min < end_min
    except Exception:
        return False


def _utc_hour_matches_user_times(settings: AccountabilitySettings, utc_hour: int) -> bool:
    """Check if UTC hour corresponds to any of user's reminder times in their timezone."""
    times = settings.reminder_times or ["09:00"]
    tz_name = settings.timezone or "UTC"
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = timezone.utc
    utc_now = datetime.now(timezone.utc).replace(hour=utc_hour, minute=0, second=0, microsecond=0)
    user_now = utc_now.astimezone(tz)
    user_time_str = f"{user_now.hour:02d}:00"
    return user_time_str in times


async def process_daily_reminders(db: AsyncSession) -> int:
    """Process daily reminders for users with reminder_enabled and matching reminder_times.
    Timezone-aware. Respects quiet hours. Returns count of notifications sent.
    """
    now_utc = datetime.now(timezone.utc)
    current_hour = now_utc.hour

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
        if not _is_reminder_type_enabled(settings, "daily_reminder"):
            continue
        if not _utc_hour_matches_user_times(settings, current_hour):
            continue
        if _in_quiet_hours(settings):
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
        user_result = await db.execute(select(User).where(User.id == settings.user_id))
        user = user_result.scalar_one_or_none()
        email = user.email if user else ""
        results = await svc.send_reminder(
            str(settings.user_id),
            email,
            "daily_reminder",
            "Your writing goal today",
            msg,
            in_app=True,
            email=settings.email_reminders_enabled,
        )
        if results["in_app"] or results["email"]:
            sent += 1

    return sent


async def process_weekly_reminders(db: AsyncSession) -> int:
    """Process weekly reminders (e.g., on Monday). Timezone-aware."""
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
        if not _is_reminder_type_enabled(settings, "weekly_reminder"):
            continue
        if _in_quiet_hours(settings):
            continue

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
        user_result = await db.execute(select(User).where(User.id == settings.user_id))
        user = user_result.scalar_one_or_none()
        email = user.email if user else ""
        results = await svc.send_reminder(
            str(settings.user_id),
            email,
            "weekly_reminder",
            "Weekly writing check-in",
            msg,
            in_app=True,
            email=settings.email_reminders_enabled,
        )
        if results["in_app"] or results["email"]:
            sent += 1

    return sent


async def process_milestone_reminders(db: AsyncSession) -> int:
    """Send reminders when user is close to a milestone."""
    result = await db.execute(
        select(AccountabilitySettings).where(
            AccountabilitySettings.reminder_enabled == True,
            AccountabilitySettings.plan_paused == False,
        )
    )
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        if not _is_reminder_type_enabled(settings, "milestone_reminder"):
            continue
        if _in_quiet_hours(settings):
            continue

        result = await db.execute(
            select(Milestone)
            .join(Book, Milestone.book_id == Book.id)
            .join(Project, Book.project_id == Project.id)
            .where(
                Project.user_id == settings.user_id,
                Milestone.book_id.isnot(None),
                Milestone.completed_at.is_(None),
            )
        )
        milestones = result.scalars().all()
        words_week = 0
        for m in milestones:
            if m.book_id:
                ch_result = await db.execute(select(Chapter).where(Chapter.book_id == m.book_id))
                chapters = ch_result.scalars().all()
                current = sum(c.word_count for c in chapters)
            else:
                current = 0
            remaining = m.target_words - current
            if 0 < remaining <= 500:
                style = get_style(settings)
                msg = get_message(style, "milestone_reminder", words=remaining)
                user_result = await db.execute(select(User).where(User.id == settings.user_id))
                user = user_result.scalar_one_or_none()
                email = user.email if user else ""
                results = await svc.send_reminder(
                    str(settings.user_id),
                    email,
                    "milestone_reminder",
                    "Milestone ahead",
                    msg,
                    in_app=True,
                    email=settings.email_reminders_enabled,
                )
                if results["in_app"] or results["email"]:
                    sent += 1
                break

    return sent


async def process_streak_reminders(db: AsyncSession) -> int:
    """Remind users to maintain their streak."""
    result = await db.execute(
        select(AccountabilitySettings).where(
            AccountabilitySettings.reminder_enabled == True,
            AccountabilitySettings.plan_paused == False,
        )
    )
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        if not _is_reminder_type_enabled(settings, "streak_reminder"):
            continue
        if _in_quiet_hours(settings):
            continue

        stats_result = await db.execute(select(UserStats).where(UserStats.user_id == settings.user_id))
        stats = stats_result.scalar_one_or_none()
        if not stats or stats.current_streak < 3:
            continue

        today_result = await db.execute(
            select(StreakLog).where(
                StreakLog.user_id == settings.user_id,
                StreakLog.date == date.today(),
            )
        )
        today_log = today_result.scalar_one_or_none()
        if today_log and today_log.words_written > 0:
            continue

        style = get_style(settings)
        msg = get_message(style, "streak_reminder", streak=stats.current_streak)
        user_result = await db.execute(select(User).where(User.id == settings.user_id))
        user = user_result.scalar_one_or_none()
        email = user.email if user else ""
        results = await svc.send_reminder(
            str(settings.user_id),
            email,
            "streak_reminder",
            "Keep your streak alive",
            msg,
            in_app=True,
            email=settings.email_reminders_enabled,
        )
        if results["in_app"] or results["email"]:
            sent += 1

    return sent


async def process_overdue_nudges(db: AsyncSession) -> int:
    """Send supportive nudges for overdue plans."""
    result = await db.execute(
        select(WritingPlan).where(
            WritingPlan.status == "active",
            WritingPlan.target_finish_date.isnot(None),
            WritingPlan.target_finish_date < date.today(),
        )
    )
    overdue_plans = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for plan in overdue_plans:
        settings_result = await db.execute(
            select(AccountabilitySettings).where(AccountabilitySettings.user_id == plan.user_id)
        )
        settings = settings_result.scalar_one_or_none()
        if not settings or not settings.reminder_enabled or settings.plan_paused:
            continue
        if not _is_reminder_type_enabled(settings, "overdue_nudge"):
            continue
        if _in_quiet_hours(settings):
            continue

        current_words = 0
        if plan.book_id:
            ch_result = await db.execute(select(Chapter).where(Chapter.book_id == plan.book_id))
            chapters = ch_result.scalars().all()
            current_words = sum(c.word_count for c in chapters)

        style = get_style(settings)
        msg = get_message(style, "overdue_nudge")
        user_result = await db.execute(select(User).where(User.id == plan.user_id))
        user = user_result.scalar_one_or_none()
        email = user.email if user else ""
        results = await svc.send_reminder(
            str(plan.user_id),
            email,
            "overdue_nudge",
            "Your manuscript is waiting",
            msg,
            in_app=True,
            email=settings.email_reminders_enabled,
        )
        if results["in_app"] or results["email"]:
            sent += 1

    return sent


async def process_finish_date_risk_alerts(db: AsyncSession) -> int:
    """Alert users when finish date is at risk."""
    today = date.today()
    result = await db.execute(
        select(WritingPlan).where(
            WritingPlan.status == "active",
            WritingPlan.target_finish_date.isnot(None),
            WritingPlan.target_finish_date >= today,
        )
    )
    plans = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for plan in plans:
        days_remaining = (plan.target_finish_date - today).days
        if days_remaining > 14:
            continue

        settings_result = await db.execute(
            select(AccountabilitySettings).where(AccountabilitySettings.user_id == plan.user_id)
        )
        settings = settings_result.scalar_one_or_none()
        if not settings or not settings.reminder_enabled or settings.plan_paused:
            continue
        if not _is_reminder_type_enabled(settings, "finish_date_risk"):
            continue
        if _in_quiet_hours(settings):
            continue

        current_words = 0
        if plan.book_id:
            ch_result = await db.execute(select(Chapter).where(Chapter.book_id == plan.book_id))
            chapters = ch_result.scalars().all()
            current_words = sum(c.word_count for c in chapters)

        from authora.services.accountability_engine import get_words_this_week

        words_this_week = await get_words_this_week(db, plan.user_id, plan.book_id)
        avg_daily = words_this_week / 7 if words_this_week else 0
        forecast = forecast_completion(
            current_words, plan.total_target_words, days_remaining, avg_daily
        )
        if forecast.get("on_track", True):
            continue

        style = get_style(settings)
        msg = get_message(style, "finish_date_risk")
        user_result = await db.execute(select(User).where(User.id == plan.user_id))
        user = user_result.scalar_one_or_none()
        email = user.email if user else ""
        results = await svc.send_reminder(
            str(plan.user_id),
            email,
            "finish_date_risk",
            "Finish date at risk",
            msg,
            in_app=True,
            email=settings.email_reminders_enabled,
        )
        if results["in_app"] or results["email"]:
            sent += 1

    return sent


async def process_resume_reminders(db: AsyncSession) -> int:
    """Remind users to resume writing."""
    result = await db.execute(
        select(AccountabilitySettings).where(
            AccountabilitySettings.reminder_enabled == True,
            AccountabilitySettings.plan_paused == False,
        )
    )
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        if not _is_reminder_type_enabled(settings, "resume_reminder"):
            continue
        if _in_quiet_hours(settings):
            continue

        result = await db.execute(
            select(Chapter)
            .join(Book, Chapter.book_id == Book.id)
            .join(Project, Book.project_id == Project.id)
            .where(Project.user_id == settings.user_id)
            .order_by(Chapter.updated_at.desc())
            .limit(1)
        )
        last_chapter = result.scalar_one_or_none()
        if not last_chapter:
            continue

        stats_result = await db.execute(select(UserStats).where(UserStats.user_id == settings.user_id))
        stats = stats_result.scalar_one_or_none()
        if stats and stats.last_writing_date:
            days_since = (date.today() - stats.last_writing_date).days
            if days_since < 2:
                continue

        style = get_style(settings)
        msg = get_message(style, "resume_reminder", chapter=last_chapter.title or "Untitled")
        user_result = await db.execute(select(User).where(User.id == settings.user_id))
        user = user_result.scalar_one_or_none()
        email = user.email if user else ""
        results = await svc.send_reminder(
            str(settings.user_id),
            email,
            "resume_reminder",
            "Resume your writing",
            msg,
            in_app=True,
            email=settings.email_reminders_enabled,
        )
        if results["in_app"] or results["email"]:
            sent += 1

    return sent


async def process_chapter_target_reminders(db: AsyncSession) -> int:
    """Remind users about chapter targets."""
    result = await db.execute(
        select(AccountabilitySettings).where(
            AccountabilitySettings.reminder_enabled == True,
            AccountabilitySettings.plan_paused == False,
        )
    )
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        if not _is_reminder_type_enabled(settings, "chapter_target_reminder"):
            continue
        if _in_quiet_hours(settings):
            continue

        result = await db.execute(
            select(ChapterTarget, Chapter)
            .join(Chapter, ChapterTarget.chapter_id == Chapter.id)
            .join(Book, Chapter.book_id == Book.id)
            .join(Project, Book.project_id == Project.id)
            .where(
                Project.user_id == settings.user_id,
                ChapterTarget.completed_at.is_(None),
            )
        )
        rows = result.all()
        for ct, ch in rows:
            remaining = ct.target_words - ch.word_count
            if 0 < remaining <= 300:
                style = get_style(settings)
                msg = get_message(
                    style,
                    "chapter_target_reminder",
                    chapter=ch.title or "Untitled",
                    words=remaining,
                )
                user_result = await db.execute(select(User).where(User.id == settings.user_id))
                user = user_result.scalar_one_or_none()
                email = user.email if user else ""
                results = await svc.send_reminder(
                    str(settings.user_id),
                    email,
                    "chapter_target_reminder",
                    f"Chapter target: {ch.title or 'Untitled'}",
                    msg,
                    in_app=True,
                    email=settings.email_reminders_enabled,
                )
                if results["in_app"] or results["email"]:
                    sent += 1
                break

    return sent


async def process_stuck_detection(db: AsyncSession) -> int:
    """Detect stuck users and send supportive nudge."""
    result = await db.execute(
        select(AccountabilitySettings).where(AccountabilitySettings.plan_paused == False)
    )
    settings_list = result.scalars().all()
    sent = 0
    svc = DefaultNotificationService(db)

    for settings in settings_list:
        if not settings.reminder_enabled:
            continue
        if not _is_reminder_type_enabled(settings, "stuck_nudge"):
            continue
        if _in_quiet_hours(settings):
            continue

        result = await db.execute(select(UserStats).where(UserStats.user_id == settings.user_id))
        stats = result.scalar_one_or_none()
        if not stats or not stats.last_writing_date:
            continue

        days_since = (date.today() - stats.last_writing_date).days
        if days_since < 5:
            continue

        style = get_style(settings)
        msg = get_message(style, "stuck")
        user_result = await db.execute(select(User).where(User.id == settings.user_id))
        user = user_result.scalar_one_or_none()
        email = user.email if user else ""
        results = await svc.send_reminder(
            str(settings.user_id),
            email,
            "stuck_nudge",
            "We miss you",
            msg,
            in_app=True,
            email=settings.email_reminders_enabled,
        )
        if results["in_app"] or results["email"]:
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
        days_remaining = max(1, days_overdue + 7)
        recovery = suggest_recovery_plan(
            current_words,
            plan.total_target_words,
            days_remaining,
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
