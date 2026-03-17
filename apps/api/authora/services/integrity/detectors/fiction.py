"""Fiction-specific issue detector. Avoids over-policing literary fiction, slow-burn, series, etc."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text
from authora.services.integrity.detectors.base import BaseDetector


class FictionDetector(BaseDetector):
    """Detect fiction issues. Mode-aware: freeform suppresses most; flexible uses softer thresholds."""

    project_type = "fiction"

    def detect(self) -> list[dict[str, Any]]:
        if self._suppress_in_freeform():
            return []

        issues = []
        chapters = self.chapters
        story_map = self.story_map
        char_apps = story_map.get("character_appearances", {})
        total_chapters = len(chapters)

        if not chapters:
            return issues

        # Thresholds: flexible = softer (literary fiction, slow-burn, unconventional structure)
        opening_min = 150 if self._softer_in_flexible() else 200
        ending_min = 100 if self._softer_in_flexible() else 150

        for i, ch in enumerate(chapters):
            content = ch.get("content") or {}
            text = tiptap_to_plain_text(content)
            word_count = len(text.split()) if text else 0
            chapter_id = str(ch.get("id", ""))
            title = ch.get("title", "Untitled")

            if i == 0 and word_count < opening_min and word_count > 0:
                issues.append(
                    self._issue(
                        "weak_opening",
                        "structure",
                        "low" if self._softer_in_flexible() else "moderate",
                        "Opening chapter may be too short",
                        "The first chapter sets reader expectations. Consider strengthening the opening.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "strengthen_inciting_incident", "label": "Add or clarify the inciting incident"},
                            {"action": "mark_intentional", "label": "Mark as intentional if spare opening is deliberate"},
                        ],
                        confidence=self._adjust_confidence(0.6, speculative=True),
                    )
                )

            # Weak ending: avoid flagging intentionally unresolved endings (literary, series)
            if i == total_chapters - 1 and word_count < ending_min and word_count > 0:
                issues.append(
                    self._issue(
                        "weak_ending",
                        "structure",
                        "moderate" if self._softer_in_flexible() else "high",
                        "Ending chapter may be incomplete",
                        "The final chapter is short. Add resolution if needed, or mark as intentional for open endings.",
                        chapter_id=chapter_id,
                        fix_suggestions=[
                            {"action": "add_resolution", "label": "Add or strengthen the resolution"},
                            {"action": "mark_intentional", "label": "Mark as intentional (open/unresolved ending)"},
                        ],
                        confidence=self._adjust_confidence(0.7, speculative=True),
                    )
                )

        # Character single appearance: minor characters, cameos are valid
        char_ids_with_one_app = [cid for cid, apps in char_apps.items() if len(apps) == 1]
        if char_ids_with_one_app and total_chapters > 5 and not self._softer_in_flexible():
            issues.append(
                self._issue(
                    "character_single_appearance",
                    "character",
                    "low",
                    "Character(s) appear only once",
                    "Some characters appear in only one chapter. Consider developing their arc or removing if minor.",
                    fix_suggestions=[
                        {"action": "develop_arc", "label": "Develop character arc across chapters"},
                        {"action": "mark_intentional", "label": "Mark as intentional (minor/cameo character)"},
                    ],
                    confidence=self._adjust_confidence(0.5, speculative=True),
                )
            )

        # Too many threads: series books often leave threads open intentionally
        threads = story_map.get("threads", [])
        if len(threads) > 10 and total_chapters < 15 and not self._softer_in_flexible():
            issues.append(
                self._issue(
                    "too_many_threads",
                    "structure",
                    "low",
                    "Many plot threads may be open",
                    "Several character and theme threads are present. Consider whether all need resolution.",
                    fix_suggestions=[
                        {"action": "prioritize_threads", "label": "Identify which threads are essential"},
                        {"action": "mark_intentional", "label": "Mark as intentional (series/open threads)"},
                    ],
                    confidence=self._adjust_confidence(0.5, speculative=True),
                )
            )

        # Pacing trough: slow-burn romance, literary fiction often have deliberate slow sections
        pacing = story_map.get("pacing_by_chapter", [])
        trough_count = sum(1 for p in pacing if p.get("pacing_hint") in ("very_short", "slow_opening"))
        if trough_count >= 4 and total_chapters > 8 and not self._softer_in_flexible():
            issues.append(
                self._issue(
                    "pacing_trough",
                    "pacing",
                    "low",
                    "Possible pacing trough across chapters",
                    "Several chapters are short. Consider varying pace, or mark as intentional for slow-burn.",
                    fix_suggestions=[
                        {"action": "vary_pace", "label": "Add a stronger beat or scene in the slow section"},
                        {"action": "mark_intentional", "label": "Mark as intentional (slow-burn/deliberate pace)"},
                    ],
                    confidence=self._adjust_confidence(0.5, speculative=True),
                )
            )

        # Theme introduced once: symbolic themes may appear briefly
        themes = story_map.get("themes_mentioned", {})
        theme_appears_once = [tid for tid, apps in themes.items() if len(apps) == 1]
        if theme_appears_once and total_chapters > 6 and not self._softer_in_flexible():
            issues.append(
                self._issue(
                    "theme_introduced_not_developed",
                    "theme",
                    "low",
                    "Theme(s) appear in only one chapter",
                    "Some themes are mentioned once but not developed. Consider weaving them through the story.",
                    fix_suggestions=[
                        {"action": "develop_theme", "label": "Revisit the theme in later chapters"},
                        {"action": "mark_intentional", "label": "Mark as intentional (symbolic/brief motif)"},
                    ],
                    confidence=self._adjust_confidence(0.5, speculative=True),
                )
            )

        return issues
