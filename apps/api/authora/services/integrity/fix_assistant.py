"""Guided fix assistant for integrity issues."""

from __future__ import annotations

from typing import Any


FIX_TEMPLATES: dict[str, dict[str, Any]] = {
    "empty_section": {
        "explanation": "This chapter has no content yet.",
        "why_it_matters": "Empty chapters can leave readers confused or suggest the manuscript is incomplete.",
        "suggestions": [
            "Add content to this chapter",
            "If it's a placeholder, consider removing or merging with another chapter",
        ],
    },
    "placeholder_heavy": {
        "explanation": "This section is very short or contains placeholder text.",
        "why_it_matters": "Placeholders can slip through to export and look unprofessional.",
        "suggestions": [
            "Expand this section with actual content",
            "Replace TODO/TBD with real text",
            "Consider merging with an adjacent chapter if it's meant to be brief",
        ],
    },
    "unresolved_placeholder": {
        "explanation": "Placeholder text (TODO, TBD, etc.) was found in this chapter.",
        "why_it_matters": "Placeholders should be resolved before export or sharing.",
        "suggestions": [
            "Search for and replace all placeholder markers",
            "Add the missing content or remove the placeholder section",
        ],
    },
    "weak_opening": {
        "explanation": "The opening chapter may need strengthening.",
        "why_it_matters": "Readers decide whether to continue in the first few pages.",
        "suggestions": [
            "Add or clarify the inciting incident",
            "Strengthen the opening hook",
            "Ensure the protagonist and stakes are clear early",
        ],
    },
    "weak_ending": {
        "explanation": "The final chapter is short. This may be intentional (open ending, series) or need development.",
        "why_it_matters": "Readers often expect some resolution; open endings can work when deliberate.",
        "suggestions": [
            "Add or strengthen the resolution if you want closure",
            "Mark as intentional if an open or unresolved ending is deliberate",
        ],
    },
    "missing_transition": {
        "explanation": "This chapter may need a clearer transition from the previous one.",
        "why_it_matters": "Smooth transitions help readers follow the flow of ideas.",
        "suggestions": [
            "Add a bridging paragraph at the start",
            "Reference the previous chapter's conclusion",
            "Use a transition phrase (However, Therefore, Next, etc.)",
        ],
    },
    "reflection_missing": {
        "explanation": "This memoir chapter may benefit from added reflection.",
        "why_it_matters": "Reflection connects events to meaning for the reader.",
        "suggestions": [
            "Add your present perspective on the events",
            "Include what you learned or realized",
            "Balance event with meaning",
        ],
    },
    "exercise_missing": {
        "explanation": "This workbook chapter may benefit from an exercise or prompt.",
        "why_it_matters": "Exercises help readers apply what they've learned.",
        "suggestions": [
            "Add a reflection or journaling prompt",
            "Include a practical exercise",
            "Add a \"Your turn\" or \"Try this\" section",
        ],
    },
    "character_single_appearance": {
        "explanation": "Some characters appear in only one chapter.",
        "why_it_matters": "Characters who appear once may feel underdeveloped or unnecessary.",
        "suggestions": [
            "Develop their arc across multiple chapters",
            "Or mark them as intentional minor characters",
        ],
    },
    "too_many_threads": {
        "explanation": "Several plot threads are present across the manuscript.",
        "why_it_matters": "Too many open threads can make the ending feel scattered.",
        "suggestions": [
            "Identify which threads are essential to the core story",
            "Resolve or trim minor threads before the climax",
        ],
    },
    "pacing_trough": {
        "explanation": "Several chapters in a row are short or slow.",
        "why_it_matters": "Pacing troughs can slow reader engagement.",
        "suggestions": [
            "Add a stronger beat or scene in the slow section",
            "Consider tightening or merging short chapters",
        ],
    },
    "theme_introduced_not_developed": {
        "explanation": "A theme appears in one chapter but not elsewhere.",
        "why_it_matters": "Themes introduced once can feel dropped.",
        "suggestions": [
            "Revisit the theme in later chapters",
            "Remove it if not central to the story",
        ],
    },
    "weak_chapter_length": {
        "explanation": "This chapter is very short.",
        "why_it_matters": "Short chapters may need more development.",
        "suggestions": [
            "Expand with examples or explanation",
            "Add practical takeaway or action step",
        ],
    },
}


def get_fix_guidance(issue_type: str, issue: dict[str, Any] | None = None) -> dict[str, Any]:
    """Get guided fix guidance for an issue type."""
    template = FIX_TEMPLATES.get(issue_type, {})
    return {
        "explanation": template.get("explanation", "This issue was detected in your manuscript."),
        "why_it_matters": template.get("why_it_matters", "Addressing it can strengthen your work."),
        "suggestions": template.get("suggestions", []),
        "fix_suggestions": (issue or {}).get("fix_suggestions", []),
    }
