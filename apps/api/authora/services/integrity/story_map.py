"""Story map construction from manuscript and project data."""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text


def build_story_map(
    chapters: list[dict[str, Any]],
    project_knowledge_mode: str,
    book_type: str,
    planner_data: dict[str, Any] | None = None,
    vault_characters: list[dict[str, Any]] | None = None,
    vault_themes: list[dict[str, Any]] | None = None,
    vault_events: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build internal story/project map from manuscript and related data."""
    threads: list[dict[str, Any]] = []
    character_appearances: dict[str, list[int]] = {}
    character_changes: dict[str, list[dict[str, Any]]] = {}
    themes_mentioned: dict[str, list[int]] = {}
    chapter_purposes: list[dict[str, Any]] = []
    promises: list[dict[str, Any]] = []
    timeline_events: list[dict[str, Any]] = []
    unresolved_questions: list[str] = []
    setup_candidates: list[dict[str, Any]] = []
    pacing_by_chapter: list[dict[str, Any]] = []
    emotional_markers: list[dict[str, Any]] = []

    for i, ch in enumerate(chapters):
        content = ch.get("content") or {}
        text = tiptap_to_plain_text(content)
        word_count = len(text.split()) if text else 0
        title = ch.get("title", "Untitled")

        purpose = _infer_chapter_purpose(text, title, i, len(chapters))
        chapter_purposes.append({
            "chapter_index": i,
            "chapter_id": str(ch.get("id", "")),
            "title": title,
            "word_count": word_count,
            "purpose_hint": purpose,
        })

        pacing_by_chapter.append({
            "chapter_index": i,
            "word_count": word_count,
            "pacing_hint": _pacing_hint(word_count, i, len(chapters)),
        })

        _extract_promises(text, i, promises)
        _extract_setup_candidates(text, i, setup_candidates)
        _extract_emotional_markers(text, i, emotional_markers)

        if vault_characters:
            for char in vault_characters:
                name = char.get("full_name") or char.get("name", "")
                if name and name.lower() in text.lower():
                    char_id = str(char.get("id", name))
                    character_appearances.setdefault(char_id, []).append(i)

        if vault_themes:
            for theme in vault_themes:
                name = theme.get("name", "")
                if name and name.lower() in text.lower():
                    theme_id = str(theme.get("id", name))
                    themes_mentioned.setdefault(theme_id, []).append(i)

        if vault_events:
            for ev in vault_events:
                name = ev.get("name") or ev.get("title", "")
                if name and name.lower() in text.lower():
                    timeline_events.append({
                        "event_id": str(ev.get("id", "")),
                        "chapter_index": i,
                    })

    threads = _infer_threads(chapter_purposes, character_appearances, themes_mentioned)
    subplot_candidates = _infer_subplot_candidates(threads, character_appearances)

    return {
        "project_type": project_knowledge_mode or book_type,
        "chapter_count": len(chapters),
        "total_word_count": sum(p["word_count"] for p in chapter_purposes),
        "threads": threads,
        "subplot_candidates": subplot_candidates,
        "character_appearances": character_appearances,
        "character_changes": character_changes,
        "themes_mentioned": themes_mentioned,
        "chapter_purposes": chapter_purposes,
        "promises": promises,
        "timeline_events": timeline_events,
        "unresolved_questions": unresolved_questions,
        "setup_candidates": setup_candidates,
        "pacing_by_chapter": pacing_by_chapter,
        "emotional_markers": emotional_markers,
        "planner_data_summary": _summarize_planner(planner_data) if planner_data else None,
    }


def _extract_promises(text: str, chapter_index: int, out: list[dict[str, Any]]) -> None:
    """Extract promise-like phrases (will, going to, promise, etc.)."""
    if not text or len(text) < 100:
        return
    lower = text.lower()
    promise_markers = ["will ", "going to ", "promise", "you'll see", "by the end"]
    for m in promise_markers:
        if m in lower:
            out.append({"chapter_index": chapter_index, "hint": m})


def _extract_setup_candidates(text: str, chapter_index: int, out: list[dict[str, Any]]) -> None:
    """Extract setup-like elements (introduced, first time, discovered)."""
    if not text or len(text) < 50:
        return
    lower = text.lower()
    setup_markers = ["introduced", "first time", "discovered", "learned that", "found out"]
    for m in setup_markers:
        if m in lower:
            out.append({"chapter_index": chapter_index, "hint": m})


def _extract_emotional_markers(text: str, chapter_index: int, out: list[dict[str, Any]]) -> None:
    """Extract emotional progression markers."""
    if not text:
        return
    lower = text.lower()
    markers = ["realized", "felt", "anger", "fear", "hope", "despair", "joy", "relief"]
    for m in markers:
        if m in lower:
            out.append({"chapter_index": chapter_index, "hint": m})
            break


def _pacing_hint(word_count: int, index: int, total: int) -> str:
    """Infer pacing hint for chapter."""
    if word_count < 100:
        return "very_short"
    if word_count > 5000:
        return "very_long"
    if index < total // 3 and word_count < 300:
        return "slow_opening"
    if index > total * 2 // 3 and word_count < 300:
        return "rushed_ending"
    return "normal"


def _infer_threads(
    chapter_purposes: list[dict[str, Any]],
    char_apps: dict[str, list[int]],
    themes: dict[str, list[int]],
) -> list[dict[str, Any]]:
    """Infer major threads from character and theme presence."""
    threads = []
    for cid, apps in char_apps.items():
        if len(apps) >= 2:
            threads.append({"type": "character", "id": cid, "chapters": apps})
    for tid, apps in themes.items():
        if len(apps) >= 2:
            threads.append({"type": "theme", "id": tid, "chapters": apps})
    return threads


def _infer_subplot_candidates(
    threads: list[dict[str, Any]],
    char_apps: dict[str, list[int]],
) -> list[dict[str, Any]]:
    """Infer subplot candidates from threads."""
    return [t for t in threads if t.get("type") == "character" and len(t.get("chapters", [])) >= 2]


def _infer_chapter_purpose(text: str, title: str, index: int, total: int) -> str:
    """Infer likely chapter purpose from content and position."""
    if not text or len(text.strip()) < 50:
        return "placeholder_or_empty"
    if index == 0:
        return "opening"
    if index == total - 1:
        return "ending"
    word_count = len(text.split())
    if word_count < 100:
        return "short_section"
    return "body"


def _summarize_planner(planner_data: dict[str, Any]) -> dict[str, Any]:
    """Summarize planner/outline data for story map."""
    return {
        "has_outline": bool(planner_data.get("chapters") or planner_data.get("outline")),
        "chapter_count": len(planner_data.get("chapters", []) or planner_data.get("outline", [])),
    }
