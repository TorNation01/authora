"""Gamification engine: rules, badges, quests."""

from authora.services.gamification_engine.rules import (
    MILESTONE_THRESHOLDS,
    PointRules,
    XPSource,
    calculate_xp,
    get_milestone_progress,
    get_next_milestone,
)
from authora.services.gamification_engine.badges import (
    BADGE_DEFINITIONS,
    BadgeDef,
    check_badge_eligibility,
    get_badges_for_context,
)

__all__ = [
    "PointRules",
    "XPSource",
    "calculate_xp",
    "get_next_milestone",
    "get_milestone_progress",
    "MILESTONE_THRESHOLDS",
    "BADGE_DEFINITIONS",
    "BadgeDef",
    "check_badge_eligibility",
    "get_badges_for_context",
]
