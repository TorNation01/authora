"""Accountability and completion engine.

Adapts to writing patterns, suggests recovery plans, detects stuck users,
prompts next best action, and prevents discouragement.
"""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    AccountabilitySettings,
    Book,
    Chapter,
    ChapterTarget,
    Goal,
    Milestone,
    RecoveryPlan,
    StreakLog,
    UserStats,
    WritingPlan,
)

# Supportive message templates by accountability style
MESSAGES = {
    "gentle": {
        "daily_reminder": "A gentle nudge: your writing space is waiting today. No pressure—just a little reminder that you're making progress.",
        "weekly_reminder": "You've been doing great. Here's a soft reminder: your weekly goal is still within reach.",
        "missed_goal": "Life happens. Your goals are still here whenever you're ready. No judgment—just support.",
        "stuck": "It's okay to take a breath. When you're ready, a small step—even 50 words—can help you find your flow again.",
        "motivational": "Every word you write is a step forward. You're building something meaningful.",
        "recovery_intro": "Here's a gentle recovery plan that fits your pace. Adjust it however feels right.",
        "milestone_reminder": "You're close to a milestone. A little more today and you'll hit it.",
        "streak_reminder": "Your {streak}-day streak is alive. A few words today keep it going.",
        "overdue_nudge": "Life happens. Your manuscript is still here when you're ready.",
        "finish_date_risk": "Your finish date might need a small adjustment. We can help you stay on track.",
        "resume_reminder": "Your last chapter is waiting. Even one paragraph can bring back the flow.",
        "chapter_target_reminder": "Chapter \"{chapter}\" is {words} words from its target. You've got this.",
    },
    "balanced": {
        "daily_reminder": "Time to write! Your daily goal is {target} words. You've got this.",
        "weekly_reminder": "Weekly check-in: {current} of {target} words. You're on track.",
        "missed_goal": "You missed a goal—no worries. Here's a recovery plan to get back on track.",
        "stuck": "Looks like you might be stuck. Try: open your last chapter and write just one sentence. Momentum often follows.",
        "motivational": "Consistency beats intensity. Small daily steps add up.",
        "recovery_intro": "Here's a balanced recovery plan. It's designed to be achievable without being overwhelming.",
        "milestone_reminder": "Milestone ahead: {words} more words to hit your target.",
        "streak_reminder": "{streak}-day streak. Keep it going with a quick session today.",
        "overdue_nudge": "You're behind schedule. Here's a recovery plan to catch up.",
        "finish_date_risk": "At your current pace, the finish date may slip. Consider adjusting or increasing daily words.",
        "resume_reminder": "Resume \"{chapter}\" and add a few more sentences. Momentum builds quickly.",
        "chapter_target_reminder": "\"{chapter}\" needs {words} more words. One focused session.",
    },
    "firm": {
        "daily_reminder": "Daily goal: {target} words. Your commitment is waiting.",
        "weekly_reminder": "Weekly target: {current}/{target} words. Stay on track.",
        "missed_goal": "Goal missed. Here's a recovery plan. Let's get back on schedule.",
        "stuck": "You haven't written in a while. Next action: open your manuscript and write 100 words. No editing—just momentum.",
        "motivational": "Discipline is choosing what you want most over what you want now.",
        "recovery_intro": "Recovery plan to catch up. Stick to schedule and you'll finish on time.",
        "milestone_reminder": "Milestone: {words} words to go. Schedule a session today.",
        "streak_reminder": "{streak}-day streak. Don't break it—write something today.",
        "overdue_nudge": "Overdue. Recovery plan attached. Execute to get back on track.",
        "finish_date_risk": "Finish date at risk. Increase daily output or adjust the deadline.",
        "resume_reminder": "Open \"{chapter}\" and write the next paragraph. Go.",
        "chapter_target_reminder": "Chapter \"{chapter}\": {words} words to target. One session.",
    },
    "coach": {
        "daily_reminder": "Coach check-in: {target} words today. What's your first sentence?",
        "weekly_reminder": "Weekly progress: {current}/{target}. What's working? What needs adjustment?",
        "missed_goal": "You missed a goal. Let's diagnose: was it too ambitious, or did life get in the way? Here's a recovery plan.",
        "stuck": "Stuck? Here's your next move: open your book, read the last paragraph, and write the next one. One paragraph. Go.",
        "motivational": "Every champion was once a beginner. Keep showing up.",
        "recovery_intro": "Here's your recovery plan. I've broken it into small wins so you can build momentum.",
    },
    "structured": {
        "daily_reminder": "[{date}] Daily target: {target} words. Schedule: {schedule}.",
        "weekly_reminder": "[Week {week}] Progress: {current}/{target} words. Milestone: {next_milestone}.",
        "missed_goal": "Goal missed. Recovery plan generated. Follow the schedule below to realign.",
        "stuck": "No activity detected. Next action: {next_action}. Target: {target} words.",
        "motivational": "Structure + consistency = completion.",
        "recovery_intro": "Recovery plan (structured). Daily targets and milestones below.",
        "milestone_reminder": "[{date}] Milestone: {words} words remaining.",
        "streak_reminder": "[Streak {streak}] Maintain with today's session.",
        "overdue_nudge": "Overdue. Recovery schedule below.",
        "finish_date_risk": "Finish date at risk. Review forecast and adjust.",
        "resume_reminder": "Resume: {chapter}. Target: {words} words.",
        "chapter_target_reminder": "[{chapter}] {words} words to target.",
    },
}


def get_style(settings: AccountabilitySettings | None) -> str:
    """Get user's accountability style."""
    if settings and settings.accountability_style in MESSAGES:
        return settings.accountability_style
    return "balanced"


def get_message(style: str, key: str, **kwargs) -> str:
    """Get supportive message for style and key."""
    msg = MESSAGES.get(style, MESSAGES["balanced"]).get(key, "")
    return msg.format(**kwargs) if kwargs else msg


async def get_or_create_settings(db: AsyncSession, user_id: UUID) -> AccountabilitySettings:
    """Get or create accountability settings."""
    result = await db.execute(select(AccountabilitySettings).where(AccountabilitySettings.user_id == user_id))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = AccountabilitySettings(user_id=user_id)
        db.add(settings)
        await db.flush()
    return settings


async def get_user_stats(db: AsyncSession, user_id: UUID) -> UserStats | None:
    """Get user stats."""
    result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    return result.scalar_one_or_none()


async def get_words_this_week(db: AsyncSession, user_id: UUID, book_id: UUID | None = None) -> int:
    """Get words written this week (all or for a book)."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    result = await db.execute(
        select(StreakLog).where(
            StreakLog.user_id == user_id,
            StreakLog.date >= week_start,
        )
    )
    logs = result.scalars().all()
    return sum(log.words_written for log in logs)


async def get_words_today(db: AsyncSession, user_id: UUID) -> int:
    """Get words written today."""
    today = date.today()
    result = await db.execute(
        select(StreakLog).where(StreakLog.user_id == user_id, StreakLog.date == today)
    )
    log = result.scalar_one_or_none()
    return log.words_written if log else 0


async def get_book_word_count(db: AsyncSession, book_id: UUID) -> int:
    """Get total word count for a book."""
    result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id)
    )
    chapters = result.scalars().all()
    return sum(c.word_count for c in chapters)


def compute_consistency_score(
    days_written: int,
    days_elapsed: int,
    target_days_per_week: float = 5.0,
) -> float:
    """Compute writing consistency score (0-100)."""
    if days_elapsed <= 0:
        return 100.0
    expected_sessions = (days_elapsed / 7) * target_days_per_week
    if expected_sessions <= 0:
        return 100.0
    ratio = min(1.0, days_written / expected_sessions)
    return round(ratio * 100, 1)


def forecast_completion(
    current_words: int,
    target_words: int,
    days_remaining: int,
    avg_daily_words: float,
) -> dict:
    """Forecast completion date and required daily pace."""
    remaining = target_words - current_words
    if remaining <= 0:
        return {"on_track": True, "estimated_done": date.today(), "daily_needed": 0}


    if avg_daily_words > 0 and days_remaining > 0:
        days_at_current = remaining / avg_daily_words
        estimated_done = date.today() + timedelta(days=int(days_at_current))
        on_track = days_at_current <= days_remaining
    else:
        estimated_done = None
        on_track = False

    daily_needed = remaining / days_remaining if days_remaining > 0 else remaining

    return {
        "on_track": on_track,
        "estimated_done": estimated_done,
        "daily_needed": round(daily_needed, 0),
        "remaining_words": remaining,
    }


def suggest_recovery_plan(
    current_words: int,
    target_words: int,
    days_remaining: int,
    style: str = "balanced",
) -> dict:
    """Suggest a recovery plan when behind."""
    remaining = target_words - current_words
    if remaining <= 0 or days_remaining <= 0:
        return {"needed": False}

    daily_needed = remaining / days_remaining
    # Cap at 2000 words/day for recovery
    if daily_needed > 2000:
        daily_needed = 2000
        adjusted_days = int(remaining / daily_needed)
        message = get_message(style, "recovery_intro") + f" At {int(daily_needed)} words/day, you'll need about {adjusted_days} more days."
    else:
        message = get_message(style, "recovery_intro")

    schedule = []
    d = date.today()
    left = remaining
    for _ in range(min(days_remaining, 14)):
        if left <= 0:
            break
        chunk = min(int(daily_needed), left, 2000)
        schedule.append({"date": d.isoformat(), "target": chunk})
        left -= chunk
        d += timedelta(days=1)

    return {
        "needed": True,
        "suggested_daily_words": int(daily_needed),
        "remaining_words": remaining,
        "days_remaining": days_remaining,
        "message": message,
        "schedule": schedule,
    }


def detect_stuck(
    last_writing_date: date | None,
    days_threshold: int = 5,
) -> bool:
    """Detect if user might be stuck (no writing for N days)."""
    if not last_writing_date:
        return True
    return (date.today() - last_writing_date).days >= days_threshold


def get_next_best_action(
    settings: AccountabilitySettings | None,
    daily_goal: int | None,
    words_today: int,
    last_chapter: Chapter | None,
) -> str:
    """Suggest next best action."""
    style = get_style(settings)
    target = daily_goal or 500

    if words_today >= target:
        return get_message(style, "motivational")

    if last_chapter:
        return f"Resume where you left off: open '{last_chapter.title}' and add a few more sentences."

    return f"Start with {target - words_today} more words today. Open your manuscript and write one paragraph."
