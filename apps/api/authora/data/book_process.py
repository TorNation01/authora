"""The repeatable process - nine steps every book runs, and the review questions.

Each step names its output and the question that tells you it is finished.
The process endpoint derives each step's state from the material that actually
exists, so the workflow cannot drift out of sync with the book.
"""

from __future__ import annotations

from typing import Any

STEPS: list[dict[str, Any]] = [
    {
        "key": "idea",
        "number": 1,
        "title": "Establish the idea",
        "purpose": "Complete the overall book idea.",
        "output": "Premise and creative direction",
        "check": "Is there enough story here for a full book, and do we know what makes it compelling?",
        "surface": "idea",
    },
    {
        "key": "canon",
        "number": 2,
        "title": "Gather existing canon",
        "purpose": "Collect the series bible, previous summaries, profiles, timeline, open threads and locked decisions.",
        "output": "What must be respected before new material",
        "check": "Do we know exactly what cannot be contradicted?",
        "surface": "series",
    },
    {
        "key": "characters",
        "number": 3,
        "title": "Develop the characters",
        "purpose": "Create or update character profiles.",
        "output": "Detailed character records",
        "check": "Can each major character make meaningful choices based on who they are?",
        "surface": "bible",
    },
    {
        "key": "bible",
        "number": 4,
        "title": "Build the book bible",
        "purpose": "Bring premise, characters, world, format, tone, themes, continuity and plot direction into one place.",
        "output": "Story reference and canon",
        "check": "Are locked facts, working ideas and unresolved decisions clearly separated?",
        "surface": "bible",
    },
    {
        "key": "outline",
        "number": 5,
        "title": "Build the overall outline",
        "purpose": "Map main plot, subplots, character arcs, relationship arcs, worldbuilding and reveals.",
        "output": "Major events and arcs",
        "check": "Does the middle have enough depth and escalation? Does the ending fulfil the promise?",
        "surface": "outline",
    },
    {
        "key": "chapter_outline",
        "number": 6,
        "title": "Build the chapter outlines",
        "purpose": "Break the outline into chapters.",
        "output": "Chapter-by-chapter map",
        "check": "Are chapters varied in function and pacing, with room for relationships and world?",
        "surface": "chapter-outline",
    },
    {
        "key": "briefs",
        "number": 7,
        "title": "Prepare chapter briefs",
        "purpose": "Create a detailed brief for the chapter being written.",
        "output": "Scene guidance",
        "check": "Does the brief give direction without prescribing every sentence?",
        "surface": "brief",
    },
    {
        "key": "write_review",
        "number": 8,
        "title": "Write and review",
        "purpose": "Draft chapters, then review progression, consistency, depth, scene work, continuity, pacing and prose.",
        "output": "Drafted chapters and revisions",
        "check": "Does each chapter achieve its purpose without repeating the last one?",
        "surface": "ghostwriter",
    },
    {
        "key": "manuscript_review",
        "number": 9,
        "title": "Review the complete manuscript",
        "purpose": "Judge the book as a whole and decide whether it needs more, less or different material.",
        "output": "Findings and revisions",
        "check": "Is this the book it promised to be, at the depth it needs?",
        "surface": None,
    },
]

STEP_BY_KEY = {s["key"]: s for s in STEPS}

MANUSCRIPT_QUESTIONS: list[dict[str, str]] = [
    {
        "key": "promise_fulfilled",
        "label": "Does the opening make a promise the ending fulfils?",
        "look_for": "Compare the first chapter's promise with the final chapter's delivery.",
    },
    {
        "key": "characters_developed",
        "label": "Are the characters fully developed?",
        "look_for": "Evidence of want, contradiction, change and cost across the draft.",
    },
    {
        "key": "world_lived_in",
        "label": "Does the world feel lived in?",
        "look_for": "Texture beyond the plot: work, ritual, ordinary people, consequence.",
    },
    {
        "key": "sufficient_depth",
        "label": "Does the story have enough depth?",
        "look_for": "Whether scenes are given room, or whether only plot remains.",
    },
    {
        "key": "scenes_breathe",
        "label": "Are scenes allowed to breathe?",
        "look_for": "Scenes that exist for tension, relationship or place rather than transit.",
    },
    {
        "key": "no_repetition",
        "label": "Does anything repeat without developing?",
        "look_for": "Repeated beats, restated information, recurring arguments that never escalate.",
    },
    {
        "key": "ending_earned",
        "label": "Are the ending and reveals earned?",
        "look_for": "Clues planted, choices set up, reversals prepared.",
    },
    {
        "key": "series_consistent",
        "label": "Are series connections clear and consistent?",
        "look_for": "Continuity with prior books and with locked future developments.",
    },
    {
        "key": "right_shape",
        "label": "Does the book need more, less, or simply different material?",
        "look_for": "A direct recommendation, not a hedge.",
    },
]

REVIEW_VERDICTS = ("pass", "partial", "fail", "unknown")


def blank_review() -> dict[str, dict[str, str]]:
    return {q["key"]: {"verdict": "unknown", "note": "", "evidence": ""} for q in MANUSCRIPT_QUESTIONS}


def normalise_review(answers: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    raw = answers or {}
    out: dict[str, dict[str, str]] = {}
    for question in MANUSCRIPT_QUESTIONS:
        given = raw.get(question["key"]) or {}
        verdict = str(given.get("verdict", "unknown") or "unknown").lower()
        out[question["key"]] = {
            "verdict": verdict if verdict in REVIEW_VERDICTS else "unknown",
            "note": str(given.get("note", "") or ""),
            "evidence": str(given.get("evidence", "") or ""),
        }
    return out


def summarise_review(answers: dict[str, Any] | None) -> dict[str, Any]:
    body = normalise_review(answers)
    counts = {v: 0 for v in REVIEW_VERDICTS}
    for item in body.values():
        counts[item["verdict"]] += 1
    total = len(MANUSCRIPT_QUESTIONS)
    return {
        "counts": counts,
        "answered": total - counts["unknown"],
        "total": total,
        "pct": round(((counts["pass"] + counts["partial"] * 0.5) / total) * 100) if total else 0,
    }
