"""Unified progress dashboard: goals, streaks, milestones, next step, finish risk."""

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    AccountabilitySettings,
    Book,
    Chapter,
    Goal,
    Milestone,
    Project,
    StreakLog,
    UserStats,
    WritingPlan,
)
from authora.services.accountability_engine import (
    compute_consistency_score,
    detect_stuck,
    forecast_completion,
    get_next_best_action,
    get_or_create_settings,
    get_words_this_week,
)
from authora.services.finish_mode import get_finish_mode_stats
from authora.services.gamification import get_or_create_user_stats


async def get_progress_dashboard(
    db: AsyncSession,
    user_id: UUID,
    project_id: UUID | None = None,
    book_id: UUID | None = None,
) -> dict[str, Any]:
    """
    Unified progress dashboard: current project, goals, streaks, milestones,
    next step, finish-risk indicator, writing history.
    """
    settings = await get_or_create_settings(db, user_id)
    stats = await get_or_create_user_stats(db, user_id)

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Streak (respect visibility)
    streak_visible = getattr(settings, "streak_visible", True)
    current_streak = stats.current_streak if streak_visible else None
    longest_streak = stats.longest_streak if streak_visible else None

    # Words
    result = await db.execute(
        select(StreakLog).where(
            StreakLog.user_id == user_id,
            StreakLog.date >= week_start - timedelta(days=7 * 4),
        )
    )
    logs = result.scalars().all()
    words_today = sum(log.words_written for log in logs if log.date == today)
    words_this_week = sum(log.words_written for log in logs if log.date >= week_start)
    days_written_4_weeks = len({log.date for log in logs if log.words_written > 0})
    consistency_score = compute_consistency_score(days_written_4_weeks, 28)

    # Goals
    goals_result = await db.execute(
        select(Goal).where(
            Goal.user_id == user_id,
            Goal.completed_at.is_(None),
            Goal.is_paused == False,
        )
    )
    active_goals = goals_result.scalars().all()
    daily_goal = settings.daily_word_goal
    weekly_goal = settings.weekly_word_goal
    for g in active_goals:
        if (g.project_id and project_id and g.project_id == project_id) or (
            g.book_id and book_id and g.book_id == book_id
        ):
            if g.target_type == "words_per_day":
                daily_goal = daily_goal or g.target_value or g.target_words
            elif g.target_type == "words_per_week":
                weekly_goal = weekly_goal or g.target_value or g.target_words

    # Stuck / finish risk
    stuck = detect_stuck(stats.last_writing_date)
    finish_risk = None

    # Project/book context
    current_project = None
    current_book = None
    milestones_reached: list[dict] = []
    next_milestone: dict | None = None
    framework_stage = None
    next_suggested_step = None

    if book_id:
        book_result = await db.execute(
            select(Book, Project).join(Project, Book.project_id == Project.id).where(
                Book.id == book_id, Project.user_id == user_id
            )
        )
        row = book_result.one_or_none()
        if row:
            current_book, proj = row
            current_project = {"id": str(proj.id), "name": proj.name}

            # Milestones
            ms_result = await db.execute(
                select(Milestone)
                .where(Milestone.book_id == book_id, Milestone.user_id == user_id)
                .order_by(Milestone.sort_order)
            )
            all_milestones = ms_result.scalars().all()
            for m in all_milestones:
                if m.completed_at:
                    milestones_reached.append(
                        {"id": str(m.id), "title": m.title, "completed_at": m.completed_at.isoformat()}
                    )
                elif not next_milestone:
                    next_milestone = {"id": str(m.id), "title": m.title, "target_words": m.target_words}

            # Framework stage (from book_settings or framework) - only when guided
            guidance_mode = getattr(proj, "guidance_mode", "guided")
            if guidance_mode == "guided" and current_book.framework_id:
                framework_stage = "framework_enabled"

            # Finish mode stats
            fm = await get_finish_mode_stats(db, book_id, user_id)
            if fm:
                next_suggested_step = fm.get("daily_plan_today")
                if fm.get("days_until_target") is not None and fm.get("days_until_target") <= 7:
                    finish_risk = "deadline_approaching"
                elif stuck:
                    finish_risk = "stall_detected"

            # Last chapter for next action (if no finish mode plan)
            if not next_suggested_step:
                ch_result = await db.execute(
                    select(Chapter)
                    .where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
                    .order_by(Chapter.updated_at.desc())
                    .limit(1)
                )
                last_chapter = ch_result.scalar_one_or_none()
                msg = get_next_best_action(settings, daily_goal, words_today, last_chapter)
                next_suggested_step = {"message": msg}
        else:
            next_suggested_step = get_next_best_action(settings, daily_goal, words_today, None)
    elif project_id:
        proj_result = await db.execute(
            select(Project).where(Project.id == project_id, Project.user_id == user_id)
        )
        proj = proj_result.scalar_one_or_none()
        if proj:
            current_project = {"id": str(proj.id), "name": proj.name}
        msg = get_next_best_action(settings, daily_goal, words_today, None)
        next_suggested_step = {"message": msg}
    else:
        # All projects summary
        ch_result = await db.execute(
            select(Chapter)
            .join(Book, Chapter.book_id == Book.id)
            .join(Project, Book.project_id == Project.id)
            .where(Project.user_id == user_id)
            .order_by(Chapter.updated_at.desc())
            .limit(1)
        )
        last_chapter = ch_result.scalar_one_or_none()
        msg = get_next_best_action(settings, daily_goal, words_today, last_chapter)
        next_suggested_step = {"message": msg}
        if stuck:
            finish_risk = "stall_detected"

    # Writing history (last 14 days)
    history = []
    for i in range(14):
        d = today - timedelta(days=i)
        day_logs = [log for log in logs if log.date == d]
        history.append(
            {"date": d.isoformat(), "words": sum(log.words_written for log in day_logs)}
        )

    # Gamification (if enabled)
    gamification_enabled = getattr(settings, "gamification_enabled", True)
    gamification = None
    if gamification_enabled:
        gamification = {
            "xp": stats.xp,
            "level": stats.level,
            "total_words": stats.total_words,
        }

    return {
        "current_project": current_project,
        "current_book": current_book and {"id": str(current_book.id), "title": current_book.title},
        "goals": {
            "daily": daily_goal,
            "weekly": weekly_goal,
            "words_today": words_today,
            "words_this_week": words_this_week,
        },
        "streaks": {
            "current": current_streak,
            "longest": longest_streak,
        },
        "consistency_score": consistency_score,
        "milestones_reached": milestones_reached,
        "next_milestone": next_milestone,
        "framework_stage": framework_stage,
        "next_suggested_step": next_suggested_step,
        "finish_risk": finish_risk,
        "stuck": stuck,
        "plan_paused": settings.plan_paused,
        "writing_history": history,
        "gamification": gamification,
    }


async def get_weekly_summary(db: AsyncSession, user_id: UUID) -> dict[str, Any]:
    """Weekly summary for the current week."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    result = await db.execute(
        select(StreakLog).where(
            StreakLog.user_id == user_id,
            StreakLog.date >= week_start,
        )
    )
    logs = result.scalars().all()
    words = sum(log.words_written for log in logs)
    days = len({log.date for log in logs if log.words_written > 0})
    return {
        "week_start": week_start.isoformat(),
        "words_this_week": words,
        "days_written": days,
    }


async def get_monthly_summary(db: AsyncSession, user_id: UUID) -> dict[str, Any]:
    """Monthly summary for the current month."""
    today = date.today()
    month_start = today.replace(day=1)
    result = await db.execute(
        select(StreakLog).where(
            StreakLog.user_id == user_id,
            StreakLog.date >= month_start,
        )
    )
    logs = result.scalars().all()
    words = sum(log.words_written for log in logs)
    days = len({log.date for log in logs if log.words_written > 0})
    return {
        "month": month_start.strftime("%Y-%m"),
        "words_this_month": words,
        "days_written": days,
    }
