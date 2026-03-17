"""General issue detector - works across all project types."""

from __future__ import annotations

import re
from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.integrity.detectors.base import BaseDetector


def _is_likely_placeholder(text: str) -> bool:
    """Detect placeholder text while avoiding false positives (ellipsis, rhetorical questions)."""
    if not text:
        return False
    lower = text.lower()
    # Strong placeholders - high confidence
    strong = ["todo", "tbd", "[placeholder]", "[insert", "[xxx]", "xxx"]
    if any(p in lower for p in strong):
        return True
    # "[placeholder" or "[insert" without closing - common placeholder pattern
    if re.search(r"\[(?:placeholder|insert|xxx)\b", lower):
        return True
    return False


class GeneralDetector(BaseDetector):
    """Detect general issues: empty sections, placeholders. Avoid over-policing creative choices."""

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return self._detect_freeform_only()

        issues = []
        for i, ch in enumerate(self.chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")

            if word_count == 0:
                issues.append(
                    self._issue(
                        "empty_section",
                        "structure",
                        "moderate",
                        f"Empty or near-empty chapter: {title}",
                        "This chapter has no content. Consider adding content or removing it.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "add_content", "label": "Add content to this chapter"},
                            {"action": "mark_intentional", "label": "Mark as intentional if placeholder"},
                        ],
                    )
                )
            elif word_count < 40 or (word_count < 50 and not self._softer_in_flexible()):
                issues.append(
                    self._issue(
                        "placeholder_heavy",
                        "structure",
                        "low",
                        f"Very short chapter: {title} ({word_count} words)",
                        "This chapter is very short. It may be a placeholder or need expansion.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "expand", "label": "Expand this chapter"},
                            {"action": "mark_intentional", "label": "Mark as intentional if brief by design"},
                        ],
                        confidence=self._adjust_confidence(0.7, speculative=True),
                    )
                )

            if _is_likely_placeholder(text or ""):
                issues.append(
                    self._issue(
                        "unresolved_placeholder",
                        "revision_blocker",
                        "moderate",
                        f"Placeholder text in chapter: {title}",
                        "This chapter contains placeholder text (TODO, TBD, etc.) that may need to be replaced.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "replace_placeholder", "label": "Replace placeholder with actual content"},
                            {"action": "mark_intentional", "label": "Mark as intentional if keeping for later"},
                        ],
                        confidence=0.9,
                    )
                )

        return issues

    def _detect_freeform_only(self) -> list[dict[str, Any]]:
        """Freeform: only flag truly empty chapters and strong placeholders."""
        issues = []
        for ch in self.chapters:
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")

            if word_count == 0:
                issues.append(
                    self._issue(
                        "empty_section",
                        "structure",
                        "low",
                        f"Empty chapter: {title}",
                        "This chapter has no content.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "add_content", "label": "Add content"},
                            {"action": "mark_intentional", "label": "Mark as intentional"},
                        ],
                        confidence=0.95,
                    )
                )
            elif _is_likely_placeholder(text or ""):
                issues.append(
                    self._issue(
                        "unresolved_placeholder",
                        "revision_blocker",
                        "low",
                        f"Placeholder text in chapter: {title}",
                        "Placeholder text (TODO, TBD) found. Replace before export if needed.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "replace_placeholder", "label": "Replace placeholder"},
                            {"action": "mark_intentional", "label": "Mark as intentional"},
                        ],
                        confidence=0.9,
                    )
                )
        return issues
