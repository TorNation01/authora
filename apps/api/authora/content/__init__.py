"""AUTHORA built-in content: templates, messages, copy."""

from authora.content.templates import (
    get_all_templates,
    get_template_by_id,
    get_templates_by_type,
    TEMPLATE_IDS,
)
from authora.content.messages import (
    ENCOURAGEMENT_MESSAGES,
    RECOVERY_NUDGES,
    CELEBRATION_MESSAGES,
    get_random_encouragement,
    get_random_recovery_nudge,
    get_random_celebration,
)
from authora.content.copy import (
    ONBOARDING_COPY,
    HELP_TOOLTIPS,
    EMPTY_STATE_COPY,
    AI_EXPLANATION_COPY,
)

__all__ = [
    "get_all_templates",
    "get_template_by_id",
    "get_templates_by_type",
    "TEMPLATE_IDS",
    "ENCOURAGEMENT_MESSAGES",
    "RECOVERY_NUDGES",
    "CELEBRATION_MESSAGES",
    "get_random_encouragement",
    "get_random_recovery_nudge",
    "get_random_celebration",
    "ONBOARDING_COPY",
    "HELP_TOOLTIPS",
    "EMPTY_STATE_COPY",
    "AI_EXPLANATION_COPY",
]
