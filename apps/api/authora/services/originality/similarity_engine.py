"""Similarity engine: n-gram fingerprinting for internal comparison.

This is NOT a substitute for institutional plagiarism detection.
Results are review aids only. Human review is central.
"""

import re
from dataclasses import dataclass
from typing import Any

from authora.services.export import tiptap_to_plain_text

NGRAM_SIZE = 5
MIN_MATCH_LEN = 20


@dataclass
class MatchResult:
    query_chapter_id: str | None
    query_text: str
    matched_text: str
    source_type: str
    source_id: str | None
    source_label: str | None
    match_type: str
    similarity_pct: float
    query_start: int | None
    query_end: int | None


def _normalize(text: str) -> str:
    """Normalize text for comparison."""
    text = re.sub(r"\s+", " ", text.lower().strip())
    return re.sub(r"[^\w\s]", "", text)


def _ngrams(text: str, n: int = NGRAM_SIZE) -> set[str]:
    """Extract character n-grams from normalized text."""
    norm = _normalize(text)
    if len(norm) < n:
        return set()
    return {norm[i : i + n] for i in range(len(norm) - n + 1)}


def _compute_similarity(text_a: str, text_b: str) -> float:
    """Jaccard similarity of n-gram sets. Returns 0-1."""
    ga = _ngrams(text_a)
    gb = _ngrams(text_b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def _find_overlap_regions(query: str, corpus_text: str, min_len: int = MIN_MATCH_LEN) -> list[tuple[int, int, str]]:
    """Find overlapping regions (sliding window). Returns (start, end, matched_substring)."""
    q_norm = _normalize(query)
    c_norm = _normalize(corpus_text)
    if len(q_norm) < min_len or len(c_norm) < min_len:
        return []
    results = []
    for i in range(len(q_norm) - min_len + 1):
        for window_len in range(min_len, min(len(q_norm) - i + 1, 100)):
            sub = q_norm[i : i + window_len]
            if sub in c_norm:
                idx = c_norm.index(sub)
                orig = corpus_text[idx : idx + window_len] if idx < len(corpus_text) else sub
                results.append((i, i + window_len, orig))
    return results


def extract_plain_text_from_chapters(chapters: list[dict[str, Any]]) -> list[tuple[str, str, dict]]:
    """Extract plain text from chapter data. Returns [(chapter_id, text, meta), ...]."""
    out = []
    for ch in chapters:
        cid = str(ch.get("id", ""))
        content = ch.get("content", {})
        text = tiptap_to_plain_text(content) if content else ""
        meta = {"title": ch.get("title", ""), "sort_order": ch.get("sort_order", 0)}
        out.append((cid, text, meta))
    return out


def compare_against_corpus(
    query_chapters: list[tuple[str, str, dict]],
    corpus_chapters: list[tuple[str, str, dict]],
    *,
    exclude_ranges: list[dict[str, Any]] | None = None,
    min_similarity: float = 0.5,
) -> list[MatchResult]:
    """
    Compare query chapters against corpus chapters.
    Returns list of MatchResult. Does not claim perfect detection.
    """
    matches: list[MatchResult] = []
    for q_id, q_text, q_meta in query_chapters:
        if not q_text or len(q_text.strip()) < MIN_MATCH_LEN:
            continue
        for c_id, c_text, c_meta in corpus_chapters:
            if q_id == c_id:
                continue
            if not c_text or len(c_text.strip()) < MIN_MATCH_LEN:
                continue
            sim = _compute_similarity(q_text, c_text)
            if sim >= min_similarity:
                overlap_regions = _find_overlap_regions(q_text, c_text)
                for start, end, matched in overlap_regions[:5]:
                    matches.append(
                        MatchResult(
                            query_chapter_id=q_id,
                            query_text=q_text[start:end],
                            matched_text=matched,
                            source_type="project",
                            source_id=c_id,
                            source_label=c_meta.get("title", "Chapter"),
                            match_type="exact" if sim > 0.9 else "paraphrase_like",
                            similarity_pct=round(sim * 100, 1),
                            query_start=start,
                            query_end=end,
                        )
                    )
    return matches


def compute_overall_similarity(matches: list[MatchResult], total_chars: int) -> float:
    """Compute overall similarity percentage from matches."""
    if total_chars <= 0:
        return 0.0
    matched_chars = sum((m.query_end or 0) - (m.query_start or 0) for m in matches)
    return min(100.0, round((matched_chars / total_chars) * 100, 1))
