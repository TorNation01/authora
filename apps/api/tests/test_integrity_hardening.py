"""Story Integrity Engine hardening tests.

Verifies mode-aware behavior, reduced false positives, and creative-freedom safeguards
across scenarios: literary fiction, unresolved endings, fragmented memoir, hybrid,
nonlinear timeline, poetic prose, unconventional workbook, series open threads,
thriller delayed reveal, slow-burn romance.
"""

import pytest

from authora.services.integrity.chapter_analyzer import analyze_chapters
from authora.services.integrity.detectors import get_detectors_for_project
from authora.services.integrity.detectors.general import GeneralDetector, _is_likely_placeholder
from authora.services.integrity.detectors.fiction import FictionDetector
from authora.services.integrity.detectors.memoir import MemoirDetector
from authora.services.integrity.detectors.nonfiction import NonfictionDetector
from authora.services.integrity.detectors.workbook import WorkbookDetector
from authora.services.integrity.story_map import build_story_map


def _chapters(*items: tuple[str, int]) -> list[dict]:
    """Build chapter list from (title, word_count) or (title, content)."""
    out = []
    for i, item in enumerate(items):
        if isinstance(item[1], int):
            title, wc = item[0], item[1]
            text = " ".join(["word"] * wc) if wc > 0 else ""
        else:
            title, text = item[0], item[1]
            wc = len(text.split()) if text else 0
        out.append({
            "id": f"ch{i}",
            "title": title,
            "content": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": text}]}]},
            "word_count": wc,
        })
    return out


def _story_map(chapters: list, project_type: str = "fiction") -> dict:
    return build_story_map(
        chapters=chapters,
        project_knowledge_mode=project_type,
        book_type=project_type,
        planner_data=None,
        vault_characters=[],
        vault_themes=[],
        vault_events=[],
    )


# --- Placeholder detection (avoid false positives) ---


def test_placeholder_avoids_ellipsis():
    """Ellipsis (...) in prose should not trigger placeholder."""
    assert not _is_likely_placeholder("She waited... and waited. Nothing.")
    assert not _is_likely_placeholder("What? Really?")


def test_placeholder_detects_todo_tbd():
    """TODO, TBD, [placeholder] should trigger."""
    assert _is_likely_placeholder("TODO: add scene here")
    assert _is_likely_placeholder("TBD - character name")
    assert _is_likely_placeholder("[placeholder] for later")


def test_placeholder_avoids_rhetorical_question():
    """Rhetorical questions (?) are valid prose."""
    assert not _is_likely_placeholder("Was it worth it? She didn't know.")


# --- Freeform mode ---


def test_freeform_fiction_suppresses_type_specific():
    """Freeform fiction: only GeneralDetector runs."""
    detectors = get_detectors_for_project("fiction", "freeform")
    assert detectors == [GeneralDetector]


def test_freeform_general_only_empty_and_strong_placeholders():
    """Freeform GeneralDetector: only empty chapters and strong placeholders."""
    chs = _chapters(("Ch1", 100), ("Ch2", 0), ("Ch3", 25))
    sm = _story_map(chs)
    sm["guidance_mode"] = "freeform"
    det = GeneralDetector(story_map=sm, chapters=chs, config={"project_type": "fiction", "guidance_mode": "freeform"})
    issues = det.detect()
    types = [i["issue_type"] for i in issues]
    assert "empty_section" in types
    assert "placeholder_heavy" not in types  # 25 words: freeform doesn't flag short


def test_freeform_chapter_analyzer_minimal_issues():
    """Freeform chapter analyzer: only truly empty chapters."""
    chs = _chapters(("Ch1", 50), ("Ch2", 10))
    sm = _story_map(chs)
    result = analyze_chapters(chs, sm, project_type="fiction", guidance_mode="freeform")
    all_issues = []
    for r in result:
        all_issues.extend(r.get("issues", []))
    # Freeform: only chapter_underwritten for < 30 words
    assert len(all_issues) <= 1


# --- Flexible mode (softer thresholds) ---


def test_flexible_weak_ending_softer():
    """Flexible: short ending gets lower severity and 'mark intentional' option."""
    chs = _chapters(("Ch1", 500), ("Ch2", 80))  # Ending 80 words (below flexible 100 threshold)
    sm = _story_map(chs)
    det = FictionDetector(story_map=sm, chapters=chs, config={"project_type": "fiction", "guidance_mode": "flexible"})
    issues = det.detect()
    weak_end = next((i for i in issues if i["issue_type"] == "weak_ending"), None)
    assert weak_end is not None
    assert weak_end["severity"] == "moderate"
    actions = [f["action"] for f in weak_end["fix_suggestions"]]
    assert "mark_intentional" in actions


def test_flexible_memoir_suppresses_reflection():
    """Flexible memoir: reflection_missing suppressed (immersive style valid)."""
    chs = _chapters(("Ch1", 350))  # No reflection markers
    sm = _story_map(chs, "memoir")
    det = MemoirDetector(story_map=sm, chapters=chs, config={"project_type": "memoir", "guidance_mode": "flexible"})
    issues = det.detect()
    ref_missing = [i for i in issues if i["issue_type"] == "reflection_missing"]
    assert len(ref_missing) == 0


def test_flexible_workbook_suppresses_exercise():
    """Flexible workbook: exercise_missing suppressed (unconventional design valid)."""
    chs = _chapters(("Mod1", 250))  # No exercise markers
    sm = _story_map(chs, "workbook")
    det = WorkbookDetector(story_map=sm, chapters=chs, config={"project_type": "workbook", "guidance_mode": "flexible"})
    issues = det.detect()
    ex_missing = [i for i in issues if i["issue_type"] == "exercise_missing"]
    assert len(ex_missing) == 0


# --- Guided mode (stricter, but still with mark intentional) ---


def test_guided_fiction_weak_ending_has_mark_intentional():
    """Guided: weak ending still offers mark as intentional for open endings."""
    chs = _chapters(("Ch1", 500), ("Ch2", 100))
    sm = _story_map(chs)
    det = FictionDetector(story_map=sm, chapters=chs, config={"project_type": "fiction", "guidance_mode": "guided"})
    issues = det.detect()
    weak_end = next((i for i in issues if i["issue_type"] == "weak_ending"), None)
    assert weak_end is not None
    actions = [f["action"] for f in weak_end["fix_suggestions"]]
    assert "mark_intentional" in actions


# --- Chapter analyzer mode-aware ---


def test_chapter_analyzer_flexible_softer_emotional_flat():
    """Flexible: emotionally_flat requires higher word count (poetic prose)."""
    chs = _chapters(("Ch1", 250))  # 250 words, no emotion markers
    sm = _story_map(chs)
    result_guided = analyze_chapters(chs, sm, project_type="fiction", guidance_mode="guided")
    result_flex = analyze_chapters(chs, sm, project_type="fiction", guidance_mode="flexible")
    issues_guided = result_guided[0].get("issues", [])
    issues_flex = result_flex[0].get("issues", [])
    # Flexible: emotion threshold is 400 words, so 250 won't trigger
    flat_guided = [i for i in issues_guided if "emotionally" in i.get("type", "")]
    flat_flex = [i for i in issues_flex if "emotionally" in i.get("type", "")]
    assert len(flat_flex) <= len(flat_guided)


def test_chapter_analyzer_overlong_threshold_raised():
    """Overlong: 5000->6000 words to avoid flagging long literary chapters."""
    chs = _chapters(("Ch1", 5500))
    sm = _story_map(chs)
    result = analyze_chapters(chs, sm, project_type="fiction", guidance_mode="guided")
    issues = result[0].get("issues", [])
    overlong = [i for i in issues if "overlong" in i.get("type", "")]
    assert len(overlong) == 0  # 5500 < 6000


# --- Confidence scoring ---


def test_speculative_issues_lower_confidence_flexible():
    """Flexible: speculative issues have lower confidence."""
    chs = _chapters(("Ch1", 500), ("Ch2", 80))  # Below 100 to trigger weak_ending
    sm = _story_map(chs)
    det = FictionDetector(story_map=sm, chapters=chs, config={"project_type": "fiction", "guidance_mode": "flexible"})
    issues = det.detect()
    weak_end = next((i for i in issues if i["issue_type"] == "weak_ending"), None)
    assert weak_end is not None
    assert weak_end["confidence"] <= 0.7


# --- Hybrid project ---


def test_hybrid_gets_nonfiction_memoir_detectors():
    """Hybrid project uses nonfiction + memoir detectors."""
    detectors = get_detectors_for_project("hybrid", "guided")
    assert GeneralDetector in detectors
    assert NonfictionDetector in detectors
    assert MemoirDetector in detectors
