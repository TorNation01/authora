"""Base detector for integrity issues."""

from __future__ import annotations

from typing import Any


class BaseDetector:
    """Base class for issue detectors."""

    project_type: str = "general"
    guidance_mode: str = "flexible"

    def __init__(self, story_map: dict[str, Any], chapters: list[dict[str, Any]], config: dict[str, Any] | None = None):
        self.story_map = story_map
        self.chapters = chapters
        self.config = config or {}
        self._project_type = self.config.get("project_type") or self.story_map.get("project_type") or "fiction"
        self._guidance_mode = self.config.get("guidance_mode") or "flexible"

    def _suppress_in_freeform(self) -> bool:
        """True if this detector should suppress most issues in freeform mode."""
        return self._guidance_mode == "freeform"

    def _softer_in_flexible(self) -> bool:
        """True if flexible mode should use softer thresholds."""
        return self._guidance_mode == "flexible"

    def _adjust_confidence(self, base: float, speculative: bool = False) -> float:
        """Lower confidence for speculative issues in flexible/freeform."""
        if self._guidance_mode == "freeform" and speculative:
            return min(base, 0.4)
        if self._guidance_mode == "flexible" and speculative:
            return min(base, 0.6)
        return base

    def detect(self) -> list[dict[str, Any]]:
        """Return list of detected issues. Override in subclasses."""
        return []

    def _issue(
        self,
        issue_type: str,
        category: str,
        severity: str,
        title: str,
        description: str | None = None,
        chapter_id: str | None = None,
        location_hint: str | None = None,
        related_chapter_ids: list[str] | None = None,
        fix_suggestions: list[dict[str, Any]] | None = None,
        confidence: float = 0.8,
    ) -> dict[str, Any]:
        """Build an issue dict."""
        return {
            "issue_type": issue_type,
            "category": category,
            "severity": severity,
            "title": title,
            "description": description,
            "chapter_id": chapter_id,
            "location_hint": location_hint,
            "related_chapter_ids": related_chapter_ids or [],
            "fix_suggestions": fix_suggestions or [],
            "confidence": confidence,
        }
