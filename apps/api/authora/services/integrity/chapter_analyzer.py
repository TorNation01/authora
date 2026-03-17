"""Chapter health, pacing, and structure analyzer."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text

CHAPTER_HEALTH_LEVELS = ("strong", "stable", "needs_support", "weak", "critical")


def analyze_chapters(
    chapters: list[dict[str, Any]],
    story_map: dict[str, Any],
    project_type: str = "fiction",
    guidance_mode: str = "flexible",
) -> list[dict[str, Any]]:
    """Analyze each chapter for health, pacing, structure, and purpose."""
    chapter_purposes = story_map.get("chapter_purposes", [])
    pacing_by_chapter = story_map.get("pacing_by_chapter", [])
    emotional_markers = story_map.get("emotional_markers", [])
    character_appearances = story_map.get("character_appearances", {})
    themes_mentioned = story_map.get("themes_mentioned", {})

    results: list[dict[str, Any]] = []
    total_chapters = len(chapters)

    for i, ch in enumerate(chapters):
        content = ch.get("content") or {}
        text = tiptap_to_plain_text(content)
        word_count = len(text.split()) if text else 0
        title = ch.get("title", "Untitled")
        chapter_id = str(ch.get("id", ""))

        purpose_data = next((p for p in chapter_purposes if p.get("chapter_index") == i), {})
        pacing_data = next((p for p in pacing_by_chapter if p.get("chapter_index") == i), {})

        purpose_clarity = _assess_purpose_clarity(text, title, i, total_chapters, purpose_data)
        relationship_to_manuscript = _assess_relationship(text, i, total_chapters, character_appearances, themes_mentioned)
        tension_level = _assess_tension(text, word_count)
        emotional_movement = _assess_emotional_movement(text, emotional_markers, i)
        plot_movement = _assess_plot_movement(text, i, total_chapters)
        information_density = _assess_information_density(text, word_count)
        pacing = _assess_pacing(word_count, i, total_chapters, pacing_data)
        transition_quality = _assess_transition_quality(text, i, total_chapters, chapters)
        opening_strength = _assess_opening_strength(text, i)
        closing_strength = _assess_closing_strength(text, i, total_chapters)
        chapter_linkage = _assess_chapter_linkage(text, i, total_chapters, chapters)
        repetition = _assess_repetition(text, chapters, i)
        unresolved_internal = _assess_unresolved_internal(text)

        health, health_reason = _compute_health(
            purpose_clarity=purpose_clarity,
            pacing=pacing,
            opening_strength=opening_strength,
            closing_strength=closing_strength,
            transition_quality=transition_quality,
            emotional_movement=emotional_movement,
            word_count=word_count,
            i=i,
            total=total_chapters,
        )

        what_this_chapter_is_doing = _summarize_what_chapter_is_doing(
            text, title, i, total_chapters, purpose_data, pacing_data
        )
        why_feels_off = _summarize_why_feels_off(
            health, health_reason, purpose_clarity, pacing, opening_strength,
            closing_strength, transition_quality, repetition
        )

        issues = _detect_chapter_issues(
            text, word_count, i, total_chapters, chapters,
            purpose_clarity, pacing, opening_strength, closing_strength,
            transition_quality, emotional_movement, repetition, chapter_id, title,
            project_type=project_type, guidance_mode=guidance_mode,
        )

        results.append({
            "chapter_id": chapter_id,
            "chapter_index": i,
            "title": title,
            "word_count": word_count,
            "health": health,
            "health_reason": health_reason,
            "purpose_clarity": purpose_clarity,
            "relationship_to_manuscript": relationship_to_manuscript,
            "tension_level": tension_level,
            "emotional_movement": emotional_movement,
            "plot_movement": plot_movement,
            "information_density": information_density,
            "pacing": pacing,
            "transition_quality": transition_quality,
            "opening_strength": opening_strength,
            "closing_strength": closing_strength,
            "chapter_linkage": chapter_linkage,
            "repetition": repetition,
            "unresolved_internal": unresolved_internal,
            "what_this_chapter_is_doing": what_this_chapter_is_doing,
            "why_feels_off": why_feels_off,
            "suggested_fixes": _suggest_fixes(health, issues),
            "issues": issues,
        })

    return results


def _score(lo: float, hi: float, val: float) -> float:
    """Map val to 0-1 score. Below lo=0, above hi=1, linear between."""
    if val <= lo:
        return 0.0
    if val >= hi:
        return 1.0
    return (val - lo) / (hi - lo)


def _assess_purpose_clarity(text: str, title: str, index: int, total: int, purpose_data: dict) -> float:
    """0-1: how clear is the chapter's purpose."""
    if not text or len(text.strip()) < 50:
        return 0.2
    purpose_hint = purpose_data.get("purpose_hint", "")
    if purpose_hint == "placeholder_or_empty":
        return 0.2
    word_count = len(text.split())
    if word_count < 100 and index not in (0, total - 1):
        return 0.4
    if purpose_hint in ("opening", "ending") and word_count >= 200:
        return 0.9
    if purpose_hint == "body" and word_count >= 300:
        return 0.8
    return 0.7


def _assess_relationship(text: str, index: int, total: int, char_apps: dict, themes: dict) -> float:
    """0-1: how connected to overall manuscript."""
    if not text or len(text) < 100:
        return 0.3
    chars_in_chapter = sum(1 for apps in char_apps.values() if index in apps)
    themes_in_chapter = sum(1 for apps in themes.values() if index in apps)
    if chars_in_chapter > 0 or themes_in_chapter > 0:
        return 0.8
    if index in (0, total - 1):
        return 0.7
    return 0.6


def _assess_tension(text: str, word_count: int) -> float:
    """0-1: tension/stakes level."""
    if not text or word_count < 50:
        return 0.2
    lower = text.lower()
    tension_markers = ["but", "however", "suddenly", "danger", "threat", "conflict", "stakes", "risk", "must", "had to"]
    count = sum(1 for m in tension_markers if m in lower)
    return min(0.9, 0.3 + count * 0.1)


def _assess_emotional_movement(text: str, emotional_markers: list, index: int) -> float:
    """0-1: emotional progression."""
    chapter_markers = [m for m in emotional_markers if m.get("chapter_index") == index]
    if chapter_markers:
        return 0.8
    if not text or len(text) < 200:
        return 0.3
    lower = text.lower()
    if any(m in lower for m in ["felt", "realized", "knew", "understood"]):
        return 0.7
    return 0.5


def _assess_plot_movement(text: str, index: int, total: int) -> float:
    """0-1: plot advancement."""
    if not text or len(text) < 100:
        return 0.2
    lower = text.lower()
    movement_markers = ["then", "next", "after", "before", "when", "decided", "went", "came", "left", "arrived"]
    count = sum(1 for m in movement_markers if m in lower)
    base = 0.4 + min(0.4, count * 0.05)
    if index == 0:
        return min(0.9, base + 0.2)
    return base


def _assess_information_density(text: str, word_count: int) -> float:
    """0-1: information density (avoid overload or thin)."""
    if word_count < 50:
        return 0.3
    sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
    words_per_sentence = word_count / sentences if sentences else 0
    if 10 <= words_per_sentence <= 25:
        return 0.8
    if words_per_sentence < 8:
        return 0.6
    if words_per_sentence > 40:
        return 0.5
    return 0.7


def _assess_pacing(word_count: int, index: int, total: int, pacing_data: dict) -> float:
    """0-1: pacing appropriateness."""
    hint = pacing_data.get("pacing_hint", "normal")
    if hint == "very_short":
        return 0.3
    if hint == "very_long":
        return 0.5
    if hint == "slow_opening" and index < total // 3:
        return 0.4
    if hint == "rushed_ending" and index > total * 2 // 3:
        return 0.4
    return 0.8


def _assess_transition_quality(text: str, index: int, total: int, chapters: list) -> float:
    """0-1: transition from previous chapter."""
    if index == 0:
        return 0.9
    if not text or len(text) < 50:
        return 0.3
    lower = text.lower()
    transition_markers = ["however", "therefore", "meanwhile", "later", "the next", "after", "when", "as"]
    if any(m in lower[:500] for m in transition_markers):
        return 0.8
    return 0.6


def _assess_opening_strength(text: str, index: int) -> float:
    """0-1: strength of chapter opening."""
    if not text or len(text) < 30:
        return 0.2
    first_para = text.split("\n\n")[0] if text else ""
    if len(first_para) < 20:
        return 0.4
    if len(first_para) >= 80:
        return 0.8
    return 0.7


def _assess_closing_strength(text: str, index: int, total: int) -> float:
    """0-1: strength of chapter closing."""
    if not text or len(text) < 50:
        return 0.3
    paras = text.split("\n\n")
    if not paras:
        return 0.4
    last_para = paras[-1].strip()
    if len(last_para) < 20:
        return 0.4
    if index == total - 1 and len(last_para) < 50:
        return 0.5
    return 0.75


def _assess_chapter_linkage(text: str, index: int, total: int, chapters: list) -> float:
    """0-1: linkage to adjacent chapters."""
    if index == 0 or index >= total - 1:
        return 0.8
    prev_ch = chapters[index - 1] if index > 0 else {}
    prev_text = tiptap_to_plain_text(prev_ch.get("content") or {})
    if not prev_text or len(prev_text) < 50:
        return 0.5
    prev_words = set(prev_text.lower().split())
    curr_words = set(text.lower().split())
    overlap = len(prev_words & curr_words) / max(1, len(curr_words))
    return min(0.9, 0.4 + overlap * 2)


def _assess_repetition(text: str, chapters: list, index: int) -> float:
    """0-1: 1 = high repetition (bad), 0 = low repetition (good). Inverted for 'quality'."""
    if not text or len(text) < 100:
        return 0.0
    words = text.lower().split()
    if len(words) < 20:
        return 0.0
    from collections import Counter
    counts = Counter(words)
    most_common = counts.most_common(5)
    repeat_score = sum(c for _, c in most_common) / max(1, len(words))
    return min(1.0, repeat_score * 3)


def _assess_unresolved_internal(text: str) -> float:
    """0-1: unresolved internal issues (questions, TODOs)."""
    if not text:
        return 0.0
    lower = text.lower()
    # High-confidence placeholders only; avoid "..." (ellipsis) and "?" (rhetorical questions)
    strong_markers = ["todo", "tbd", "[placeholder]", "[insert", "xxx", "[xxx]"]
    count = sum(1 for m in strong_markers if m in lower)
    return min(0.8, count * 0.3)


def _compute_health(
    purpose_clarity: float,
    pacing: float,
    opening_strength: float,
    closing_strength: float,
    transition_quality: float,
    emotional_movement: float,
    word_count: int,
    i: int,
    total: int,
) -> tuple[str, str]:
    """Compute overall health level and reason."""
    avg = (purpose_clarity + pacing + opening_strength + closing_strength + transition_quality + emotional_movement) / 6
    reasons: list[str] = []

    if purpose_clarity < 0.4:
        reasons.append("unclear purpose")
    if pacing < 0.4:
        reasons.append("pacing concerns")
    if opening_strength < 0.4:
        reasons.append("weak opening")
    if closing_strength < 0.4:
        reasons.append("weak closing")
    if transition_quality < 0.4:
        reasons.append("poor transition")
    if emotional_movement < 0.4:
        reasons.append("emotionally flat")
    if word_count < 50:
        reasons.append("very short")
    if word_count > 6000:
        reasons.append("very long")

    if avg >= 0.8 and not reasons:
        return "strong", "Chapter is well-structured and purposeful."
    if avg >= 0.65 and len(reasons) <= 1:
        return "stable", "Chapter is solid with minor room for improvement."
    if avg >= 0.5 or len(reasons) <= 2:
        return "needs_support", "; ".join(reasons) if reasons else "Could be strengthened."
    if avg >= 0.35 or len(reasons) <= 3:
        return "weak", "; ".join(reasons) if reasons else "Several areas need attention."
    return "critical", "; ".join(reasons) if reasons else "Significant structural issues."


def _summarize_what_chapter_is_doing(
    text: str, title: str, index: int, total: int,
    purpose_data: dict, pacing_data: dict,
) -> str:
    """Generate 'what this chapter is doing' summary."""
    purpose_hint = purpose_data.get("purpose_hint", "body")
    word_count = len(text.split()) if text else 0

    if purpose_hint == "placeholder_or_empty":
        return "This chapter is empty or placeholder content."
    if index == 0:
        return f"Opening chapter ({word_count} words). Sets up the story and reader expectations."
    if index == total - 1:
        return f"Closing chapter ({word_count} words). Brings the narrative to resolution."
    if purpose_hint == "short_section":
        return f"Short bridge or transition section ({word_count} words)."
    return f"Body chapter ({word_count} words). Advances the narrative."


def _summarize_why_feels_off(
    health: str,
    health_reason: str,
    purpose_clarity: float,
    pacing: float,
    opening_strength: float,
    closing_strength: float,
    transition_quality: float,
    repetition: float,
) -> str | None:
    """Generate 'why this chapter feels off' analysis."""
    if health in ("strong", "stable"):
        return None
    parts = [health_reason]
    if purpose_clarity < 0.5:
        parts.append("The chapter's purpose may be unclear.")
    if pacing < 0.5:
        parts.append("Pacing may feel off—too slow or too rushed.")
    if opening_strength < 0.5:
        parts.append("The opening could hook the reader more strongly.")
    if closing_strength < 0.5:
        parts.append("The ending may lack punch or transition.")
    if transition_quality < 0.5:
        parts.append("The link to the previous chapter could be smoother.")
    if repetition > 0.5:
        parts.append("Some repetition may dilute impact.")
    return " ".join(parts)


def _detect_chapter_issues(
    text: str,
    word_count: int,
    index: int,
    total: int,
    chapters: list,
    purpose_clarity: float,
    pacing: float,
    opening_strength: float,
    closing_strength: float,
    transition_quality: float,
    emotional_movement: float,
    repetition: float,
    chapter_id: str,
    title: str,
    project_type: str = "fiction",
    guidance_mode: str = "flexible",
) -> list[dict[str, Any]]:
    """Detect chapter-level issues for integrity engine. Mode-aware to reduce false positives."""
    issues: list[dict[str, Any]] = []

    # Freeform: suppress most speculative issues; keep only clear structural gaps
    if guidance_mode == "freeform":
        if word_count < 30:  # Truly empty
            issues.append({
                "type": "chapter_underwritten",
                "severity": "moderate",
                "title": f"Chapter has minimal content: {title}",
                "suggestion": "Add content or remove if intentional.",
            })
        return issues

    # Flexible: softer thresholds, higher bar for speculative issues
    flexible = guidance_mode == "flexible"
    purpose_thresh = 0.35 if flexible else 0.4
    pacing_thresh = 0.35 if flexible else 0.4
    emotion_thresh = 0.35 if flexible else 0.4
    transition_thresh = 0.35 if flexible else 0.4
    opening_thresh = 0.35 if flexible else 0.4
    closing_thresh = 0.35 if flexible else 0.4
    repetition_thresh = 0.7 if flexible else 0.6  # Higher bar for repetition flag

    if purpose_clarity < purpose_thresh:
        issues.append({
            "type": "chapter_lacks_clear_purpose",
            "severity": "moderate",
            "title": f"Chapter lacks clear purpose: {title}",
            "suggestion": "Clarify what this chapter accomplishes for the reader or story.",
        })
    if repetition > repetition_thresh:
        issues.append({
            "type": "chapter_repeats_prior_content",
            "severity": "low",
            "title": f"Possible repetition: {title}",
            "suggestion": "Review for redundant phrasing or repeated ideas.",
        })
    if pacing < pacing_thresh and index not in (0, total - 1):
        issues.append({
            "type": "chapter_stalls_momentum",
            "severity": "moderate",
            "title": f"Chapter may stall momentum: {title}",
            "suggestion": "Consider tightening or adding a beat that advances the story.",
        })
    # Overlong: only flag if very long; many genres use long chapters
    if word_count > 6000:
        issues.append({
            "type": "chapter_overlong",
            "severity": "low",
            "title": f"Chapter may be overlong: {title}",
            "suggestion": "Consider splitting or trimming.",
        })
    # Weak transition out: skip for last chapter (intentionally unresolved endings)
    if closing_strength < closing_thresh and index < total - 1:
        issues.append({
            "type": "chapter_ends_without_effective_transition",
            "severity": "moderate",
            "title": f"Weak transition out: {title}",
            "suggestion": "Add a stronger bridge to the next chapter.",
        })
    # Emotionally flat: skip for poetic/symbolic prose; higher word threshold
    if emotional_movement < emotion_thresh and word_count > 400:
        issues.append({
            "type": "chapter_emotionally_flat",
            "severity": "low",
            "title": f"Chapter may be emotionally flat: {title}",
            "suggestion": "Consider adding emotional beats or character reflection.",
        })
    if transition_quality < transition_thresh and index > 0:
        issues.append({
            "type": "chapter_disconnected_from_main_thread",
            "severity": "moderate",
            "title": f"Chapter may feel disconnected: {title}",
            "suggestion": "Strengthen the link to the previous chapter or main thread.",
        })
    # Placeholder-heavy: allow short bridge chapters
    if word_count < 80 and index not in (0, total - 1):
        issues.append({
            "type": "chapter_placeholder_heavy",
            "severity": "moderate",
            "title": f"Chapter has little content: {title}",
            "suggestion": "Expand or merge with an adjacent chapter.",
        })
    if word_count < 40:
        issues.append({
            "type": "chapter_underwritten",
            "severity": "high",
            "title": f"Chapter is underwritten: {title}",
            "suggestion": "Add substantial content or remove if intentional.",
        })
    if opening_strength < opening_thresh and word_count > 150:
        issues.append({
            "type": "chapter_weak_opening",
            "severity": "low",
            "title": f"Weak chapter opening: {title}",
            "suggestion": "Strengthen the opening hook or first paragraph.",
        })

    return issues


def _suggest_fixes(health: str, issues: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Generate suggested fixes from health and issues."""
    fixes: list[dict[str, str]] = []
    for iss in issues:
        fixes.append({
            "action": iss.get("type", "improve"),
            "label": iss.get("suggestion", "Review and strengthen this chapter."),
        })
    if not fixes and health in ("needs_support", "weak", "critical"):
        fixes.append({"action": "review", "label": "Read through and identify what feels off."})
    return fixes
