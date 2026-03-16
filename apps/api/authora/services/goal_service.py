"""Writing goals service: create, complete, pause, and evaluate goals."""

from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Goal, StreakLog
from authora.models.gamification import GOAL_TARGET_TYPES

GOAL_PRESETS = {
    "gentle": {"words_per_day": 250, "words_per_week": 1500, "sessions_per_week": 3},
    "balanced": {"words_per_day": 500, "words_per_week": 3500, "sessions_per_week": 5},
    "aggressive": {"words_per_day": 1000, "words_per_week": 7000, "sessions_per_week": 6},
}


async def create_goal(
    db: AsyncSession,
    user_id: UUID,
    *,
    target_type: str | None = None,
    target_value: int | None = None,
    target_words: int = 0,
    deadline: datetime | None = None,
    book_id: UUID | None = None,
    project_id: UUID | None = None,
    preset: str | None = None,
    extra_data: dict | None = None,
) -> Goal:
    """Create a writing goal. Uses preset or explicit values."""
    if preset and preset in GOAL_PRESETS:
        p = GOAL_PRESETS[preset]
        target_type = target_type or "words_per_day"
        target_value = target_value or p.get("words_per_day", 500)
    elif target_type and target_value is not None:
        pass
    elif target_words > 0 and not target_type:
        target_type = "legacy"
        target_value = target_words
    else:
        target_type = target_type or "words_per_day"
        target_value = target_value or 500

    if target_type not in GOAL_TARGET_TYPES and target_type != "legacy":
        target_type = "words_per_day"

    if target_type == "words_per_day" or target_type == "words_per_week":
        target_words = target_value or target_words
    if target_words <= 0:
        target_words = target_value or 500

    goal = Goal(
        user_id=user_id,
        book_id=book_id,
        project_id=project_id,
        target_words=target_words or target_value or 500,
        deadline=deadline,
        target_type=target_type,
        target_value=target_value,
        extra_data=extra_data,
    )
    db.add(goal)
    await db.flush()
    await db.refresh(goal)
    return goal


async def check_goal_completion(
    db: AsyncSession,
    user_id: UUID,
    words_added: int,
    book_id: UUID | None = None,
    project_id: UUID | None = None,
    words_today: int | None = None,
    words_this_week: int | None = None,
) -> list[Goal]:
    """Check if any active goals were completed by this write. Returns completed goals."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    result = await db.execute(
        select(Goal).where(
            Goal.user_id == user_id,
            Goal.completed_at.is_(None),
            Goal.is_paused == False,
        )
    )
    goals = result.scalars().all()
    completed: list[Goal] = []

    for g in goals:
        if g.book_id and book_id and g.book_id != book_id:
            continue
        if g.project_id and project_id and g.project_id != project_id:
            continue
        if g.low_energy_mode:
            continue

        tt = g.target_type or "legacy"
        if tt == "legacy":
            if g.target_words and g.deadline and date.today() >= g.deadline.date():
                total = await _get_words_for_goal(db, user_id, g, today, week_start)
                if total >= g.target_words:
                    g.completed_at = datetime.now(timezone.utc)
                    completed.append(g)
        elif tt == "words_per_day":
            daily = words_today if words_today is not None else words_added
            if daily >= (g.target_value or g.target_words):
                g.completed_at = datetime.now(timezone.utc)
                completed.append(g)
        elif tt == "words_per_week":
            week_words = words_this_week
            if week_words is None:
                week_words = await _get_week_words(db, user_id, week_start, g.book_id, g.project_id)
            if week_words >= (g.target_value or g.target_words):
                g.completed_at = datetime.now(timezone.utc)
                completed.append(g)

    return completed


async def _get_week_words(
    db: AsyncSession,
    user_id: UUID,
    week_start: date,
    book_id: UUID | None,
    project_id: UUID | None,
) -> int:
    """Get words written this week for a goal scope."""
    result = await db.execute(
        select(StreakLog).where(
            StreakLog.user_id == user_id,
            StreakLog.date >= week_start,
        )
    )
    return sum(log.words_written for log in result.scalars().all())


async def _get_words_for_goal(
    db: AsyncSession,
    user_id: UUID,
    goal: Goal,
    today: date,
    week_start: date,
) -> int:
    """Get total words for goal scope (all-time for legacy)."""
    result = await db.execute(
        select(StreakLog).where(StreakLog.user_id == user_id)
    )
    return sum(log.words_written for log in result.scalars().all())


async def pause_goal(db: AsyncSession, goal_id: UUID, user_id: UUID) -> Goal | None:
    """Pause a goal."""
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
    goal = result.scalar_one_or_none()
    if goal:
        goal.is_paused = True
        await db.flush()
    return goal


async def resume_goal(db: AsyncSession, goal_id: UUID, user_id: UUID) -> Goal | None:
    """Resume a paused goal."""
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id))
    goal = result.scalar_one_or_none()
    if goal:
        goal.is_paused = False
        await db.flush()
    return goal


async def list_active_goals(
    db: AsyncSession,
    user_id: UUID,
    project_id: UUID | None = None,
    book_id: UUID | None = None,
) -> list[Goal]:
    """List active (non-completed, non-paused) goals."""
    q = select(Goal).where(
        Goal.user_id == user_id,
        Goal.completed_at.is_(None),
        Goal.is_paused == False,
    )
    if project_id:
        q = q.where((Goal.project_id == project_id) | (Goal.project_id.is_(None)))
    if book_id:
        q = q.where((Goal.book_id == book_id) | (Goal.book_id.is_(None)))
    result = await db.execute(q.order_by(Goal.created_at.desc()))
    return list(result.scalars().all())
