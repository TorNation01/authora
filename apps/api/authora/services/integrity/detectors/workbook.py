"""Workbook/guided book issue detector. Tolerates unconventional module sequence."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.integrity.detectors.base import BaseDetector


class WorkbookDetector(BaseDetector):
    """Detect workbook issues. Mode-aware: freeform suppresses; flexible softer on exercise presence."""

    project_type = "workbook"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []
        chapters = self.chapters

        exercise_markers = ["exercise", "prompt", "activity", "try this", "your turn", "practice", "reflect", "worksheet", "journal"]
        min_words = 300 if self._softer_in_flexible() else 200

        for i, ch in enumerate(chapters):
            content = ch.get("content") or {}
            text = (tiptap_to_plain_text(content) or "").lower()
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")
            word_count = len(text.split())

            has_exercise = any(m in text for m in exercise_markers)
            if word_count > min_words and not has_exercise and not self._softer_in_flexible():
                issues.append(
                    self._issue(
                        "exercise_missing",
                        "progression",
                        "low",
                        f"Consider adding exercise or prompt: {title}",
                        "Workbook chapters often benefit from exercises or reflection prompts.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "add_exercise", "label": "Add exercise or reflection prompt"},
                            {"action": "mark_intentional", "label": "Mark as intentional (unconventional module design)"},
                        ],
                        confidence=self._adjust_confidence(0.5, speculative=True),
                    )
                )

        return issues
