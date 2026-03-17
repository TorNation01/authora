"""Repetition analysis for the Story Density Engine.

Provides repetition heat per chapter, repeated points/beats, and cross-chapter overlap.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from authora.services.export import tiptap_to_plain_text


def analyze_repetition(
    chapters: list[dict[str, Any]],
    repeated_concepts: list[dict[str, Any]],
    repeated_beats: list[dict[str, Any]],
) -> dict[str, Any]:
    """Analyze repetition across manuscript with per-chapter heat."""
    all_texts = [tiptap_to_plain_text(ch.get("content") or {}) for ch in chapters]
    total = len(chapters)

    chapter_heat: list[dict[str, Any]] = []
    for i in range(total):
        text = all_texts[i]
        in_chapter = _chapter_repetition_score(text)
        cross_chapter = _cross_chapter_repetition_share(text, all_texts, i)
        heat = (in_chapter * 0.6 + cross_chapter * 0.4)
        chapter_heat.append({
            "chapter_index": i,
            "chapter_id": str(chapters[i].get("id", "")),
            "title": chapters[i].get("title", "Untitled"),
            "word_count": len(text.split()) if text else 0,
            "in_chapter_repetition": in_chapter,
            "cross_chapter_overlap": cross_chapter,
            "repetition_heat": min(1.0, heat),
            "heat_level": _heat_level(heat),
        })

    repeated_points = _extract_repeated_points(all_texts, repeated_concepts)
    repeated_beat_chapters = _map_beats_to_chapters(repeated_beats)

    return {
        "chapter_repetition_heat": chapter_heat,
        "repeated_points": repeated_points,
        "repeated_beat_chapters": repeated_beat_chapters,
        "manuscript_repetition_score": _manuscript_repetition_score(chapter_heat),
    }


def _chapter_repetition_score(text: str) -> float:
    """0-1: higher = more repetition within chapter."""
    if not text or len(text) < 100:
        return 0.0
    words = [w.lower() for w in text.split() if len(w) > 3]
    if len(words) < 50:
        return 0.0
    counts = Counter(words)
    total = len(words)
    top = sum(c for _, c in counts.most_common(15))
    return min(1.0, top / total * 1.5)


def _cross_chapter_repetition_share(text: str, all_texts: list[str], index: int) -> float:
    """0-1: how much of this chapter's phrasing appears in other chapters."""
    if not text or len(text) < 100:
        return 0.0
    words = set(w.lower() for w in text.split() if len(w) > 4)
    if not words:
        return 0.0
    other_texts = [all_texts[j] for j in range(len(all_texts)) if j != index]
    if not other_texts:
        return 0.0
    other_words = set()
    for t in other_texts:
        other_words.update(w.lower() for w in t.split() if len(w) > 4)
    overlap = len(words & other_words) / max(1, len(words))
    return min(1.0, overlap * 2)


def _heat_level(heat: float) -> str:
    """low, moderate, high, very_high."""
    if heat < 0.25:
        return "low"
    if heat < 0.5:
        return "moderate"
    if heat < 0.75:
        return "high"
    return "very_high"


def _extract_repeated_points(
    all_texts: list[str],
    repeated_concepts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build list of repeated points with chapter references."""
    points: list[dict[str, Any]] = []
    for rc in repeated_concepts[:20]:
        phrase = rc.get("phrase", "")
        occ = rc.get("occurrences", 0)
        if not phrase or occ < 2:
            continue
        chapters_where: list[int] = []
        for i, text in enumerate(all_texts):
            if text and phrase in text.lower():
                chapters_where.append(i)
        points.append({
            "phrase": phrase,
            "occurrences": occ,
            "chapter_indices": chapters_where,
        })
    return points


def _map_beats_to_chapters(repeated_beats: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map repeated emotional beats to structure."""
    return [
        {"hint": b.get("hint", ""), "occurrences": b.get("occurrences", 0)}
        for b in repeated_beats
    ]


def _manuscript_repetition_score(chapter_heat: list[dict[str, Any]]) -> float:
    """0-100: lower = more repetition (worse). Inverse of average heat for scoring."""
    if not chapter_heat:
        return 80.0
    avg = sum(h.get("repetition_heat", 0) for h in chapter_heat) / len(chapter_heat)
    return max(0, min(100, 100 - avg * 60))
