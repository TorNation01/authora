"""Non-fiction-specific issue detector. Tolerates lyrical/poetic nonfiction, unconventional structure."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.integrity.detectors.base import BaseDetector


class NonfictionDetector(BaseDetector):
    """Detect non-fiction issues. Mode-aware: freeform suppresses; flexible softer on transitions."""

    project_type = "nonfiction"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []
        chapters = self.chapters

        short_threshold = 80 if self._softer_in_flexible() else 100
        transition_min_words = 300 if self._softer_in_flexible() else 200

        for i, ch in enumerate(chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")

            if word_count > 0 and word_count < short_threshold:
                issues.append(
                    self._issue(
                        "weak_chapter_length",
                        "structure",
                        "low",
                        f"Short chapter: {title}",
                        "This chapter may need more development to fully support its purpose.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "expand", "label": "Expand with examples or explanation"},
                            {"action": "mark_intentional", "label": "Mark as intentional if punchy by design"},
                        ],
                        confidence=self._adjust_confidence(0.6, speculative=True),
                    )
                )

            # Missing transition: lyrical/poetic nonfiction may not use formulaic transitions
            transition_markers = ["however", "therefore", "furthermore", "in addition", "next", "first", "second", "meanwhile", "then"]
            has_transition = any(m in (text or "").lower() for m in transition_markers)
            if i > 0 and word_count > transition_min_words and not has_transition and not self._softer_in_flexible():
                issues.append(
                    self._issue(
                        "missing_transition",
                        "clarity",
                        "low",
                        f"Possible missing transition: {title}",
                        "Consider adding a transition to connect this chapter to the previous one.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "add_transition", "label": "Add bridging paragraph at chapter start"},
                            {"action": "mark_intentional", "label": "Mark as intentional (lyrical/fragmentary style)"},
                        ],
                        confidence=self._adjust_confidence(0.5, speculative=True),
                    )
                )

        return issues
