"""Badge definitions and eligibility logic."""

from dataclasses import dataclass
from typing import Any


@dataclass
class BadgeDef:
    """Badge definition."""

    id: str
    name: str
    description: str
    icon: str
    category: str
    xp_reward: int
    criteria_type: str
    criteria_value: dict[str, Any] | None
    sort_order: int = 0


BADGE_DEFINITIONS: list[BadgeDef] = [
    # Consistency
    BadgeDef("first_word", "First Word", "Write your first word", "pen", "consistency", 10, "total_words", {"min": 1}, 0),
    BadgeDef("streak_3", "Three Day Streak", "Write 3 days in a row", "flame", "consistency", 25, "streak", {"min": 3}, 1),
    BadgeDef("streak_7", "Week Warrior", "Write 7 days in a row", "flame", "consistency", 75, "streak", {"min": 7}, 2),
    BadgeDef("streak_14", "Fortnight", "Write 14 days in a row", "flame", "consistency", 150, "streak", {"min": 14}, 3),
    BadgeDef("streak_30", "Monthly Master", "Write 30 days in a row", "flame", "consistency", 300, "streak", {"min": 30}, 4),
    BadgeDef("comeback", "Welcome Back", "Return after 7+ days away", "sunrise", "consistency", 75, "comeback", {"days_away": 7}, 5),
    # Completion
    BadgeDef("first_chapter", "Chapter One", "Complete your first chapter", "book-open", "completion", 100, "chapters_complete", {"min": 1}, 10),
    BadgeDef("five_chapters", "Building Blocks", "Complete 5 chapters", "book-open", "completion", 200, "chapters_complete", {"min": 5}, 11),
    BadgeDef("ten_chapters", "Decade", "Complete 10 chapters", "book-open", "completion", 400, "chapters_complete", {"min": 10}, 12),
    # Volume
    BadgeDef("10k_words", "10K Club", "Reach 10,000 words", "trophy", "volume", 250, "total_words", {"min": 10_000}, 20),
    BadgeDef("25k_words", "Quarter Draft", "Reach 25,000 words", "trophy", "volume", 500, "total_words", {"min": 25_000}, 21),
    BadgeDef("50k_words", "Half Novel", "Reach 50,000 words", "trophy", "volume", 1000, "total_words", {"min": 50_000}, 22),
    BadgeDef("75k_words", "Three Quarters", "Reach 75,000 words", "trophy", "volume", 1500, "total_words", {"min": 75_000}, 23),
    BadgeDef("100k_words", "Century", "Reach 100,000 words", "trophy", "volume", 2500, "total_words", {"min": 100_000}, 24),
    # Focus
    BadgeDef("focus_first", "Focused Start", "Complete your first focus session", "timer", "focus", 25, "focus_sessions", {"min": 1}, 30),
    BadgeDef("focus_10", "Deep Work", "Complete 10 focus sessions", "timer", "focus", 100, "focus_sessions", {"min": 10}, 31),
    BadgeDef("focus_25", "Focus Master", "Complete 25 focus sessions", "timer", "focus", 250, "focus_sessions", {"min": 25}, 32),
    # Personal best
    BadgeDef("pb_daily_500", "Daily 500", "Write 500 words in a day", "zap", "personal_best", 50, "daily_words", {"min": 500}, 40),
    BadgeDef("pb_daily_1000", "Daily 1K", "Write 1,000 words in a day", "zap", "personal_best", 100, "daily_words", {"min": 1000}, 41),
    BadgeDef("pb_daily_2000", "Daily 2K", "Write 2,000 words in a day", "zap", "personal_best", 200, "daily_words", {"min": 2000}, 42),
    BadgeDef("pb_weekly_5k", "Weekly 5K", "Write 5,000 words in a week", "zap", "personal_best", 150, "weekly_words", {"min": 5000}, 43),
    BadgeDef("pb_weekly_10k", "Weekly 10K", "Write 10,000 words in a week", "zap", "personal_best", 300, "weekly_words", {"min": 10000}, 44),
]


def check_badge_eligibility(
    badge: BadgeDef,
    *,
    total_words: int = 0,
    current_streak: int = 0,
    longest_streak: int = 0,
    chapters_complete: int = 0,
    focus_sessions: int = 0,
    daily_words: int = 0,
    weekly_words: int = 0,
    days_since_last_active: int | None = None,
    earned_badge_ids: set[str] | None = None,
) -> bool:
    """Check if user is eligible for a badge (not yet earned)."""
    earned = earned_badge_ids or set()
    if badge.id in earned:
        return False

    cv = badge.criteria_value or {}
    match badge.criteria_type:
        case "total_words":
            return total_words >= cv.get("min", 0)
        case "streak":
            return current_streak >= cv.get("min", 0) or longest_streak >= cv.get("min", 0)
        case "comeback":
            return days_since_last_active is not None and days_since_last_active >= cv.get("days_away", 7)
        case "chapters_complete":
            return chapters_complete >= cv.get("min", 0)
        case "focus_sessions":
            return focus_sessions >= cv.get("min", 0)
        case "daily_words":
            return daily_words >= cv.get("min", 0)
        case "weekly_words":
            return weekly_words >= cv.get("min", 0)
        case _:
            return False


def get_badges_for_context(
    total_words: int = 0,
    current_streak: int = 0,
    longest_streak: int = 0,
    chapters_complete: int = 0,
    focus_sessions: int = 0,
    daily_words: int = 0,
    weekly_words: int = 0,
    days_since_last_active: int | None = None,
    earned_badge_ids: set[str] | None = None,
) -> list[BadgeDef]:
    """Return badges user is newly eligible for."""
    earned = earned_badge_ids or set()
    result = []
    for b in BADGE_DEFINITIONS:
        if b.id in earned:
            continue
        if check_badge_eligibility(
            b,
            total_words=total_words,
            current_streak=current_streak,
            longest_streak=longest_streak,
            chapters_complete=chapters_complete,
            focus_sessions=focus_sessions,
            daily_words=daily_words,
            weekly_words=weekly_words,
            days_since_last_active=days_since_last_active,
            earned_badge_ids=earned,
        ):
            result.append(b)
    return result
