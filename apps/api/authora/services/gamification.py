"""Gamification service - entry point."""

from authora.services.gamification_service import (
    add_achievement,
    complete_focus_session,
    get_or_create_user_stats,
    get_user_achievements,
    record_chapter_complete,
    record_words,
)

__all__ = [
    "get_or_create_user_stats",
    "record_words",
    "record_chapter_complete",
    "complete_focus_session",
    "add_achievement",
    "get_user_achievements",
]
