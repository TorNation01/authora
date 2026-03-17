"""Base detector for density issues."""

from __future__ import annotations

from typing import Any


def _get_chapter_purpose(density_map: dict[str, Any], chapter_id: str) -> dict[str, Any] | None:
    """Get chapter purpose data from scene_purpose_analysis."""
    purpose = density_map.get("scene_purpose_analysis") or {}
    for cp in purpose.get("chapter_purposes", []):
        if str(cp.get("chapter_id", "")) == str(chapter_id):
            return cp
    return None


def _is_likely_intentional_style(
    density_map: dict[str, Any],
    chapter_index: int,
    chapter_id: str | None = None,
    primary_jobs: list[str] | None = None,
) -> bool:
    """True if chapter appears to be intentionally reflective, atmospheric, or literary.

    Used to avoid flagging: quiet emotional scenes, poetic memoir, literary fiction,
    contemplative nonfiction, atmospheric fantasy, intentionally slow pacing.
    """
    density_by_chapter = density_map.get("density_by_chapter", [])
    ch_data = next((d for d in density_by_chapter if d.get("chapter_index") == chapter_index), {})
    emotional_density = ch_data.get("emotional_density", 0)
    purpose_hint = ch_data.get("purpose_hint", "")

    # High emotional density suggests intentional emotional weight
    if emotional_density >= 0.5:
        return True
    # Bridge or reflective purpose often intentional
    if purpose_hint in ("bridge", "reflection"):
        return True
    # Scene purpose jobs that suggest intentional slowness
    jobs = primary_jobs
    if jobs is None and chapter_id is not None:
        cp = _get_chapter_purpose(density_map, chapter_id)
        if cp:
            jobs = cp.get("primary_jobs", [])
    if jobs:
        intentional_jobs = {"reinforce_theme", "deliver_reflection", "deepen_character", "build_setup"}
        if intentional_jobs & set(jobs):
            return True
    return False


class BaseDensityDetector:
    """Base class for density issue detectors."""

    project_type: str = "general"
    guidance_mode: str = "flexible"

    def __init__(
        self,
        density_map: dict[str, Any],
        chapters: list[dict[str, Any]],
        story_map: dict[str, Any],
        config: dict[str, Any] | None = None,
    ):
        self.density_map = density_map
        self.chapters = chapters
        self.story_map = story_map
        self.config = config or {}
        self._project_type = self.config.get("project_type") or self.density_map.get("project_type") or "fiction"
        self._guidance_mode = self.config.get("guidance_mode") or "flexible"

    def detect(self) -> list[dict[str, Any]]:
        """Return list of detected density issues. Override in subclasses."""
        return []

    def _suppress_in_freeform(self) -> bool:
        return self._guidance_mode == "freeform"

    def _softer_in_flexible(self) -> bool:
        return self._guidance_mode == "flexible"

    def _is_guided(self) -> bool:
        return self._guidance_mode == "guided"

    def _issue(
        self,
        issue_type: str,
        category: str,
        action_category: str,
        severity: str,
        title: str,
        description: str | None = None,
        chapter_id: str | None = None,
        location_hint: str | None = None,
        related_chapter_ids: list[str] | None = None,
        fix_suggestions: list[dict[str, Any]] | None = None,
        confidence: float = 0.8,
    ) -> dict[str, Any]:
        """Build a density issue dict."""
        return {
            "issue_type": issue_type,
            "category": category,
            "action_category": action_category,
            "severity": severity,
            "title": title,
            "description": description,
            "chapter_id": chapter_id,
            "location_hint": location_hint,
            "related_chapter_ids": related_chapter_ids or [],
            "fix_suggestions": fix_suggestions or [],
            "confidence": confidence,
        }
