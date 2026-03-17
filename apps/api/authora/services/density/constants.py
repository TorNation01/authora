"""Story Density Engine constants.

Artistic-freedom safeguards: thresholds and tolerances to reduce false positives
for literary, reflective, atmospheric, and intentionally slow writing.
"""

DENSITY_SCAN_TYPES = (
    "full_project",
    "chapter",
    "section",
    "revision_pass",
    "pre_export",
    "trim_chapter",
    "strengthen_chapter",
)

DENSITY_SEVERITIES = ("low", "moderate", "high", "critical")

DENSITY_ACTION_CATEGORIES = (
    "trim",
    "compress",
    "strengthen",
    "expand",
    "bridge",
    "clarify",
    "merge",
    "keep_as_intentional",
)

DENSITY_ISSUE_CATEGORIES = (
    "clutter",
    "filler",
    "repetition",
    "drag",
    "over_explanation",
    "thin_support",
    "rushed_moment",
    "weak_transition",
    "bloated_scene",
    "underweighted_payoff",
    "instructional_redundancy",
    "practical_support_gap",
)

PROJECT_TYPES = ("fiction", "nonfiction", "memoir", "workbook", "hybrid", "freeform")
GUIDANCE_MODES = ("guided", "flexible", "freeform")
DENSITY_ISSUE_STATUSES = ("open", "resolved", "ignored", "intentional")

# --- Artistic-freedom tolerance thresholds ---

# Repetition: higher = less sensitive (avoids flagging refrains, motifs, poetic repetition)
REPETITION_SCORE_THRESHOLD_GUIDED = 0.30
REPETITION_SCORE_THRESHOLD_FLEXIBLE = 0.38
REPETITION_SCORE_THRESHOLD_FREEFORM = 0.50

# Thin section: word count below which we flag (flexible = more tolerant of brief bridges)
THIN_SECTION_WORDS_GUIDED = 80
THIN_SECTION_WORDS_FLEXIBLE = 120
THIN_SECTION_WORDS_MEMOIR = 150  # memoir often has short reflective beats

# Possible bloat: word count above which we consider flagging
BLOAT_WORDS_GUIDED = 5000
BLOAT_WORDS_FLEXIBLE = 6500
BLOAT_WORDS_ATMOSPHERIC = 8000  # fantasy worldbuilding, literary

# Exposition overload: tension/movement below which we flag (flexible = more tolerant)
EXPOSITION_TENSION_THRESHOLD_GUIDED = 0.30
EXPOSITION_TENSION_THRESHOLD_FLEXIBLE = 0.22
EXPOSITION_WORDS_MIN = 1200  # need substantial length before flagging

# Memoir: reflection and emotion counts
MEMOIR_REFLECTION_COUNT_GUIDED = 3
MEMOIR_REFLECTION_COUNT_FLEXIBLE = 5
MEMOIR_EMOTION_COUNT_GUIDED = 15
MEMOIR_EMOTION_COUNT_FLEXIBLE = 25

# Nonfiction: intro/outro length tolerance
INTRO_OUTRO_WORDS_GUIDED = 1500
INTRO_OUTRO_WORDS_FLEXIBLE = 2500

# Workbook: reflection-page tolerance (short chapter with reflect/journal = intentional)
WORKBOOK_EXERCISE_WORDS_MIN = 400  # below this, don't require exercise
WORKBOOK_EXPLANATION_COUNT_FLEXIBLE = 8  # higher = more tolerant

# Chapter drag: is_dragging threshold (higher = less sensitive)
DRAG_SCORE_THRESHOLD_GUIDED = 0.60
DRAG_SCORE_THRESHOLD_FLEXIBLE = 0.70
DRAG_SCORE_THRESHOLD_MEMOIR = 0.80  # highest - poetic memoir, reflective
DRAG_SCORE_THRESHOLD_LITERARY = 0.78  # literary fiction, slow-burn
