"""Finish Mode service - completion-focused manuscript workflow."""

from datetime import date
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Book, BookSettings, Chapter, Project, WritingPlan

# Encouraging messages by progress tier
PROGRESS_MESSAGES = [
    (0.0, "Every chapter starts with a single word. You've got this."),
    (0.1, "Momentum builds. Keep going."),
    (0.25, "You're a quarter of the way. That's real progress."),
    (0.5, "Halfway there. The finish line is in sight."),
    (0.75, "You're in the home stretch. Almost there."),
    (0.9, "So close. One more push."),
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


def _get_progress_message(progress: float) -> str:
    """Return encouraging message for current progress."""
    for threshold, msg in reversed(PROGRESS_MESSAGES):
        if progress >= threshold:
            return msg
    return PROGRESS_MESSAGES[0][1]


def _get_milestone_message(done_count: int) -> str | None:
    """Return milestone message if applicable."""
    return MILESTONE_MESSAGES.get(done_count)


async def get_finish_mode_stats(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
) -> dict[str, Any]:
    """
    Compute finish mode stats: remaining chapters, forecast, next section, etc.
    """
    result = await db.execute(
        select(Book)
        .options()
        .join(Project)
        .where(Book.id == book_id, Project.user_id == user_id)
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

    total_words = sum(c.word_count for c in chapters)
    avg_words = (total_words / total_count) if total_count else 1500
    work_remaining = len(remaining_chapters) * max(avg_words, 500)
    days_to_finish = max(1, int(work_remaining / words_per_day)) if words_per_day else None

    target_date = None
    if target_date_str:
        try:
            target_date = date.fromisoformat(target_date_str)
        except (ValueError, TypeError):
            pass

    if target_date:
        today = date.today()
        days_until_target = (target_date - today).days
        days_to_finish = max(1, days_until_target) if days_until_target > 0 else 0
        daily_plan_words = int(work_remaining / days_to_finish) if days_to_finish else words_per_day
    else:
        days_until_target = None
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
        today = date.today()
        days_until_target = (target_date - today).days
        if days_until_target > 0:
            days_to_finish = days_until_target
            daily_plan_words = int(work_remaining / days_to_finish) if days_to_finish else words_per_day

    next_chapter = remaining_chapters[0] if remaining_chapters else None
    milestone_msg = _get_milestone_message(done_count)

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
        "next_chapter_id": str(next_chapter.id) if next_chapter else None,
        "next_chapter_title": next_chapter.title if next_chapter else None,
        "remaining_chapters": [
            {"id": str(c.id), "title": c.title, "sort_order": c.sort_order, "word_count": c.word_count}
            for c in remaining_chapters
        ],
        "progress_message": _get_progress_message(progress_pct / 100),
        "milestone_message": milestone_msg,
        "can_enter_finish_mode": total_count >= 3 and progress_pct >= 30,
    }


async def update_finish_mode_settings(
    db: AsyncSession,
    book_id: UUID,
    user_id: UUID,
    *,
    enabled: bool | None = None,
    target_date: str | None = None,
    words_per_day: int | None = None,
) -> dict[str, Any]:
    """Update finish mode settings in book_settings."""
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

    return await get_finish_mode_stats(db, book_id, user_id)
