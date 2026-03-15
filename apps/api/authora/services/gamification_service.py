"""Gamification service: XP, streaks, badges, quests, notifications."""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    Achievement,
    Book,
    Chapter,
    DailyQuest,
    FocusSession,
    Project,
    StreakLog,
    UserStats,
    WeeklyMission,
)
from authora.services.gamification_engine import (
    get_badges_for_context,
    MILESTONE_THRESHOLDS,
)
from authora.services.gamification_engine.rules import XPSource, calculate_xp

# Lazy import to avoid circular dependency
def _get_notification_service(db: AsyncSession):
    from authora.infrastructure.notifications.factory import get_notification_service
    return get_notification_service(db)


async def get_or_create_user_stats(db: AsyncSession, user_id: UUID) -> UserStats:
    """Get or create user stats."""
    result = await db.execute(select(UserStats).where(UserStats.user_id == user_id))
    stats = result.scalar_one_or_none()
    if not stats:
        stats = UserStats(user_id=user_id)
        db.add(stats)
        await db.flush()
    return stats


def _week_start(d: date) -> date:
    """Monday of the week."""
    return d - timedelta(days=d.weekday())


async def record_words(
    db: AsyncSession,
    user_id: UUID,
    words: int,
    book_id: UUID | None = None,
    *,
    notify: bool = True,
) -> dict:
    """
    Record words written. Updates streak, XP, personal bests, quests.
    Returns dict with: stats, events (list of celebration events).
    """
    stats = await get_or_create_user_stats(db, user_id)
    today = date.today()
    now = datetime.now(timezone.utc)

    # Update last_active
    stats.last_active_at = now

    # Streak log
    result = await db.execute(
        select(StreakLog).where(StreakLog.user_id == user_id, StreakLog.date == today)
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.words_written += words
    else:
        log = StreakLog(user_id=user_id, date=today, words_written=words)
        db.add(log)

    # Recalculate streak
    streak = 0
    d = today
    while True:
        r = await db.execute(select(StreakLog).where(StreakLog.user_id == user_id, StreakLog.date == d))
        log = r.scalar_one_or_none()
        if not log or log.words_written == 0:
            break
        streak += 1
        d -= timedelta(days=1)

    stats.current_streak = streak
    if streak > stats.longest_streak:
        stats.longest_streak = streak

    # Base XP: words
    xp_gained = calculate_xp(XPSource.WORDS, words)
    stats.xp += xp_gained

    # Streak bonus (e.g. +5 XP per day of streak, max 50)
    if streak > 0:
        bonus = calculate_xp(XPSource.STREAK_BONUS, streak)
        stats.xp += bonus
        xp_gained += bonus

    # Level
    stats.level = max(1, stats.xp // 1000 + 1)

    # Total words
    stats.total_words += words

    # Comeback detection
    events = []
    if stats.last_writing_date:
        gap = (today - stats.last_writing_date).days
        if gap > 1:
            days_away = gap - 1
            if days_away >= 7:
                comeback_xp = calculate_xp(XPSource.COMEBACK)
                stats.xp += comeback_xp
                xp_gained += comeback_xp
                events.append({"type": "comeback", "xp": comeback_xp, "days_away": days_away})
                if notify:
                    svc = _get_notification_service(db)
                    await svc.send_in_app(
                        str(user_id),
                        "gamification_comeback",
                        "Welcome back",
                        f"You returned after {days_away} days. +{comeback_xp} XP to get you started.",
                    )

    stats.last_writing_date = today

    # Personal bests
    daily_words = (existing.words_written if existing else 0) + words
    if daily_words > getattr(stats, "best_daily_words", 0):
        stats.best_daily_words = daily_words
        events.append({"type": "personal_best_daily", "words": daily_words})

    week_start = _week_start(today)
    week_words = await _get_week_words(db, user_id, week_start)
    if week_words > getattr(stats, "best_weekly_words", 0):
        stats.best_weekly_words = week_words
        events.append({"type": "personal_best_weekly", "words": week_words})

    # Milestone check (award highest unreached milestone)
    for t in reversed(MILESTONE_THRESHOLDS):
        if stats.total_words >= t:
            r = await db.execute(
                select(Achievement).where(
                    Achievement.user_id == user_id,
                    Achievement.type == f"milestone_{t}",
                )
            )
            if r.scalar_one_or_none() is None:
                milestone_xp = calculate_xp(XPSource.MILESTONE, t)
                stats.xp += milestone_xp
                xp_gained += milestone_xp
                ach = Achievement(
                    user_id=user_id,
                    type=f"milestone_{t}",
                    badge_id=None,
                    achievement_metadata={"words": t},
                )
                db.add(ach)
                events.append({"type": "milestone", "words": t, "xp": milestone_xp})
                if notify:
                    svc = _get_notification_service(db)
                    await svc.send_in_app(
                        str(user_id),
                        "gamification_milestone",
                        f"{t:,} words",
                        f"Milestone reached! +{milestone_xp} XP.",
                    )
                break

    # Badge check
    earned_ids = await _get_earned_badge_ids(db, user_id)
    chapters_complete = await _count_completed_chapters(db, user_id)
    focus_count = await _count_focus_sessions(db, user_id)
    days_away = (
        (today - stats.last_writing_date).days - 1
        if stats.last_writing_date and (today - stats.last_writing_date).days > 1
        else None
    )
    new_badges = get_badges_for_context(
        total_words=stats.total_words,
        current_streak=streak,
        longest_streak=stats.longest_streak,
        chapters_complete=chapters_complete,
        focus_sessions=focus_count,
        daily_words=daily_words,
        weekly_words=week_words,
        days_since_last_active=days_away if days_away and days_away >= 7 else None,
        earned_badge_ids=earned_ids,
    )
    for b in new_badges:
        stats.xp += b.xp_reward
        xp_gained += b.xp_reward
        ach = Achievement(user_id=user_id, type=b.id, badge_id=b.id, achievement_metadata=None)
        db.add(ach)
        events.append({"type": "badge", "badge_id": b.id, "name": b.name, "xp": b.xp_reward})
        if notify:
            svc = _get_notification_service(db)
            await svc.send_in_app(
                str(user_id),
                "gamification_badge",
                b.name,
                b.description or f"+{b.xp_reward} XP",
            )

    # Update daily quests
    await _update_daily_quests(db, user_id, today, daily_words, stats, events, notify)
    await _update_weekly_missions(db, user_id, week_start, week_words, stats, events, notify)

    await db.flush()
    await db.refresh(stats)
    return {"stats": stats, "events": events, "xp_gained": xp_gained}


async def _get_week_words(db: AsyncSession, user_id: UUID, week_start: date) -> int:
    end = week_start + timedelta(days=7)
    r = await db.execute(
        select(func.coalesce(func.sum(StreakLog.words_written), 0)).where(
            StreakLog.user_id == user_id,
            StreakLog.date >= week_start,
            StreakLog.date < end,
        )
    )
    return int(r.scalar() or 0)


async def _get_earned_badge_ids(db: AsyncSession, user_id: UUID) -> set[str]:
    r = await db.execute(select(Achievement.type, Achievement.badge_id).where(Achievement.user_id == user_id))
    ids = set()
    for row in r.all():
        ids.add(row.badge_id or row.type)
    return ids


async def _count_completed_chapters(db: AsyncSession, user_id: UUID) -> int:
    subq = select(Book.id).join(Project).where(Project.user_id == user_id)
    r = await db.execute(
        select(func.count(Chapter.id)).where(
            Chapter.book_id.in_(subq),
            Chapter.gamification_completed_at.isnot(None),
        )
    )
    return int(r.scalar() or 0)


async def _count_focus_sessions(db: AsyncSession, user_id: UUID) -> int:
    r = await db.execute(
        select(func.count(FocusSession.id)).where(
            FocusSession.user_id == user_id,
            FocusSession.completed_at.isnot(None),
        )
    )
    return int(r.scalar() or 0)


async def _update_daily_quests(
    db: AsyncSession,
    user_id: UUID,
    today: date,
    daily_words: int,
    stats: UserStats,
    events: list,
    notify: bool,
) -> None:
    r = await db.execute(
        select(DailyQuest).where(DailyQuest.user_id == user_id, DailyQuest.quest_date == today)
    )
    quests = list(r.scalars().all())
    if not quests:
        quests = await _ensure_daily_quests(db, user_id, today)

    for q in quests:
        if q.completed_at:
            continue
        if q.quest_type == "words":
            q.current_value = min(daily_words, q.target_value)
        elif q.quest_type == "write_any":
            q.current_value = 1 if daily_words > 0 else 0
        if q.current_value >= q.target_value:
            q.completed_at = datetime.now(timezone.utc)
            stats.xp += q.xp_reward
            events.append({"type": "daily_quest", "title": q.title, "xp": q.xp_reward})
            if notify:
                svc = _get_notification_service(db)
                await svc.send_in_app(
                    str(user_id),
                    "gamification_quest",
                    "Daily quest complete",
                    f"{q.title} — +{q.xp_reward} XP",
                )


async def get_or_create_daily_quests(db: AsyncSession, user_id: UUID) -> list[DailyQuest]:
    """Get or create today's daily quests. Syncs current_value from streak log."""
    today = date.today()
    r = await db.execute(
        select(DailyQuest).where(DailyQuest.user_id == user_id, DailyQuest.quest_date == today)
    )
    quests = list(r.scalars().all())
    if not quests:
        quests = await _ensure_daily_quests(db, user_id, today)
    r = await db.execute(
        select(StreakLog).where(StreakLog.user_id == user_id, StreakLog.date == today)
    )
    log = r.scalar_one_or_none()
    daily_words = log.words_written if log else 0
    for q in quests:
        if q.completed_at:
            continue
        if q.quest_type == "words":
            q.current_value = min(daily_words, q.target_value)
        elif q.quest_type == "write_any":
            q.current_value = 1 if daily_words > 0 else 0
        if q.current_value >= q.target_value:
            q.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return quests


async def get_or_create_weekly_missions(db: AsyncSession, user_id: UUID) -> list[WeeklyMission]:
    """Get or create this week's missions. Syncs current_value from streak logs."""
    week_start = _week_start(date.today())
    r = await db.execute(
        select(WeeklyMission).where(
            WeeklyMission.user_id == user_id,
            WeeklyMission.week_start == week_start,
        )
    )
    missions = list(r.scalars().all())
    if not missions:
        missions = await _ensure_weekly_missions(db, user_id, week_start)
    week_words = await _get_week_words(db, user_id, week_start)
    for m in missions:
        if m.completed_at:
            continue
        m.current_value = week_words
        if m.current_value >= m.target_value:
            m.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return missions


async def _ensure_daily_quests(db: AsyncSession, user_id: UUID, today: date) -> list[DailyQuest]:
    """Ensure user has daily quests for the day."""
    import random
    templates = [
        ("words", "Write 250 words today", 250, 50),
        ("words", "Write 500 words today", 500, 75),
        ("write_any", "Write something today", 1, 25),
    ]
    chosen = random.sample(templates, min(2, len(templates)))
    quests = []
    for qtype, title, target, xp in chosen:
        q = DailyQuest(
            user_id=user_id,
            quest_date=today,
            quest_type=qtype,
            title=title,
            target_value=target,
            current_value=0,
            xp_reward=xp,
        )
        db.add(q)
        quests.append(q)
    await db.flush()
    return quests


async def _update_weekly_missions(
    db: AsyncSession,
    user_id: UUID,
    week_start: date,
    week_words: int,
    stats: UserStats,
    events: list,
    notify: bool,
) -> None:
    r = await db.execute(
        select(WeeklyMission).where(
            WeeklyMission.user_id == user_id,
            WeeklyMission.week_start == week_start,
        )
    )
    missions = list(r.scalars().all())
    if not missions:
        missions = await _ensure_weekly_missions(db, user_id, week_start)

    for m in missions:
        if m.completed_at:
            continue
        m.current_value = week_words
        if m.current_value >= m.target_value:
            m.completed_at = datetime.now(timezone.utc)
            stats.xp += m.xp_reward
            events.append({"type": "weekly_mission", "title": m.title, "xp": m.xp_reward})
            if notify:
                svc = _get_notification_service(db)
                await svc.send_in_app(
                    str(user_id),
                    "gamification_mission",
                    "Weekly mission complete",
                    f"{m.title} — +{m.xp_reward} XP",
                )


async def _ensure_weekly_missions(db: AsyncSession, user_id: UUID, week_start: date) -> list[WeeklyMission]:
    missions = [
        WeeklyMission(
            user_id=user_id,
            week_start=week_start,
            mission_type="words",
            title="Write 2,500 words this week",
            target_value=2500,
            current_value=0,
            xp_reward=200,
        ),
        WeeklyMission(
            user_id=user_id,
            week_start=week_start,
            mission_type="words",
            title="Write 5,000 words this week",
            target_value=5000,
            current_value=0,
            xp_reward=350,
        ),
    ]
    for m in missions:
        db.add(m)
    await db.flush()
    return missions


async def record_chapter_complete(
    db: AsyncSession,
    user_id: UUID,
    chapter_id: UUID,
    book_id: UUID,
    *,
    notify: bool = True,
) -> dict:
    """Record chapter completion. Awards XP and badge if eligible."""
    from authora.models import Chapter
    from authora.services.gamification.rules import XPSource, calculate_xp

    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    chapter = result.scalar_one_or_none()
    if not chapter or chapter.gamification_completed_at:
        return {"stats": None, "events": []}

    chapter.gamification_completed_at = datetime.now(timezone.utc)
    xp = calculate_xp(XPSource.CHAPTER_COMPLETE)
    stats = await get_or_create_user_stats(db, user_id)
    stats.xp += xp
    stats.last_active_at = datetime.now(timezone.utc)

    events = [{"type": "chapter_complete", "chapter_id": str(chapter_id), "xp": xp}]
    if notify:
        svc = _get_notification_service(db)
        await svc.send_in_app(
            str(user_id),
            "gamification_chapter",
            "Chapter complete",
            f"Chapter finished. +{xp} XP.",
        )

    # Badge check for chapters
    chapters_complete = await _count_completed_chapters(db, user_id)
    earned_ids = await _get_earned_badge_ids(db, user_id)
    new_badges = get_badges_for_context(
        chapters_complete=chapters_complete,
        earned_badge_ids=earned_ids,
    )
    for b in new_badges:
        if b.criteria_type == "chapters_complete":
            stats.xp += b.xp_reward
            ach = Achievement(user_id=user_id, type=b.id, badge_id=b.id, achievement_metadata=None)
            db.add(ach)
            events.append({"type": "badge", "badge_id": b.id, "name": b.name, "xp": b.xp_reward})
            if notify:
                svc = _get_notification_service(db)
                await svc.send_in_app(str(user_id), "gamification_badge", b.name, b.description or "")

    await db.flush()
    await db.refresh(stats)
    return {"stats": stats, "events": events}


async def complete_focus_session(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID,
    actual_minutes: int,
    words_written: int,
    *,
    notify: bool = True,
) -> dict:
    """Mark focus session complete and award XP."""
    from authora.services.gamification.rules import XPSource, calculate_xp

    r = await db.execute(select(FocusSession).where(FocusSession.id == session_id, FocusSession.user_id == user_id))
    session = r.scalar_one_or_none()
    if not session:
        return {"stats": None, "events": []}
    session.completed_at = datetime.now(timezone.utc)
    session.actual_minutes = actual_minutes
    session.words_written = words_written

    xp = calculate_xp(XPSource.FOCUS_SESSION)
    stats = await get_or_create_user_stats(db, user_id)
    stats.xp += xp
    stats.last_active_at = datetime.now(timezone.utc)

    events = [{"type": "focus_session", "xp": xp, "minutes": actual_minutes}]
    if notify:
        svc = _get_notification_service(db)
        await svc.send_in_app(
            str(user_id),
            "gamification_focus",
            "Focus session complete",
            f"{actual_minutes} min. +{xp} XP.",
        )

    await db.flush()
    await db.refresh(stats)
    return {"stats": stats, "events": events}


async def add_achievement(
    db: AsyncSession,
    user_id: UUID,
    achievement_type: str,
    badge_id: str | None = None,
    achievement_metadata: dict | None = None,
) -> Achievement:
    """Award achievement."""
    ach = Achievement(
        user_id=user_id,
        type=achievement_type,
        badge_id=badge_id,
        achievement_metadata=achievement_metadata,
    )
    db.add(ach)
    await db.flush()
    await db.refresh(ach)
    return ach


async def get_user_achievements(db: AsyncSession, user_id: UUID) -> list[Achievement]:
    """Get user achievements."""
    result = await db.execute(
        select(Achievement).where(Achievement.user_id == user_id).order_by(Achievement.earned_at.desc())
    )
    return list(result.scalars().all())
