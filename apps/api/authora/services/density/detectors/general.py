"""General density detector - clutter, filler, repetition, thin support."""

from __future__ import annotations

from collections import Counter
from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.density.constants import (
    REPETITION_SCORE_THRESHOLD_FLEXIBLE,
    REPETITION_SCORE_THRESHOLD_GUIDED,
    THIN_SECTION_WORDS_FLEXIBLE,
    THIN_SECTION_WORDS_GUIDED,
    BLOAT_WORDS_FLEXIBLE,
    BLOAT_WORDS_GUIDED,
)
from authora.services.density.detectors.base import (
    BaseDensityDetector,
    _is_likely_intentional_style,
)


class GeneralDensityDetector(BaseDensityDetector):
    """Detect general density issues: repetition, clutter, thin support, drag."""

    def detect(self) -> list[dict[str, Any]]:
        issues = []
        density_by_chapter = self.density_map.get("density_by_chapter", [])
        repeated_concepts = self.density_map.get("repeated_concepts", [])
        thin_transitions = self.density_map.get("thin_transitions", [])
        total = len(self.chapters)

        for i, ch in enumerate(self.chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")

            # Repetition: high word repeat in same chapter
            if word_count > 300 and not self._suppress_in_freeform():
                repeat_score = _chapter_repetition_score(text)
                threshold = REPETITION_SCORE_THRESHOLD_FLEXIBLE if self._softer_in_flexible() else REPETITION_SCORE_THRESHOLD_GUIDED
                if repeat_score > threshold:
                    # Skip if likely intentional (refrain, motif, poetic repetition)
                    if _is_likely_intentional_style(self.density_map, i, chapter_id=chapter_id):
                        continue
                    issues.append(
                        self._issue(
                            "repetition_in_chapter",
                            "repetition",
                            "compress",
                            "low",
                            f"Possible repetition: {title}",
                            "This chapter may contain repeated phrases or ideas. Consider compressing.",
                            chapter_id=chapter_id,
                            fix_suggestions=[
                                {"action": "compress", "label": "Compress repeated points into one"},
                                {"action": "mark_intentional", "label": "Mark as intentional (deliberate repetition)"},
                            ],
                            confidence=0.6,
                        )
                    )

            # Thin chapter: very short middle chapter
            thin_threshold = THIN_SECTION_WORDS_FLEXIBLE if self._softer_in_flexible() else THIN_SECTION_WORDS_GUIDED
            if word_count < thin_threshold and i not in (0, total - 1) and not self._softer_in_flexible():
                issues.append(
                    self._issue(
                        "thin_section",
                        "thin_support",
                        "expand",
                        "low",
                        f"Thin section: {title}",
                        "This section is very short. Consider expanding or merging.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "expand", "label": "Add content or merge with adjacent chapter"},
                            {"action": "mark_intentional", "label": "Mark as intentional (brief bridge)"},
                        ],
                        confidence=0.7,
                    )
                )

            # Overlong chapter: possible bloat
            bloat_threshold = BLOAT_WORDS_FLEXIBLE if self._softer_in_flexible() else BLOAT_WORDS_GUIDED
            if word_count > bloat_threshold and not self._suppress_in_freeform():
                d = next((x for x in density_by_chapter if x.get("chapter_index") == i), {})
                info_density = d.get("information_density", 0.5)
                # Skip if likely intentional (atmospheric, literary, worldbuilding)
                if _is_likely_intentional_style(self.density_map, i, chapter_id=chapter_id):
                    continue
                if info_density < 0.5:
                    issues.append(
                        self._issue(
                            "possible_bloat",
                            "bloated_scene",
                            "trim",
                            "low",
                            f"Chapter may be overlong: {title}",
                            "This chapter is long with relatively low information density. Consider trimming.",
                            chapter_id=chapter_id,
                            fix_suggestions=[
                                {"action": "trim", "label": "Trim redundant or low-value passages"},
                                {"action": "compress", "label": "Compress exposition or description"},
                                {"action": "mark_intentional", "label": "Mark as intentional"},
                            ],
                            confidence=0.5,
                        )
                    )

        # Thin transitions
        for ch_idx in thin_transitions:
            if ch_idx < len(self.chapters) and not self._suppress_in_freeform():
                ch = self.chapters[ch_idx]
                chapter_id = str(ch.get("id", ""))
                title = ch.get("title", "Untitled")
                issues.append(
                    self._issue(
                        "thin_transition",
                        "weak_transition",
                        "bridge",
                        "low",
                        f"Thin transition into: {title}",
                        "This chapter may need a stronger bridge from the previous one.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "bridge", "label": "Add a bridging paragraph or scene"},
                            {"action": "mark_intentional", "label": "Mark as intentional (deliberate jump)"},
                        ],
                        confidence=0.6,
                    )
                )

        # Repeated concepts across manuscript (flexible: require more to reduce false positives)
        min_concepts = 5 if self._softer_in_flexible() else 3
        if repeated_concepts and len(repeated_concepts) >= min_concepts:
            issues.append(
                self._issue(
                    "repeated_concepts",
                    "repetition",
                    "compress",
                    "low",
                    "Repeated concepts across manuscript",
                    "Several phrases or concepts appear in multiple chapters. Consider consolidating.",
                    fix_suggestions=[
                        {"action": "compress", "label": "Consolidate repeated points"},
                        {"action": "mark_intentional", "label": "Mark as intentional (deliberate refrain)"},
                    ],
                    confidence=0.5,
                )
            )

        return issues


def _chapter_repetition_score(text: str) -> float:
    """0-1: higher = more repetition within chapter."""
    if not text or len(text) < 100:
        return 0.0
    words = [w.lower() for w in text.split() if len(w) > 3]
    if len(words) < 50:
        return 0.0
    counts = Counter(words)
    total = len(words)
    top5 = sum(c for _, c in counts.most_common(10))
    return top5 / total
