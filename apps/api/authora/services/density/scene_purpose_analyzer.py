"""Scene and section purpose analysis for the Story Density Engine.

Estimates whether each scene/section is primarily doing one or more jobs:
move_plot, deepen_character, escalate_tension, deliver_payoff, build_setup,
deliver_reflection, explain_concept, provide_example, create_transition,
provide_exercise, reinforce_theme.
"""

from __future__ import annotations

from typing import Any

from authora.services.export import tiptap_to_plain_text


SECTION_JOBS = (
    "move_plot",
    "deepen_character",
    "escalate_tension",
    "deliver_payoff",
    "build_setup",
    "deliver_reflection",
    "explain_concept",
    "provide_example",
    "create_transition",
    "provide_exercise",
    "reinforce_theme",
)

JOB_MARKERS: dict[str, list[str]] = {
    "move_plot": ["then", "next", "after", "when", "decided", "went", "came", "left", "arrived", "discovered"],
    "deepen_character": ["felt", "realized", "knew", "understood", "thought", "wondered", "remembered"],
    "escalate_tension": ["but", "however", "suddenly", "danger", "threat", "conflict", "risk", "must", "had to"],
    "deliver_payoff": ["finally", "at last", "realized", "understood", "revealed", "discovered"],
    "build_setup": ["introduced", "first time", "learned", "found out", "noticed", "began to"],
    "deliver_reflection": ["looking back", "in retrospect", "i realized", "it occurred to me", "reflecting"],
    "explain_concept": ["means", "simply put", "in other words", "the key is", "essentially", "basically"],
    "provide_example": ["for example", "for instance", "consider", "imagine", "suppose", "such as"],
    "create_transition": ["however", "therefore", "meanwhile", "later", "the next", "after that", "as"],
    "provide_exercise": ["try this", "exercise", "practice", "reflect on", "journal", "write down", "action step"],
    "reinforce_theme": ["always", "never", "truth", "lesson", "meaning", "theme", "moral"],
}


def extract_sections_from_content(content: dict[str, Any] | None, target_words: int = 400) -> list[dict[str, Any]]:
    """Extract sections (chunks) from TipTap content. Each section is ~target_words."""
    if content is None or not isinstance(content, dict):
        return []
    blocks: list[str] = []
    if "content" in content and isinstance(content["content"], list):
        for node in content["content"]:
            text = _extract_text_from_node(node)
            if text.strip():
                blocks.append(text.strip())
    if not blocks:
        return []

    sections: list[dict[str, Any]] = []
    current_text: list[str] = []
    current_words = 0
    for block in blocks:
        words = block.split()
        block_word_count = len(words)
        if current_words + block_word_count > target_words and current_text:
            combined = " ".join(current_text)
            sections.append({
                "text": combined,
                "word_count": current_words,
                "block_count": len(current_text),
            })
            current_text = []
            current_words = 0
        current_text.append(block)
        current_words += block_word_count
    if current_text:
        combined = " ".join(current_text)
        sections.append({
            "text": combined,
            "word_count": current_words,
            "block_count": len(current_text),
        })
    return sections


def _extract_text_from_node(node: dict[str, Any]) -> str:
    """Extract plain text from a TipTap node."""
    if "text" in node:
        return str(node.get("text", ""))
    if "content" in node:
        parts = []
        for c in node["content"]:
            if isinstance(c, dict):
                if c.get("type") == "hardBreak":
                    parts.append("\n")
                elif "text" in c:
                    parts.append(str(c.get("text", "")))
                elif "content" in c:
                    parts.append(_extract_text_from_node(c))
            elif isinstance(c, list):
                for sub in c:
                    if isinstance(sub, dict):
                        parts.append(_extract_text_from_node(sub))
        return "".join(parts)
    return ""


def infer_section_jobs(text: str) -> list[str]:
    """Infer which jobs this section is primarily doing. Returns list of job keys."""
    if not text or len(text.strip()) < 30:
        return []
    lower = text.lower()
    jobs: list[tuple[str, int]] = []
    for job, markers in JOB_MARKERS.items():
        count = sum(1 for m in markers if m in lower)
        if count > 0:
            jobs.append((job, count))
    jobs.sort(key=lambda x: -x[1])
    return [j[0] for j in jobs[:3]] if jobs else ["unclear"]


def analyze_chapter_purpose(
    content: dict[str, Any] | None,
    chapter_index: int,
    total_chapters: int,
    project_type: str,
) -> dict[str, Any]:
    """Analyze chapter-level purpose: jobs, clarity, flags."""
    text = tiptap_to_plain_text(content)
    word_count = len(text.split()) if text else 0
    chapter_jobs = infer_section_jobs(text) if text else []

    purpose_clarity = _assess_purpose_clarity(text, chapter_jobs, word_count, chapter_index, total_chapters)
    plot_contribution = _score_markers(text, JOB_MARKERS["move_plot"])
    character_contribution = _score_markers(text, JOB_MARKERS["deepen_character"])
    emotional_contribution = _score_markers(text, JOB_MARKERS["deliver_reflection"]) + _score_markers(text, JOB_MARKERS["deepen_character"])
    thematic_contribution = _score_markers(text, JOB_MARKERS["reinforce_theme"])
    instructional_contribution = _score_markers(text, JOB_MARKERS["explain_concept"]) if project_type in ("nonfiction", "workbook", "hybrid") else 0.0
    practical_contribution = _score_markers(text, JOB_MARKERS["provide_exercise"]) if project_type in ("workbook", "hybrid") else 0.0

    flags: list[str] = []
    if not chapter_jobs or chapter_jobs == ["unclear"]:
        flags.append("unclear_purpose")
    if word_count > 500 and purpose_clarity < 0.5:
        flags.append("does_too_little_for_size")
    if purpose_clarity >= 0.7 and word_count > 3000:
        flags.append("likely_needs_compression")

    return {
        "chapter_index": chapter_index,
        "word_count": word_count,
        "primary_jobs": chapter_jobs,
        "purpose_clarity": purpose_clarity,
        "plot_contribution": min(1.0, plot_contribution),
        "character_contribution": min(1.0, character_contribution),
        "emotional_contribution": min(1.0, emotional_contribution),
        "thematic_contribution": min(1.0, thematic_contribution),
        "instructional_contribution": min(1.0, instructional_contribution),
        "practical_contribution": min(1.0, practical_contribution),
        "flags": flags,
    }


def analyze_scene_purposes(
    content: dict[str, Any] | None,
    chapter_id: str,
    chapter_index: int,
    chapter_title: str,
    project_type: str,
) -> list[dict[str, Any]]:
    """Analyze each section/scene within a chapter for purpose jobs and flags."""
    sections = extract_sections_from_content(content)
    results: list[dict[str, Any]] = []
    seen_jobs: dict[str, int] = {}

    for i, sec in enumerate(sections):
        text = sec.get("text", "")
        jobs = infer_section_jobs(text)
        word_count = sec.get("word_count", 0)

        flags: list[str] = []
        if not jobs or jobs == ["unclear"]:
            flags.append("unclear_purpose")
        for j in jobs:
            if j != "unclear":
                seen_jobs[j] = seen_jobs.get(j, 0) + 1
        if jobs and jobs[0] != "unclear" and seen_jobs.get(jobs[0], 0) > 2:
            flags.append("repeats_job_from_earlier_section")
        if word_count > 400 and len(jobs) <= 1 and (not jobs or jobs == ["unclear"]):
            flags.append("does_too_little_for_size")
        if word_count > 600 and "create_transition" in jobs and len(jobs) == 1:
            flags.append("likely_needs_compression")
        if word_count > 200 and "deliver_payoff" in jobs and len(jobs) == 1:
            flags.append("likely_needs_strengthening")

        results.append({
            "section_index": i,
            "chapter_id": chapter_id,
            "chapter_index": chapter_index,
            "chapter_title": chapter_title,
            "word_count": word_count,
            "primary_jobs": jobs,
            "flags": flags,
            "suggestion": _suggest_for_section(flags, jobs, word_count),
        })
    return results


def _score_markers(text: str, markers: list[str]) -> float:
    """0-1 score based on marker presence."""
    if not text or len(text) < 50:
        return 0.0
    lower = text.lower()
    count = sum(1 for m in markers if m in lower)
    return min(0.9, 0.2 + count * 0.15)


def _assess_purpose_clarity(
    text: str,
    jobs: list[str],
    word_count: int,
    chapter_index: int,
    total: int,
) -> float:
    """0-1: how clear is the chapter's purpose."""
    if not text or len(text.strip()) < 50:
        return 0.2
    if not jobs or jobs == ["unclear"]:
        return 0.3
    if word_count < 100 and chapter_index not in (0, total - 1):
        return 0.5
    if len(jobs) >= 2:
        return 0.8
    return 0.75


def _suggest_for_section(flags: list[str], jobs: list[str], word_count: int) -> str | None:
    """Suggest action for section based on flags."""
    if "unclear_purpose" in flags:
        return "Clarify purpose or consider cutting."
    if "repeats_job_from_earlier_section" in flags:
        return "Compress or merge with earlier section."
    if "does_too_little_for_size" in flags:
        return "Strengthen or trim."
    if "likely_needs_compression" in flags:
        return "Consider compressing."
    if "likely_needs_strengthening" in flags:
        return "Consider strengthening payoff."
    return None


def run_full_purpose_analysis(
    chapters: list[dict[str, Any]],
    project_type: str = "fiction",
) -> dict[str, Any]:
    """Run scene purpose and chapter purpose analysis for full manuscript."""
    chapter_purposes: list[dict[str, Any]] = []
    scene_purposes: list[dict[str, Any]] = []
    total = len(chapters)

    for i, ch in enumerate(chapters):
        content = ch.get("content") or {}
        chapter_id = str(ch.get("id", ""))
        title = ch.get("title", "Untitled")

        cp = analyze_chapter_purpose(content, i, total, project_type)
        cp["chapter_id"] = chapter_id
        cp["title"] = title
        chapter_purposes.append(cp)

        scenes = analyze_scene_purposes(content, chapter_id, i, title, project_type)
        scene_purposes.extend(scenes)

    return {
        "chapter_purposes": chapter_purposes,
        "scene_purposes": scene_purposes,
        "project_type": project_type,
    }
