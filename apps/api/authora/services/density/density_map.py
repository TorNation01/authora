"""Density map construction for manuscript analysis.

Models chapter purpose, information density, repetition, thin transitions,
and support gaps to determine what should be trimmed, compressed, strengthened,
or expanded.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.density.scene_purpose_analyzer import run_full_purpose_analysis
from authora.services.density.chapter_drag_analyzer import analyze_chapter_drag
from authora.services.density.repetition_analyzer import analyze_repetition


def build_density_map(
    chapters: list[dict[str, Any]],
    story_map: dict[str, Any],
) -> dict[str, Any]:
    """Build internal density map from manuscript and story map."""
    density_by_chapter: list[dict[str, Any]] = []
    repeated_concepts: list[dict[str, Any]] = []
    repeated_beats: list[dict[str, Any]] = []
    thin_transitions: list[int] = []
    underweighted_payoffs: list[dict[str, Any]] = []
    all_chapter_texts: list[str] = []
    word_freq_global: Counter[str] = Counter()

    total = len(chapters)
    for i, ch in enumerate(chapters):
        content = ch.get("content") or {}
        text = tiptap_to_plain_text(content)
        word_count = len(text.split()) if text else 0
        all_chapter_texts.append(text or "")

        if text:
            words = text.lower().split()
            word_freq_global.update(w for w in words if len(w) > 3)

        info_density = _assess_information_density(text, word_count)
        emotional_density = _assess_emotional_density(text)
        tension_density = _assess_tension_density(text)
        movement = _assess_movement(text, i, total)
        purpose = _infer_section_purpose(text, i, total, word_count)

        density_by_chapter.append({
            "chapter_index": i,
            "chapter_id": str(ch.get("id", "")),
            "title": ch.get("title", "Untitled"),
            "word_count": word_count,
            "information_density": info_density,
            "emotional_density": emotional_density,
            "tension_density": tension_density,
            "movement": movement,
            "purpose_hint": purpose,
            "is_midpoint": _is_midpoint(i, total),
        })

    # Cross-chapter: repeated concepts (same key phrases in multiple chapters)
    _find_repeated_concepts(all_chapter_texts, repeated_concepts)
    # Repeated emotional beats
    emotional_markers = story_map.get("emotional_markers", [])
    _find_repeated_emotional_beats(emotional_markers, repeated_beats)
    # Thin transitions (chapters with weak linkage to previous)
    _find_thin_transitions(all_chapter_texts, thin_transitions)
    # Underweighted payoffs (promises without fulfillment)
    promises = story_map.get("promises", [])
    _find_underweighted_payoffs(promises, total, underweighted_payoffs)

    manuscript_score = _compute_manuscript_density_score(
        density_by_chapter, len(repeated_concepts), len(thin_transitions)
    )

    project_type = story_map.get("project_type", "fiction")

    guidance_mode = story_map.get("guidance_mode", "flexible")
    purpose_analysis = run_full_purpose_analysis(chapters, project_type)
    drag_analysis = analyze_chapter_drag(
        chapters, density_by_chapter, project_type, guidance_mode
    )
    repetition_analysis = analyze_repetition(
        chapters, repeated_concepts, repeated_beats
    )

    return {
        "project_type": project_type,
        "guidance_mode": story_map.get("guidance_mode", "flexible"),
        "chapter_count": total,
        "total_word_count": sum(d["word_count"] for d in density_by_chapter),
        "manuscript_density_score": manuscript_score,
        "density_by_chapter": density_by_chapter,
        "repeated_concepts": repeated_concepts,
        "repeated_beats": repeated_beats,
        "thin_transitions": thin_transitions,
        "underweighted_payoffs": underweighted_payoffs,
        "word_freq_global": dict(word_freq_global.most_common(100)),
        "scene_purpose_analysis": purpose_analysis,
        "chapter_drag_analysis": drag_analysis,
        "repetition_analysis": repetition_analysis,
    }


def _assess_information_density(text: str, word_count: int) -> float:
    """0-1: balance of information (avoid overload or thin)."""
    if word_count < 50:
        return 0.3
    sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
    words_per_sentence = word_count / sentences if sentences else 0
    if 10 <= words_per_sentence <= 25:
        return 0.8
    if words_per_sentence < 8:
        return 0.5
    if words_per_sentence > 40:
        return 0.4
    return 0.7


def _assess_emotional_density(text: str) -> float:
    """0-1: emotional content level. Used to avoid flagging intentional emotional/reflective passages."""
    if not text or len(text) < 100:
        return 0.2
    lower = text.lower()
    markers = [
        "felt", "realized", "knew", "understood", "hope", "fear", "anger", "joy", "despair",
        "reflecting", "looking back", "in retrospect", "meaning", "silence", "quiet",
    ]
    count = sum(1 for m in markers if m in lower)
    return min(0.9, 0.3 + count * 0.08)


def _assess_tension_density(text: str) -> float:
    """0-1: tension/stakes level."""
    if not text or len(text) < 50:
        return 0.2
    lower = text.lower()
    markers = ["but", "however", "suddenly", "danger", "threat", "conflict", "risk", "must"]
    count = sum(1 for m in markers if m in lower)
    return min(0.9, 0.3 + count * 0.1)


def _assess_movement(text: str, index: int, total: int) -> float:
    """0-1: plot/narrative movement."""
    if not text or len(text) < 100:
        return 0.2
    lower = text.lower()
    markers = ["then", "next", "after", "when", "decided", "went", "came", "left", "arrived"]
    count = sum(1 for m in markers if m in lower)
    return min(0.9, 0.4 + count * 0.05)


def _infer_section_purpose(text: str, index: int, total: int, word_count: int) -> str:
    """Infer section purpose for density analysis."""
    if not text or len(text.strip()) < 50:
        return "unclear"
    if index == 0:
        return "opening"
    if index == total - 1:
        return "ending"
    if 0.4 <= index / max(1, total) <= 0.6:
        return "midpoint"
    if word_count < 150:
        return "bridge"
    # Detect reflective passages (used for artistic-freedom safeguards)
    lower = text.lower()
    if any(m in lower for m in ["reflecting", "looking back", "in retrospect", "i realized", "it occurred to me"]):
        return "reflection"
    return "body"


def _is_midpoint(index: int, total: int) -> bool:
    """True if chapter is in midpoint region (35-65%)."""
    if total < 3:
        return False
    return 0.35 <= index / total <= 0.65


def _find_repeated_concepts(texts: list[str], out: list[dict[str, Any]]) -> None:
    """Find concepts/phrases repeated across chapters."""
    # Simple: extract 3-5 word phrases that appear in 2+ chapters
    phrase_counts: Counter[str] = Counter()
    for text in texts:
        if not text or len(text) < 100:
            continue
        words = text.lower().split()
        for i in range(len(words) - 2):
            phrase = " ".join(words[i : i + 3])
            if len(phrase) > 15 and phrase.count(" ") == 2:
                phrase_counts[phrase] += 1
    for phrase, count in phrase_counts.items():
        if count >= 2:
            out.append({"phrase": phrase, "occurrences": count})


def _find_repeated_emotional_beats(
    emotional_markers: list[dict[str, Any]],
    out: list[dict[str, Any]],
) -> None:
    """Find emotional beats that repeat without progression."""
    hint_counts: Counter[str] = Counter()
    for m in emotional_markers:
        hint = m.get("hint", "")
        if hint:
            hint_counts[hint] += 1
    for hint, count in hint_counts.items():
        if count >= 3:
            out.append({"hint": hint, "occurrences": count})


def _find_thin_transitions(texts: list[str], out: list[int]) -> None:
    """Find chapters with thin transition from previous."""
    transition_markers = ["however", "therefore", "meanwhile", "later", "the next", "after", "when", "as"]
    for i in range(1, len(texts)):
        text = (texts[i] or "").lower()[:500]
        if not text or len(text) < 50:
            out.append(i)
            continue
        has_marker = any(m in text for m in transition_markers)
        prev_words = set((texts[i - 1] or "").lower().split())
        curr_words = set(text.split())
        overlap = len(prev_words & curr_words) / max(1, len(curr_words))
        if not has_marker and overlap < 0.05:
            out.append(i)


def _find_underweighted_payoffs(
    promises: list[dict[str, Any]],
    total: int,
    out: list[dict[str, Any]],
) -> None:
    """Find promises in first 2/3 with no clear payoff in last 1/3."""
    for p in promises:
        ch_idx = p.get("chapter_index", 0)
        if ch_idx < total * 2 // 3:
            # Would need to check last third for fulfillment - simplified: flag if many promises
            out.append({"chapter_index": ch_idx, "hint": p.get("hint", "")})


def _compute_manuscript_density_score(
    density_by_chapter: list[dict[str, Any]],
    repeated_count: int,
    thin_transition_count: int,
) -> float:
    """0-100: overall manuscript density health. Higher = better."""
    if not density_by_chapter:
        return 70.0
    avg_info = sum(d.get("information_density", 0.5) for d in density_by_chapter) / len(density_by_chapter)
    base = avg_info * 80
    base -= repeated_count * 3
    base -= thin_transition_count * 2
    return max(0, min(100, base))
