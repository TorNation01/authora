"""Nonfiction density detector - repeated points, bloated explanation, weak support."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.density.constants import (
    INTRO_OUTRO_WORDS_FLEXIBLE,
    INTRO_OUTRO_WORDS_GUIDED,
)
from authora.services.density.detectors.base import BaseDensityDetector


class NonfictionDensityDetector(BaseDensityDetector):
    """Detect nonfiction density issues: repeated points, bloated explanation, weak examples."""

    project_type = "nonfiction"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []
        total = len(self.chapters)

        for i, ch in enumerate(self.chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")
            lower = (text or "").lower()

            # Example markers
            has_example = any(m in lower for m in ["for example", "for instance", "consider", "imagine", "suppose"])
            # Practical/takeaway markers
            has_takeaway = any(m in lower for m in ["takeaway", "action step", "try this", "you can", "here's how"])

            # Weak support: concept-heavy chapter without example
            # Skip contemplative/reflective chapters (may be intentionally abstract)
            if word_count > 400 and not has_example:
                contemplative_markers = ["reflect", "consider", "meaning", "contemplate", "meditate", "pause"]
                if any(m in lower for m in contemplative_markers):
                    continue
                concept_markers = ["concept", "idea", "principle", "theory", "approach", "method"]
                has_concept = any(m in lower for m in concept_markers)
                if has_concept and not self._softer_in_flexible():
                    issues.append(
                        self._issue(
                            "missing_example",
                            "practical_support_gap",
                            "expand",
                            "low",
                            f"Chapter may need example: {title}",
                            "This chapter introduces concepts but may benefit from a concrete example.",
                            chapter_id=chapter_id,
                            fix_suggestions=[
                                {"action": "expand", "label": "Add a concrete example"},
                                {"action": "mark_intentional", "label": "Mark as intentional"},
                            ],
                            confidence=0.5,
                        )
                    )

            # Bloated intro/outro (contemplative nonfiction often has substantial intro)
            intro_outro_threshold = INTRO_OUTRO_WORDS_FLEXIBLE if self._softer_in_flexible() else INTRO_OUTRO_WORDS_GUIDED
            if (i == 0 or i == total - 1) and word_count > intro_outro_threshold:
                issues.append(
                    self._issue(
                        "bloated_intro_or_outro",
                        "over_explanation",
                        "trim",
                        "low",
                        f"Long intro/outro: {title}",
                        "This chapter is long. Consider trimming to essential points.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "trim", "label": "Trim to essential points"},
                            {"action": "mark_intentional", "label": "Mark as intentional"},
                        ],
                        confidence=0.5,
                    )
                )

        return issues
