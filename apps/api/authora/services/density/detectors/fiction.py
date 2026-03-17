"""Fiction density detector - scene purpose, repeated beats, exposition overload."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.density.constants import (
    EXPOSITION_TENSION_THRESHOLD_FLEXIBLE,
    EXPOSITION_TENSION_THRESHOLD_GUIDED,
    EXPOSITION_WORDS_MIN,
)
from authora.services.density.detectors.base import (
    BaseDensityDetector,
    _is_likely_intentional_style,
)


class FictionDensityDetector(BaseDensityDetector):
    """Detect fiction density issues: unclear scene purpose, repeated beats, exposition overload."""

    project_type = "fiction"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []
        density_by_chapter = self.density_map.get("density_by_chapter", [])
        repeated_beats = self.density_map.get("repeated_beats", [])
        total = len(self.chapters)

        for i, ch in enumerate(self.chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")

            d = next((x for x in density_by_chapter if x.get("chapter_index") == i), {})

            # Weak midpoint (guided only; skip if reflective/thematic - may be intentional)
            if d.get("is_midpoint") and word_count < 300 and not self._softer_in_flexible():
                if _is_likely_intentional_style(self.density_map, i, chapter_id=chapter_id):
                    continue
                tension = d.get("tension_density", 0)
                movement = d.get("movement", 0)
                if tension < 0.4 or movement < 0.4:
                    issues.append(
                        self._issue(
                            "weak_midpoint",
                            "drag",
                            "strengthen",
                            "low",
                            f"Midpoint may need strengthening: {title}",
                            "Chapters in the middle often benefit from a clear beat or turn.",
                            chapter_id=chapter_id,
                            fix_suggestions=[
                                {"action": "strengthen", "label": "Add a midpoint beat or revelation"},
                                {"action": "mark_intentional", "label": "Mark as intentional"},
                            ],
                            confidence=0.5,
                        )
                    )

            # Exposition overload: long passages with low tension/movement
            # Skip quiet emotional scenes, literary reflection, atmospheric pacing
            if word_count > EXPOSITION_WORDS_MIN and not self._suppress_in_freeform():
                if _is_likely_intentional_style(self.density_map, i, chapter_id=chapter_id):
                    continue
                tension = d.get("tension_density", 0.5)
                movement = d.get("movement", 0.5)
                threshold = EXPOSITION_TENSION_THRESHOLD_FLEXIBLE if self._softer_in_flexible() else EXPOSITION_TENSION_THRESHOLD_GUIDED
                if tension < threshold and movement < threshold:
                    issues.append(
                        self._issue(
                            "exposition_overload",
                            "over_explanation",
                            "trim",
                            "low",
                            f"Possible exposition overload: {title}",
                            "This chapter has long passages with little tension or movement. Consider trimming or dramatizing.",
                            chapter_id=chapter_id,
                            fix_suggestions=[
                                {"action": "trim", "label": "Trim exposition"},
                                {"action": "compress", "label": "Convert exposition to scene"},
                                {"action": "mark_intentional", "label": "Mark as intentional"},
                            ],
                            confidence=0.5,
                        )
                    )

            # Repeated emotional beat (skip if thematic/reflective - may be deliberate refrain)
            if repeated_beats and word_count > 400:
                if _is_likely_intentional_style(self.density_map, i, chapter_id=chapter_id):
                    continue
                lower = (text or "").lower()
                for beat in repeated_beats:
                    hint = beat.get("hint", "")
                    if hint in lower and beat.get("occurrences", 0) >= 3:
                        issues.append(
                            self._issue(
                                "repeated_emotional_beat",
                                "repetition",
                                "compress",
                                "low",
                                f"Repeated emotional beat: {title}",
                                f"'{hint}' appears often. Consider varying or deepening the beat.",
                                chapter_id=chapter_id,
                                fix_suggestions=[
                                    {"action": "compress", "label": "Vary or deepen the emotional beat"},
                                    {"action": "mark_intentional", "label": "Mark as intentional"},
                                ],
                                confidence=0.5,
                            )
                        )
                        break

        return issues
