"""The twelve questions that test an outline.

Each one is a diagnostic: it reads the material and returns a verdict with
evidence, so a thin middle or an unearned ending is visible before drafting.
"""

from __future__ import annotations

from typing import Any

QUESTIONS: list[dict[str, str]] = [
    {
        "key": "causality",
        "label": "Does each major event follow logically from what came before?",
        "look_for": "Cause and effect between sections. Flag any turn that needs a coincidence, an unexplained arrival or a decision nobody had reason to make.",
    },
    {
        "key": "agency",
        "label": "Do characters make decisions, or do things merely happen to them?",
        "look_for": "Count sections where the protagonist chooses, and where they are acted upon. Passive stretches are a fail even if they are exciting.",
    },
    {
        "key": "personal_stakes",
        "label": "Are the stakes personal as well as external?",
        "look_for": "Name what each main character personally loses. External stakes alone (the world ends) do not carry a book.",
    },
    {
        "key": "relationships",
        "label": "Do relationships change through shared experiences?",
        "look_for": "Track at least one relationship across the outline. If it ends where it began, fail it.",
    },
    {
        "key": "world_inhabited",
        "label": "Does the world feel inhabited beyond the main plot?",
        "look_for": "Evidence of ordinary life, work, ritual, cost, and people with concerns beyond the plot.",
    },
    {
        "key": "quiet_scenes",
        "label": "Are quieter scenes doing useful emotional or dramatic work?",
        "look_for": "Every low-intensity section should still change something: knowledge, allegiance, resolve or cost.",
    },
    {
        "key": "lasting_consequences",
        "label": "Are there consequences that last beyond a single chapter?",
        "look_for": "Trace a decision forward at least two sections. If nothing compounds, the middle will feel weightless.",
    },
    {
        "key": "middle_develops",
        "label": "Does the middle develop rather than repeat the same conflict?",
        "look_for": "Each confrontation should raise the terms of the problem, not restage the previous one with new scenery.",
    },
    {
        "key": "fair_clues",
        "label": "Are mysteries supported by fair clues?",
        "look_for": "Every reveal needs at least one earlier planted clue; every clue needs a reason to exist in the scene.",
    },
    {
        "key": "promise_kept",
        "label": "Does the ending fulfil the book's promise?",
        "look_for": "Compare the opening promise and intended reader experience with what the ending actually delivers.",
    },
    {
        "key": "ending_earned",
        "label": "Is the ending earned by character choices?",
        "look_for": "The resolution must turn on a decision the protagonist made possible by their arc, not on rescue or luck.",
    },
    {
        "key": "sufficient_depth",
        "label": "Does the book have sufficient depth for its intended experience?",
        "look_for": "Judgement call: does the material support the intended length, genre and emotional register, or is it a sketch?",
    },
]

QUESTION_BY_KEY = {q["key"]: q for q in QUESTIONS}
VERDICTS = ("pass", "partial", "fail", "unknown")


def blank_answers() -> dict[str, dict[str, str]]:
    return {q["key"]: {"verdict": "unknown", "note": "", "evidence": ""} for q in QUESTIONS}


def normalise(answers: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    raw = answers or {}
    out: dict[str, dict[str, str]] = {}
    for question in QUESTIONS:
        given = raw.get(question["key"]) or {}
        verdict = str(given.get("verdict", "unknown") or "unknown").lower()
        out[question["key"]] = {
            "verdict": verdict if verdict in VERDICTS else "unknown",
            "note": str(given.get("note", "") or ""),
            "evidence": str(given.get("evidence", "") or ""),
        }
    return out


def summarise(answers: dict[str, Any] | None) -> dict[str, Any]:
    body = normalise(answers)
    counts = {v: 0 for v in VERDICTS}
    for item in body.values():
        counts[item["verdict"]] += 1
    answerable = len(QUESTIONS) - counts["unknown"]
    return {
        "counts": counts,
        "answered": answerable,
        "total": len(QUESTIONS),
        "pct": round(((counts["pass"] + counts["partial"] * 0.5) / len(QUESTIONS)) * 100) if QUESTIONS else 0,
    }
