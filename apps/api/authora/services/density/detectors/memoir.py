"""Memoir density detector - repeated reflection, event retelling, emotional over-explanation."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.density.constants import (
    MEMOIR_REFLECTION_COUNT_FLEXIBLE,
    MEMOIR_REFLECTION_COUNT_GUIDED,
    MEMOIR_EMOTION_COUNT_FLEXIBLE,
    MEMOIR_EMOTION_COUNT_GUIDED,
)
from authora.services.density.detectors.base import BaseDensityDetector


class MemoirDensityDetector(BaseDensityDetector):
    """Detect memoir density issues: repeated reflection, event retelling, thin support."""

    project_type = "memoir"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []
        repeated_beats = self.density_map.get("repeated_beats", [])

        for i, ch in enumerate(self.chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")
            lower = (text or "").lower()

            reflection_markers = ["i realized", "i learned", "looking back", "in retrospect", "i now understand"]
            reflection_count = sum(1 for m in reflection_markers if m in lower)

            # Repeated reflection without new meaning (poetic memoir often has layered reflection)
            ref_threshold = MEMOIR_REFLECTION_COUNT_FLEXIBLE if self._softer_in_flexible() else MEMOIR_REFLECTION_COUNT_GUIDED
            if reflection_count >= ref_threshold:
                issues.append(
                    self._issue(
                        "repeated_reflection",
                        "repetition",
                        "compress",
                        "low",
                        f"Repeated reflection: {title}",
                        "This chapter has multiple similar reflections. Consider deepening or consolidating.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "compress", "label": "Consolidate or deepen reflections"},
                            {"action": "mark_intentional", "label": "Mark as intentional"},
                        ],
                        confidence=0.5,
                    )
                )

            # Emotional over-explanation (memoir voice is often emotional; avoid punishing authentic voice)
            if word_count > 600:
                emotion_words = ["felt", "feeling", "emotion", "emotional", "realized", "understood"]
                emotion_count = sum(lower.count(w) for w in emotion_words)
                emo_threshold = MEMOIR_EMOTION_COUNT_FLEXIBLE if self._softer_in_flexible() else MEMOIR_EMOTION_COUNT_GUIDED
                if emotion_count > emo_threshold:
                    issues.append(
                        self._issue(
                            "emotional_over_explanation",
                            "over_explanation",
                            "trim",
                            "low",
                            f"Possible emotional over-explanation: {title}",
                            "Consider whether all emotional explanation is needed, or if some can be shown.",
                            chapter_id=chapter_id,
                            fix_suggestions=[
                                {"action": "trim", "label": "Trim or show rather than tell"},
                                {"action": "mark_intentional", "label": "Mark as intentional"},
                            ],
                            confidence=0.5,
                        )
                    )

        return issues
