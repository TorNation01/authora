"""Finish Mode service - completion-focused manuscript workflow."""

import random
from datetime import date, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, BookSettings, Chapter, Project, ProjectMember, StreakLog, WritingPlan

# Encouraging messages by progress tier
PROGRESS_MESSAGES = [
    (0.0, "Every chapter starts with a single word. You've got this."),
    (0.1, "Momentum builds. Keep going."),
    (0.25, "You're a quarter of the way. That's real progress."),
    (0.5, "Halfway there. The finish line is in sight."),
    (0.75, "You're in the home stretch. Almost there."),
    (0.9, "So close. One more push."),
    (0.95, "The finish line is right there. You've got this."),
    (1.0, "You did it. Manuscript complete."),
]

MILESTONE_MESSAGES = {
    1: "First chapter done. The hardest one is behind you.",
    3: "Three chapters in. You're building something real.",
    5: "Five chapters. You're a writer.",
    10: "Ten chapters. This is a book.",
    15: "Fifteen chapters. You're almost there.",
    20: "Twenty chapters. Incredible.",
}

# Celebratory messages for final stretch (last N chapters)
FINAL_STRETCH_MESSAGES = [
    "One chapter left. This is it.",
    "Two chapters to go. You're almost there.",
    "Three chapters remaining. The home stretch.",
]

# Finish Mode momentum messages (draft now, refine later)
FINISH_MODE_MOMENTUM = [
    "Draft now, refine later. Keep the momentum.",
    "One finished section beats another postponed perfect draft.",
    "Your manuscript is waiting. Let's move it forward.",
    "Done is better than perfect. Keep going.",
    "A small session today keeps the book moving.",
]

# Sprint duration options (days)
FINISH_MODE_SPRINTS = [7, 14, 30]


def _get_progress_message(progress: float) -> str:
    """Return encouraging message for current progress."""
    for threshold, msg in reversed(PROGRESS_MESSAGES):
        if progress >= threshold:
            return msg
    return PROGRESS_MESSAGES[0][1]


def _get_milestone_message(done_count: int) -> str | None:
    """Return milestone message if applicable."""
    return MILESTONE_MESSAGES.get(done_count)


def _get_final_stretch_message(remaining: int) -> str | None:
    """Return encouraging message for final stretch (last 1–3 chapters)."""
    if 1 <= remaining <= 3:
        return FINAL_STRETCH_MESSAGES[remaining - 1]
    return None


def _is_final_stretch(remaining: int) -> bool:
    """True when 1–3 chapters left (celebratory state)."""
    return 1 <= remaining <= 3


async def get_finish_mode_stats(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    project_id: UUID | None = None,
) -> dict[str, Any]:
    """
    Compute finish mode stats: remaining chapters, forecast, next section, etc.
    If project_id given, allows owner or project member. Otherwise owner only.
    """
    if project_id:
        result = await db.execute(
            select(Book)
            .where(Book.id == book_id, Book.project_id == project_id)
        )
        book = result.scalar_one_or_none()
        if not book:
            return {}
        proj = await db.get(Project, project_id)
        if not proj:
            return {}
        if proj.user_id != user_id:
            member = await db.execute(
                select(ProjectMember).where(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id,
                )
            )
            if not member.scalar_one_or_none():
                return {}
    else:
        result = await db.execute(
            select(Book).join(Project).where(Book.id == book_id, Project.user_id == user_id)
        )
        book = result.scalar_one_or_none()
        if not book:
            return {}

    # Load book_settings for finish_mode
    settings_result = await db.execute(
        select(BookSettings).where(BookSettings.book_id == book_id)
    )
    book_settings = settings_result.scalar_one_or_none()
    settings = (book_settings.settings or {}) if book_settings else {}
    finish_mode = settings.get("finish_mode") or {}
    enabled = finish_mode.get("enabled", False)
    target_date_str = finish_mode.get("target_date")
    words_per_day = finish_mode.get("words_per_day") or 500

    # Load chapters
    chapters_result = await db.execute(
        select(Chapter)
        .where(Chapter.book_id == book_id, Chapter.deleted_at.is_(None))
        .order_by(Chapter.sort_order)
    )
    chapters = list(chapters_result.scalars().all())

    done_chapters = [c for c in chapters if c.section_status == "done"]
    remaining_chapters = [c for c in chapters if c.section_status != "done"]
    done_count = len(done_chapters)
    total_count = len(chapters)
    progress_pct = (done_count / total_count * 100) if total_count else 0
    is_complete = done_count == total_count and total_count > 0

    total_words = sum(c.word_count for c in chapters)
    avg_words_per_chapter = (total_words / total_count) if total_count else 1500
    min_chapter_words = 500
    target_per_chapter = max(avg_words_per_chapter, min_chapter_words)
    # Work remaining: words still needed per remaining chapter (target - current, min 0)
    work_remaining = sum(
        max(0, target_per_chapter - c.word_count) for c in remaining_chapters
    ) if remaining_chapters else 0
    if work_remaining <= 0 and remaining_chapters:
        work_remaining = len(remaining_chapters) * target_per_chapter

    target_date = None
    if target_date_str:
        try:
            target_date = date.fromisoformat(target_date_str)
        except (ValueError, TypeError):
            pass

    today = date.today()
    days_until_target = None
    days_to_finish = None
    daily_plan_words = words_per_day

    # Check WritingPlan for target
    plan_result = await db.execute(
        select(WritingPlan)
        .where(
            WritingPlan.book_id == book_id,
            WritingPlan.user_id == user_id,
            WritingPlan.status == "active",
        )
    )
    plan = plan_result.scalar_one_or_none()
    if plan and plan.target_finish_date:
        target_date = plan.target_finish_date
        days_until_target = (target_date - today).days
        if days_until_target > 0:
            days_to_finish = days_until_target
            daily_plan_words = int(work_remaining / days_to_finish) if work_remaining else words_per_day
        elif days_until_target <= 0:
            days_to_finish = 0
    elif target_date:
        days_until_target = (target_date - today).days
        if days_until_target > 0:
            days_to_finish = days_until_target
            daily_plan_words = int(work_remaining / days_to_finish) if work_remaining else words_per_day
        elif days_until_target <= 0:
            days_to_finish = 0
    else:
        if work_remaining and words_per_day:
            days_to_finish = max(1, int(work_remaining / words_per_day))

    # Realistic forecast: use recent writing pace if available
    week_start = today - timedelta(days=today.weekday())
    streak_result = await db.execute(
        select(StreakLog).where(
            StreakLog.user_id == user_id,
            StreakLog.date >= week_start,
        )
    )
    words_this_week = sum(log.words_written for log in streak_result.scalars().all())
    avg_daily_recent = words_this_week / 7 if words_this_week else 0
    on_track = True
    estimated_completion = None
    if work_remaining > 0:
        if avg_daily_recent > 0:
            days_at_pace = work_remaining / avg_daily_recent
            estimated_completion = today + timedelta(days=int(days_at_pace))
            if days_to_finish is not None and days_to_finish > 0:
                on_track = days_at_pace <= days_to_finish
        elif days_to_finish is not None:
            estimated_completion = today + timedelta(days=days_to_finish)

    # Daily plan: today's focus (next chapter + target words)
    next_chapter = remaining_chapters[0] if remaining_chapters else None
    daily_plan_today = None
    if next_chapter and not is_complete:
        daily_plan_today = {
            "chapter_id": str(next_chapter.id),
            "chapter_title": next_chapter.title,
            "target_words": min(daily_plan_words, max(work_remaining, 100)),
            "suggested_session_minutes": 25,
        }

    milestone_msg = _get_milestone_message(done_count)
    final_stretch_msg = _get_final_stretch_message(len(remaining_chapters))
    is_final_stretch = _is_final_stretch(len(remaining_chapters))

    # Momentum message (draft now, refine later)
    momentum_message = random.choice(FINISH_MODE_MOMENTUM) if FINISH_MODE_MOMENTUM else None

    # Activation: allow when 1+ chapters; suggest when 70%+ or 3+ remaining
    can_enter = total_count >= 1
    suggest_finish_mode = (
        total_count >= 3
        and progress_pct >= 70
        and len(remaining_chapters) <= 5
        and not enabled
    )

    return {
        "enabled": enabled,
        "target_date": target_date.isoformat() if target_date else None,
        "words_per_day": words_per_day,
        "chapters_done": done_count,
        "chapters_total": total_count,
        "chapters_remaining": len(remaining_chapters),
        "progress_pct": round(progress_pct, 1),
        "total_words": total_words,
        "work_remaining_estimate": int(work_remaining),
        "days_to_finish": days_to_finish,
        "days_until_target": days_until_target,
        "daily_plan_words": daily_plan_words,
        "daily_plan_today": daily_plan_today,
        "next_chapter_id": str(next_chapter.id) if next_chapter else None,
        "next_chapter_title": next_chapter.title if next_chapter else None,
        "remaining_chapters": [
            {"id": str(c.id), "title": c.title, "sort_order": c.sort_order, "word_count": c.word_count}
            for c in remaining_chapters
        ],
        "progress_message": _get_progress_message(progress_pct / 100),
        "milestone_message": milestone_msg,
        "final_stretch_message": final_stretch_msg,
        "is_final_stretch": is_final_stretch,
        "is_complete": is_complete,
        "can_enter_finish_mode": can_enter,
        "suggest_finish_mode": suggest_finish_mode,
        "momentum_message": momentum_message,
        "sprint_options": FINISH_MODE_SPRINTS,
        "forecast": {
            "on_track": on_track,
            "estimated_completion_date": estimated_completion.isoformat() if estimated_completion else None,
            "avg_daily_this_week": round(avg_daily_recent, 0),
        },
    }


async def update_finish_mode_settings(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    *,
    project_id: UUID | None = None,
    enabled: bool | None = None,
    target_date: str | None = None,
    words_per_day: int | None = None,
) -> dict[str, Any]:
    """Update finish mode settings in book_settings. If project_id given, allows owner or member."""
    if project_id:
        result = await db.execute(select(Book).where(Book.id == book_id, Book.project_id == project_id))
        book = result.scalar_one_or_none()
        if not book:
            return {}
        proj = await db.get(Project, project_id)
        if not proj:
            return {}
        if proj.user_id != user_id:
            member = await db.execute(
                select(ProjectMember).where(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == user_id,
                )
            )
            if not member.scalar_one_or_none():
                return {}
    else:
        result = await db.execute(
            select(Book).join(Project).where(Book.id == book_id, Project.user_id == user_id)
        )
        if not result.scalar_one_or_none():
            return {}

    settings_result = await db.execute(
        select(BookSettings).where(BookSettings.book_id == book_id)
    )
    book_settings = settings_result.scalar_one_or_none()
    if not book_settings:
        book_settings = BookSettings(book_id=book_id, settings={})
        db.add(book_settings)
        await db.flush()

    finish_mode = dict(book_settings.settings.get("finish_mode") or {})
    if enabled is not None:
        finish_mode["enabled"] = enabled
    if target_date is not None:
        finish_mode["target_date"] = target_date
    if words_per_day is not None:
        finish_mode["words_per_day"] = max(100, min(5000, words_per_day))

    book_settings.settings = {**(book_settings.settings or {}), "finish_mode": finish_mode}
    await db.flush()
    await db.refresh(book_settings)

    return await get_finish_mode_stats(db, book_id, user_id, project_id)
