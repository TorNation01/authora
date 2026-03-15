"""Point rules engine for gamification."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class XPSource(str, Enum):
    """Sources of XP."""

    WORDS = "words"
    CHAPTER_COMPLETE = "chapter_complete"
    MILESTONE = "milestone"
    DAILY_QUEST = "daily_quest"
    WEEKLY_MISSION = "weekly_mission"
    BADGE = "badge"
    FOCUS_SESSION = "focus_session"
    COMEBACK = "comeback"
    STREAK_BONUS = "streak_bonus"


@dataclass
class PointRules:
    """XP rules configuration."""

    xp_per_word: int = 1
    xp_chapter_complete: int = 100
    xp_milestone_10k: int = 250
    xp_milestone_25k: int = 500
    xp_milestone_50k: int = 1000
    xp_milestone_75k: int = 1500
    xp_milestone_100k: int = 2500
    xp_daily_quest: int = 50
    xp_weekly_mission: int = 200
    xp_focus_session: int = 25
    xp_comeback: int = 75
    streak_bonus_per_day: int = 5
    max_streak_bonus: int = 50


DEFAULT_RULES = PointRules()


def calculate_xp(
    source: XPSource,
    value: int | None = None,
    rules: PointRules | None = None,
) -> int:
    """Calculate XP for a given source and optional value."""
    r = rules or DEFAULT_RULES
    match source:
        case XPSource.WORDS:
            return (value or 0) * r.xp_per_word
        case XPSource.CHAPTER_COMPLETE:
            return r.xp_chapter_complete
        case XPSource.MILESTONE:
            return _milestone_xp(value or 0, r)
        case XPSource.DAILY_QUEST:
            return value or r.xp_daily_quest
        case XPSource.WEEKLY_MISSION:
            return value or r.xp_weekly_mission
        case XPSource.BADGE:
            return value or 0
        case XPSource.FOCUS_SESSION:
            return r.xp_focus_session
        case XPSource.COMEBACK:
            return r.xp_comeback
        case XPSource.STREAK_BONUS:
            return min(r.streak_bonus_per_day * (value or 0), r.max_streak_bonus)
        case _:
            return 0


def _milestone_xp(total_words: int, rules: PointRules) -> int:
    """XP for word count milestones."""
    if total_words >= 100_000:
        return rules.xp_milestone_100k
    if total_words >= 75_000:
        return rules.xp_milestone_75k
    if total_words >= 50_000:
        return rules.xp_milestone_50k
    if total_words >= 25_000:
        return rules.xp_milestone_25k
    if total_words >= 10_000:
        return rules.xp_milestone_10k
    return 0


MILESTONE_THRESHOLDS = [10_000, 25_000, 50_000, 75_000, 100_000]


def get_next_milestone(total_words: int) -> int | None:
    """Return next milestone threshold above current total."""
    for t in MILESTONE_THRESHOLDS:
        if total_words < t:
            return t
    return None


def get_milestone_progress(total_words: int) -> tuple[int, int] | None:
    """Return (current, next) for progress bar, or None if at max."""
    prev = 0
    for t in MILESTONE_THRESHOLDS:
        if total_words < t:
            return (total_words - prev, t - prev)
        prev = t
    return None
