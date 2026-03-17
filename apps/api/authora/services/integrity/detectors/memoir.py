"""Memoir-specific issue detector. Tolerates fragmented/immersive memoir structure."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.integrity.detectors.base import BaseDetector


class MemoirDetector(BaseDetector):
    """Detect memoir issues. Mode-aware: freeform suppresses; flexible softer on reflection."""

    project_type = "memoir"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []
        chapters = self.chapters

        reflection_markers = [
            "i realized", "i learned", "looking back", "in retrospect", "i now understand",
            "i felt", "i understood", "it meant", "i see now", "reflecting",
        ]
        min_words = 400 if self._softer_in_flexible() else 300

        for i, ch in enumerate(chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")
            word_count = len((text or "").split())

            has_reflection = any(m in (text or "").lower() for m in reflection_markers)
            if word_count > min_words and not has_reflection and not self._softer_in_flexible():
                issues.append(
                    self._issue(
                        "reflection_missing",
                        "emotional_arc",
                        "low",
                        f"Consider adding reflection: {title}",
                        "Memoir benefits from reflection on events. Consider adding your present perspective.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "add_reflection", "label": "Add reflection or meaning-making"},
                            {"action": "mark_intentional", "label": "Mark as intentional (immersive/fragmentary style)"},
                        ],
                        confidence=self._adjust_confidence(0.5, speculative=True),
                    )
                )

        return issues
