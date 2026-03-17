"""Workbook density detector - excessive explanation, weak exercise support."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.density.constants import (
    WORKBOOK_EXERCISE_WORDS_MIN,
    WORKBOOK_EXPLANATION_COUNT_FLEXIBLE,
)
from authora.services.density.detectors.base import BaseDensityDetector


class WorkbookDensityDetector(BaseDensityDetector):
    """Detect workbook density issues: excessive explanation, weak exercise support."""

    project_type = "workbook"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []

        for i, ch in enumerate(self.chapters):
            content = ch.get("content") or {}
            text = (tiptap_to_plain_text(content) or "").lower()
            word_count = len(text.split())
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")

            exercise_markers = ["exercise", "prompt", "activity", "try this", "your turn", "reflect", "journal"]
            has_exercise = any(m in text for m in exercise_markers)
            explanation_markers = ["because", "this means", "in other words", "simply put", "the idea is"]
            explanation_count = sum(text.count(m) for m in explanation_markers)

            # Excessive explanation before action (workbooks often have intentional setup)
            expl_threshold = WORKBOOK_EXPLANATION_COUNT_FLEXIBLE if self._softer_in_flexible() else 5
            if word_count > 400 and has_exercise and explanation_count > expl_threshold:
                issues.append(
                    self._issue(
                        "excessive_explanation",
                        "over_explanation",
                        "trim",
                        "low",
                        f"Excessive explanation: {title}",
                        "This chapter may have more explanation than needed before the exercise. Consider trimming.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "trim", "label": "Trim explanation to essentials"},
                            {"action": "mark_intentional", "label": "Mark as intentional"},
                        ],
                        confidence=0.5,
                    )
                )

            # Missing exercise support (skip intentional reflection pages - short, reflective)
            if word_count > WORKBOOK_EXERCISE_WORDS_MIN and not has_exercise:
                if self._softer_in_flexible():
                    if word_count < 600:
                        reflection_markers = ["reflect", "consider", "pause", "journal", "space"]
                        if any(m in text for m in reflection_markers):
                            continue  # Likely intentional reflection page
                    continue  # In flexible, don't require exercise for every chapter
                issues.append(
                    self._issue(
                        "missing_exercise",
                        "practical_support_gap",
                        "expand",
                        "low",
                        f"Consider adding exercise: {title}",
                        "Workbook chapters often benefit from an exercise or reflection prompt.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "expand", "label": "Add exercise or reflection prompt"},
                            {"action": "mark_intentional", "label": "Mark as intentional"},
                        ],
                        confidence=0.5,
                    )
                )

        return issues
