"""Trim/compress/strengthen assistant for density issues."""

from __future__ import annotations

from typing import Any

from authora.services.density.trim_vs_strengthen_engine import decide_action


DENSITY_FIX_TEMPLATES: dict[str, dict[str, Any]] = {
    "repetition_in_chapter": {
        "explanation": "This section appears to repeat an earlier beat without much new movement.",
        "why_it_matters": "Compressing can tighten the prose. State the point once clearly.",
        "suggestions": [
            "Identify the repeated point and state it once clearly",
            "Cut redundant phrasing",
            "Mark as intentional if repetition is deliberate (refrain, motif)",
        ],
    },
    "thin_section": {
        "explanation": "This moment may need more buildup to land fully.",
        "why_it_matters": "Thin sections may benefit from expansion or merging.",
        "suggestions": [
            "Add content to develop the idea",
            "Consider merging with an adjacent chapter",
            "Mark as intentional if it's a deliberate bridge",
        ],
    },
    "possible_bloat": {
        "explanation": "This chapter may be doing less than its size suggests.",
        "why_it_matters": "Trimming can improve pace. Consider compressible passages.",
        "suggestions": [
            "Trim redundant or low-value passages",
            "Compress exposition or description",
            "Consider splitting into two chapters",
        ],
    },
    "thin_transition": {
        "explanation": "This section may benefit from one bridging beat rather than a full rewrite.",
        "why_it_matters": "Smooth transitions help readers follow the flow.",
        "suggestions": [
            "Add a bridging paragraph at the start",
            "Reference the previous chapter's conclusion",
            "Use a transition phrase (However, Meanwhile, Later)",
        ],
    },
    "repeated_concepts": {
        "explanation": "This section appears to repeat an earlier beat without much new movement.",
        "why_it_matters": "Consolidating can tighten the manuscript.",
        "suggestions": [
            "Identify the core point and state it once strongly",
            "Remove redundant restatements",
            "Mark as intentional if it's a deliberate refrain",
        ],
    },
    "weak_midpoint": {
        "explanation": "This moment may need more buildup to land fully.",
        "why_it_matters": "A strong midpoint can sustain reader engagement.",
        "suggestions": [
            "Add a midpoint revelation or complication",
            "Introduce a new obstacle or discovery",
            "Mark as intentional if structure is deliberate",
        ],
    },
    "exposition_overload": {
        "explanation": "This passage may be stronger if compressed.",
        "why_it_matters": "Converting exposition to scene can increase engagement.",
        "suggestions": [
            "Trim exposition to essentials",
            "Convert key information into dialogue or action",
            "Mark as intentional if reflective pace is deliberate",
        ],
    },
    "repeated_emotional_beat": {
        "explanation": "This section appears to repeat an earlier beat without much new movement.",
        "why_it_matters": "Varying or deepening can strengthen impact.",
        "suggestions": [
            "Vary the emotional expression",
            "Deepen the beat with new dimension",
            "Mark as intentional if refrain is deliberate",
        ],
    },
    "missing_example": {
        "explanation": "This moment may need more support.",
        "why_it_matters": "Examples help readers apply the idea.",
        "suggestions": [
            "Add a concrete example or case study",
            "Include a before/after illustration",
            "Mark as intentional if abstract by design",
        ],
    },
    "bloated_intro_or_outro": {
        "explanation": "This chapter may be doing less than its size suggests.",
        "why_it_matters": "Readers often want to get to the main content.",
        "suggestions": [
            "Trim to essential points",
            "Move tangential material to later chapters",
            "Mark as intentional",
        ],
    },
    "repeated_reflection": {
        "explanation": "This section appears to repeat an earlier beat without much new movement.",
        "why_it_matters": "Consolidating can deepen the meaning.",
        "suggestions": [
            "Consolidate into one stronger reflection",
            "Deepen each reflection with new insight",
            "Mark as intentional if layered reflection is deliberate",
        ],
    },
    "emotional_over_explanation": {
        "explanation": "This passage may be stronger if compressed.",
        "why_it_matters": "Showing can sometimes replace telling.",
        "suggestions": [
            "Trim emotional explanation where action shows it",
            "Trust the reader to infer",
            "Mark as intentional if introspective style is deliberate",
        ],
    },
    "excessive_explanation": {
        "explanation": "This passage may be stronger if compressed.",
        "why_it_matters": "Readers often want to get to the action.",
        "suggestions": [
            "Trim explanation to essentials",
            "Move detailed explanation to an appendix",
            "Mark as intentional",
        ],
    },
    "missing_exercise": {
        "explanation": "This moment may need more support.",
        "why_it_matters": "Exercises help readers apply what they've learned.",
        "suggestions": [
            "Add a reflection or journaling prompt",
            "Include a practical exercise",
            "Mark as intentional if conceptual only",
        ],
    },
}


def get_density_fix_guidance(
    issue_type: str,
    issue: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get guided fix guidance for a density issue type.

    If context (density map snapshot) is provided, runs the trim-vs-strengthen
    decision engine and includes recommended_action, confidence, alternatives.
    """
    template = DENSITY_FIX_TEMPLATES.get(issue_type, {})
    issue = issue or {}
    fix_suggestions = issue.get("fix_suggestions") or []

    out = {
        "explanation": template.get("explanation", "This density issue was detected in your manuscript. Review and decide what serves the story."),
        "why_it_matters": template.get("why_it_matters", "Addressing it can tighten and strengthen your work."),
        "suggestions": template.get("suggestions", []),
        "fix_suggestions": fix_suggestions,
    }

    if context:
        decision = decide_action(issue, context)
        out["recommended_action"] = decision.get("recommended_action")
        out["confidence"] = decision.get("confidence")
        out["alternatives"] = decision.get("alternatives", [])
        out["revision_task_suggestion"] = decision.get("revision_task_suggestion")
        if decision.get("explanation"):
            out["explanation"] = decision["explanation"]

    return out
