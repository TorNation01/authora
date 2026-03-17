"""Chapter drag analysis for the Story Density Engine.

Detects consecutive sections/chapters that drag (low movement for their size),
merge candidates, and compression candidates.

Artistic-freedom: memoir and literary fiction use higher drag thresholds to avoid
punishing intentional slowness, reflection, and atmospheric pacing.
"""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.density.constants import (
    DRAG_SCORE_THRESHOLD_FLEXIBLE,
    DRAG_SCORE_THRESHOLD_GUIDED,
    DRAG_SCORE_THRESHOLD_MEMOIR,
    DRAG_SCORE_THRESHOLD_LITERARY,
)


def _drag_threshold(project_type: str, guidance_mode: str = "flexible") -> float:
    """Drag score above which we flag. Higher = more tolerant of slow pacing."""
    if project_type == "memoir":
        return DRAG_SCORE_THRESHOLD_MEMOIR  # 0.75 - poetic memoir, reflective
    if project_type == "fiction" and guidance_mode == "flexible":
        return DRAG_SCORE_THRESHOLD_LITERARY  # 0.78 - literary fiction, slow-burn
    if guidance_mode == "flexible":
        return DRAG_SCORE_THRESHOLD_FLEXIBLE
    return DRAG_SCORE_THRESHOLD_GUIDED


def analyze_chapter_drag(
    chapters: list[dict[str, Any]],
    density_by_chapter: list[dict[str, Any]],
    project_type: str = "fiction",
    guidance_mode: str = "flexible",
) -> dict[str, Any]:
    """Analyze chapter drag across consecutive sections."""
    total = len(chapters)
    if total < 1:
        return {
            "drag_runs": [],
            "merge_candidates": [],
            "compression_candidates": [],
            "chapter_drag_scores": [],
        }

    drag_threshold = _drag_threshold(project_type, guidance_mode)

    all_texts = [tiptap_to_plain_text(ch.get("content") or {}) for ch in chapters]
    word_counts = [len(t.split()) for t in all_texts]

    chapter_scores: list[dict[str, Any]] = []
    for i in range(total):
        text = all_texts[i]
        wc = word_counts[i]
        movement = _assess_movement(text, wc)
        info_density = _get_density(density_by_chapter, i, "information_density", 0.5)
        drag_score = _compute_drag_score(wc, movement, info_density, i, total)
        chapter_scores.append({
            "chapter_index": i,
            "chapter_id": str(chapters[i].get("id", "")),
            "title": chapters[i].get("title", "Untitled"),
            "word_count": wc,
            "movement": movement,
            "information_density": info_density,
            "drag_score": drag_score,
            "is_dragging": drag_score > drag_threshold,
        })

    drag_runs = _find_drag_runs(chapter_scores)
    merge_candidates = _find_merge_candidates(chapters, chapter_scores, all_texts)
    compression_candidates = _find_compression_candidates(chapter_scores)

    return {
        "drag_runs": drag_runs,
        "merge_candidates": merge_candidates,
        "compression_candidates": compression_candidates,
        "chapter_drag_scores": chapter_scores,
    }


def _assess_movement(text: str, word_count: int) -> float:
    """0-1: plot/narrative movement."""
    if not text or word_count < 50:
        return 0.2
    lower = text.lower()
    markers = ["then", "next", "after", "when", "decided", "went", "came", "left", "arrived", "discovered", "realized"]
    count = sum(1 for m in markers if m in lower)
    return min(0.9, 0.3 + count * 0.08)


def _get_density(density_by_chapter: list[dict], index: int, key: str, default: float) -> float:
    """Get value from density_by_chapter for chapter index."""
    for d in density_by_chapter:
        if d.get("chapter_index") == index:
            return d.get(key, default)
    return default


def _compute_drag_score(word_count: int, movement: float, info_density: float, index: int, total: int) -> float:
    """0-1: higher = more drag. Long + low movement + low density = high drag."""
    if word_count < 200:
        return 0.2
    base = (1 - movement) * 0.4 + (1 - info_density) * 0.3
    if word_count > 3000:
        base += 0.2
    elif word_count > 1500:
        base += 0.1
    if 0.3 <= index / max(1, total) <= 0.7 and base > 0.4:
        base += 0.1
    return min(1.0, base)


def _find_drag_runs(chapter_scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find consecutive chapters that are dragging."""
    runs: list[dict[str, Any]] = []
    current_run: list[int] = []

    for i, cs in enumerate(chapter_scores):
        if cs.get("is_dragging"):
            current_run.append(i)
        else:
            if len(current_run) >= 2:
                runs.append({
                    "chapter_indices": current_run.copy(),
                    "chapter_ids": [chapter_scores[j].get("chapter_id", "") for j in current_run],
                    "titles": [chapter_scores[j].get("title", "Untitled") for j in current_run],
                    "total_words": sum(chapter_scores[j].get("word_count", 0) for j in current_run),
                    "suggestion": "Consider trimming or tightening these consecutive chapters.",
                })
            current_run = []
    if len(current_run) >= 2:
        runs.append({
            "chapter_indices": current_run,
            "chapter_ids": [chapter_scores[j].get("chapter_id", "") for j in current_run],
            "titles": [chapter_scores[j].get("title", "Untitled") for j in current_run],
            "total_words": sum(chapter_scores[j].get("word_count", 0) for j in current_run),
            "suggestion": "Consider trimming or tightening these consecutive chapters.",
        })
    return runs


def _find_merge_candidates(
    chapters: list[dict[str, Any]],
    chapter_scores: list[dict[str, Any]],
    all_texts: list[str],
) -> list[dict[str, Any]]:
    """Find pairs of consecutive short chapters that could be merged."""
    candidates: list[dict[str, Any]] = []
    for i in range(len(chapters) - 1):
        wc1 = chapter_scores[i].get("word_count", 0)
        wc2 = chapter_scores[i + 1].get("word_count", 0)
        if wc1 < 800 and wc2 < 800 and wc1 + wc2 < 2500:
            overlap = _word_overlap(all_texts[i], all_texts[i + 1])
            if overlap > 0.02:
                candidates.append({
                    "chapter_indices": [i, i + 1],
                    "chapter_ids": [
                        chapter_scores[i].get("chapter_id", ""),
                        chapter_scores[i + 1].get("chapter_id", ""),
                    ],
                    "titles": [
                        chapter_scores[i].get("title", "Untitled"),
                        chapter_scores[i + 1].get("title", "Untitled"),
                    ],
                    "word_counts": [wc1, wc2],
                    "combined_words": wc1 + wc2,
                    "suggestion": "These short chapters may work better merged.",
                })
    return candidates


def _word_overlap(text1: str, text2: str) -> float:
    """Fraction of text2 words that appear in text1."""
    if not text1 or not text2:
        return 0.0
    w1 = set(text1.lower().split())
    w2 = text2.lower().split()
    if not w2:
        return 0.0
    return len([w for w in w2 if w in w1]) / len(w2)


def _find_compression_candidates(chapter_scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find chapters that likely need compression (long + low density)."""
    candidates: list[dict[str, Any]] = []
    for cs in chapter_scores:
        wc = cs.get("word_count", 0)
        density = cs.get("information_density", 0.5)
        drag = cs.get("drag_score", 0)
        if wc > 2500 and density < 0.55 and drag > 0.5:
            candidates.append({
                "chapter_index": cs.get("chapter_index"),
                "chapter_id": cs.get("chapter_id", ""),
                "title": cs.get("title", "Untitled"),
                "word_count": wc,
                "information_density": density,
                "suggestion": "This chapter may benefit from compression.",
            })
    return candidates
