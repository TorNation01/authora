"""Trim-vs-strengthen decision engine for density issues.

Helps the writer decide whether a weak section should be cut, compressed,
expanded, bridged, clarified, or left alone.
"""

from __future__ import annotations

from typing import Any

ACTIONS = (
    "trim",
    "compress",
    "strengthen",
    "expand",
    "bridge",
    "merge",
    "clarify",
    "keep_as_intentional",
)


def decide_action(
    issue: dict[str, Any],
    context: dict[str, Any],
) -> dict[str, Any]:
    """Decide the best likely action for a density issue.

    Args:
        issue: Density issue dict (issue_type, category, action_category, chapter_id, etc.)
        context: Density map snapshot + optional chapter-specific data

    Returns:
        recommended_action, confidence, explanation, alternatives, revision_task_suggestion
    """
    issue_type = issue.get("issue_type", "")
    category = issue.get("category", "")
    current_action = issue.get("action_category", "trim")
    chapter_id = issue.get("chapter_id")
    related_ids = issue.get("related_chapter_ids") or []

    project_type = context.get("project_type", "fiction")
    guidance_mode = context.get("guidance_mode", "flexible")

    purpose_data = _get_chapter_context(context, chapter_id, "scene_purpose_analysis", "chapter_purposes")
    drag_data = _get_chapter_context(context, chapter_id, "chapter_drag_analysis", "chapter_drag_scores")
    rep_data = _get_chapter_context(context, chapter_id, "repetition_analysis", "chapter_repetition_heat")
    density_data = _get_density_chapter(context, chapter_id)

    purpose_clarity = purpose_data.get("purpose_clarity", 0.5) if purpose_data else 0.5
    primary_jobs = purpose_data.get("primary_jobs", []) if purpose_data else []
    emotional_density = density_data.get("emotional_density", 0) if density_data else 0
    is_dragging = drag_data.get("is_dragging", False) if drag_data else False
    repetition_heat = rep_data.get("repetition_heat", 0) if rep_data else 0
    heat_level = rep_data.get("heat_level", "low") if rep_data else "low"

    rule = _apply_decision_rules(
        issue_type=issue_type,
        category=category,
        current_action=current_action,
        purpose_clarity=purpose_clarity,
        primary_jobs=primary_jobs,
        emotional_density=emotional_density,
        is_dragging=is_dragging,
        repetition_heat=repetition_heat,
        heat_level=heat_level,
        has_related=len(related_ids) > 0,
        project_type=project_type,
        guidance_mode=guidance_mode,
    )

    return {
        "recommended_action": rule["action"],
        "confidence": rule["confidence"],
        "explanation": rule["explanation"],
        "alternatives": rule["alternatives"],
        "revision_task_suggestion": rule.get("revision_task_suggestion"),
    }


def _get_density_chapter(context: dict[str, Any], chapter_id: str | None) -> dict[str, Any] | None:
    """Get chapter from density_by_chapter by chapter_id."""
    if not chapter_id:
        return None
    items = context.get("density_by_chapter") or []
    ch_id_str = str(chapter_id)
    for item in items:
        if str(item.get("chapter_id", "")) == ch_id_str:
            return item
    return None


def _get_chapter_context(
    context: dict[str, Any],
    chapter_id: str | None,
    analysis_key: str,
    list_key: str,
) -> dict[str, Any] | None:
    """Get chapter-specific data from context."""
    if not chapter_id:
        return None
    analysis = context.get(analysis_key) or {}
    items = analysis.get(list_key) or []
    ch_id_str = str(chapter_id)
    for item in items:
        if str(item.get("chapter_id", "")) == ch_id_str:
            return item
    return None


def _apply_decision_rules(
    issue_type: str,
    category: str,
    current_action: str,
    purpose_clarity: float,
    primary_jobs: list[str],
    emotional_density: float,
    is_dragging: bool,
    repetition_heat: float,
    heat_level: str,
    has_related: bool,
    project_type: str,
    guidance_mode: str,
) -> dict[str, Any]:
    """Apply decision rules. Returns action, confidence, explanation, alternatives."""
    alternatives: list[dict[str, str]] = []
    intentional_jobs = {"reinforce_theme", "deliver_reflection", "deepen_character", "build_setup"}
    has_intentional_job = bool(intentional_jobs & set(primary_jobs))

    if guidance_mode == "freeform":
        return {
            "action": current_action,
            "confidence": 0.5,
            "explanation": "In freeform mode, we suggest the detected action but leave the choice to you.",
            "alternatives": [
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If this is deliberate."},
            ],
            "revision_task_suggestion": f"Review: {issue_type.replace('_', ' ')}",
        }

    if issue_type == "repetition_in_chapter" or (category == "repetition" and heat_level in ("high", "very_high")):
        return {
            "action": "compress",
            "confidence": 0.85,
            "explanation": "This section appears to repeat an earlier beat without much new movement. State the point once clearly.",
            "alternatives": [
                {"action": "trim", "label": "Trim options", "when_to_consider": "If the repeated material adds no value."},
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If repetition is a deliberate refrain or motif."},
            ],
            "revision_task_suggestion": "Compress repeated points in this chapter",
        }

    if issue_type == "thin_transition" or category == "weak_transition":
        return {
            "action": "bridge",
            "confidence": 0.8,
            "explanation": "This section may benefit from one bridging beat rather than a full rewrite.",
            "alternatives": [
                {"action": "expand", "label": "Strengthen options", "when_to_consider": "If the chapter needs more than a brief bridge."},
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If the abrupt shift is deliberate."},
            ],
            "revision_task_suggestion": "Add bridge at chapter opening",
        }

    if issue_type == "thin_section" or category == "thin_support":
        if purpose_clarity < 0.4:
            return {
                "action": "expand",
                "confidence": 0.75,
                "explanation": "This moment may need more buildup to land fully. Expand to develop the idea or merge with an adjacent section.",
                "alternatives": [
                    {"action": "merge", "label": "Trim options", "when_to_consider": "If it fits better with the next chapter."},
                    {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If it's a deliberate brief bridge."},
                ],
                "revision_task_suggestion": "Expand or merge thin section",
            }
        return {
            "action": "expand",
            "confidence": 0.7,
            "explanation": "This moment may need more buildup to land fully. Consider expanding or merging with an adjacent chapter.",
            "alternatives": [
                {"action": "merge", "label": "Trim options", "when_to_consider": "If it fits better with the next chapter."},
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If it's a deliberate brief bridge."},
            ],
            "revision_task_suggestion": "Expand or merge thin section",
        }

    if issue_type in ("repeated_concepts", "repeated_reflection", "repeated_emotional_beat") or (category == "repetition" and has_related):
        return {
            "action": "compress",
            "confidence": 0.8,
            "explanation": "This section appears to repeat an earlier beat without much new movement. Consolidate into one stronger statement.",
            "alternatives": [
                {"action": "merge", "label": "Trim options", "when_to_consider": "If the sections can be combined."},
                {"action": "trim", "label": "Trim options", "when_to_consider": "If some instances add no value."},
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If it's a deliberate refrain."},
            ],
            "revision_task_suggestion": "Consolidate repeated content across chapters",
        }

    if issue_type in ("missing_example", "missing_exercise") or category == "practical_support_gap":
        return {
            "action": "strengthen",
            "confidence": 0.85,
            "explanation": "This moment may need more support. Add an example, exercise, or action step.",
            "alternatives": [
                {"action": "expand", "label": "Strengthen options", "when_to_consider": "If you want to add more than one example."},
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If abstract by design."},
            ],
            "revision_task_suggestion": "Add example or exercise to support concept",
        }

    if issue_type in ("exposition_overload", "possible_bloat", "excessive_explanation") or category in ("bloated_scene", "over_explanation"):
        # Prefer keep_as_intentional for reflective, emotional, thematic, or literary passages
        if (has_intentional_job and purpose_clarity >= 0.6) or emotional_density >= 0.5:
            return {
                "action": "keep_as_intentional",
                "confidence": 0.6,
                "explanation": "This passage may be strongly weighted. Consider keeping if the reflective pace is deliberate.",
                "alternatives": [
                    {"action": "compress", "label": "Trim options", "when_to_consider": "If some passages can be tightened."},
                    {"action": "trim", "label": "Trim options", "when_to_consider": "If it still feels long after reflection."},
                ],
                "revision_task_suggestion": "Review: keep or compress reflective passage",
            }
        if is_dragging:
            return {
                "action": "trim",
                "confidence": 0.8,
                "explanation": "This chapter may be doing less than its size suggests. Trim redundant or low-value passages.",
                "alternatives": [
                    {"action": "compress", "label": "Trim options", "when_to_consider": "If you prefer tightening over cutting."},
                    {"action": "strengthen", "label": "Strengthen options", "when_to_consider": "If the issue is thin content, not bloat."},
                ],
                "revision_task_suggestion": "Trim or compress dragging passages",
            }
        return {
            "action": "compress",
            "confidence": 0.75,
            "explanation": "This passage may be stronger if compressed. Compress exposition or convert key information into scene.",
            "alternatives": [
                {"action": "trim", "label": "Trim options", "when_to_consider": "If cutting is cleaner."},
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If reflective pace is deliberate."},
            ],
            "revision_task_suggestion": "Compress exposition or trim",
        }

    if issue_type == "bloated_intro_or_outro":
        # Contemplative nonfiction, memoir often have substantial intro/outro by design
        if has_intentional_job or emotional_density >= 0.4:
            return {
                "action": "keep_as_intentional",
                "confidence": 0.55,
                "explanation": "This intro/outro may be deliberately substantial. Consider keeping if it sets tone or delivers meaning.",
                "alternatives": [
                    {"action": "trim", "label": "Trim options", "when_to_consider": "If some passages can be cut."},
                    {"action": "compress", "label": "Trim options", "when_to_consider": "If you prefer tightening."},
                ],
                "revision_task_suggestion": "Review: keep or trim intro/outro",
            }
        return {
            "action": "trim",
            "confidence": 0.8,
            "explanation": "This chapter may be doing less than its size suggests. Intro/outro chapters often benefit from trimming to essentials.",
            "alternatives": [
                {"action": "compress", "label": "Trim options", "when_to_consider": "If you prefer tightening over cutting."},
                {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If length is deliberate."},
            ],
            "revision_task_suggestion": "Trim intro/outro to essentials",
        }

    if issue_type == "weak_midpoint" or category == "underweighted_payoff":
        return {
            "action": "strengthen",
            "confidence": 0.75,
            "explanation": "This moment may need more buildup to land fully. Strengthen with more setup, consequence, or emotional weight.",
            "alternatives": [
                {"action": "expand", "label": "Strengthen options", "when_to_consider": "If it needs significant new content."},
                {"action": "bridge", "label": "Strengthen options", "when_to_consider": "If the issue is transition, not payoff."},
            ],
            "revision_task_suggestion": "Strengthen midpoint or payoff beat",
        }

    if category == "rushed_moment":
        return {
            "action": "strengthen",
            "confidence": 0.8,
            "explanation": "This moment may need more buildup to land fully. Add consequence, reflection, or escalation.",
            "alternatives": [
                {"action": "expand", "label": "Strengthen options", "when_to_consider": "If it needs more scene."},
                {"action": "bridge", "label": "Strengthen options", "when_to_consider": "If the issue is transition."},
            ],
            "revision_task_suggestion": "Strengthen rushed moment",
        }

    if has_related and category in ("repetition", "instructional_redundancy"):
        return {
            "action": "merge",
            "confidence": 0.7,
            "explanation": "This section may be better merged. Two similar sections may work better as one.",
            "alternatives": [
                {"action": "compress", "label": "Trim options", "when_to_consider": "If merging isn't practical."},
                {"action": "trim", "label": "Trim options", "when_to_consider": "If one section adds no value."},
            ],
            "revision_task_suggestion": "Consider merging with related section",
        }

    return {
        "action": current_action,
        "confidence": 0.65,
        "explanation": f"Based on the detected issue, we suggest {current_action}. Review the alternatives if unsure.",
        "alternatives": [
            {"action": "keep_as_intentional", "label": "Mark as intentional", "when_to_consider": "If this is deliberate."},
            {"action": "trim", "label": "Trim options", "when_to_consider": "If the section adds little value."},
            {"action": "strengthen", "label": "Strengthen options", "when_to_consider": "If the issue is thin support, not bloat."},
        ],
        "revision_task_suggestion": f"Review: {issue_type.replace('_', ' ')}",
    }


def get_alternatives_comparison(
    issue: dict[str, Any],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return a comparison of alternative repair paths for the issue."""
    decision = decide_action(issue, context)
    rec = decision["recommended_action"]
    alts = decision.get("alternatives", [])

    out = [{"action": rec, "label": rec.replace("_", " ").title(), "is_recommended": True}]
    for a in alts:
        act = a.get("action", "")
        if act != rec:
            out.append({
                "action": act,
                "label": a.get("label", act.replace("_", " ").title()),
                "when_to_consider": a.get("when_to_consider", ""),
                "is_recommended": False,
            })
    return out
