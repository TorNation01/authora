"""Story Integrity Engine constants."""

SCAN_TYPES = (
    "full_project",
    "chapter",
    "section",
    "revision_pass",
    "export_readiness",
    "pre_finish",
    "manual_targeted",
)

SEVERITIES = ("low", "moderate", "high", "critical")

ISSUE_CATEGORIES = (
    "structure",
    "continuity",
    "pacing",
    "character",
    "emotional_arc",
    "setup_payoff",
    "theme",
    "clarity",
    "progression",
    "promise_fulfillment",
    "revision_blocker",
    "export_readiness_blocker",
)

PROJECT_TYPES = ("fiction", "nonfiction", "memoir", "workbook", "hybrid", "freeform")

GUIDANCE_MODES = ("guided", "flexible", "freeform")

ISSUE_STATUSES = ("open", "resolved", "ignored", "intentional")
