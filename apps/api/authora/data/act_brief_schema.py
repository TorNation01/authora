"""Act-level outline sheets - what each major section must establish.

The turning points record *what happens*. These sheets record what the
beginning, middle and ending have to accomplish: character movement,
relationships, world, mysteries, subplots, emotional pacing and cause.
"""

from __future__ import annotations

from typing import Any

SECTIONS: list[dict[str, Any]] = [
    {
        "key": "setup",
        "number": 1,
        "title": "Act 1 · Setup",
        "intro": "Ordinary life, the people inside it, and the thing that breaks it open.",
        "fields": [
            {
                "key": "ordinary_life",
                "label": "Ordinary life before the disruption",
                "type": "text",
                "prompt": "The lived texture, not the premise. What does a normal day look like for these people?",
                "ai": True,
            },
            {
                "key": "who_we_follow",
                "label": "Who we are following",
                "type": "short",
                "prompt": "The character or characters the opening belongs to, and why them.",
                "ai": True,
            },
            {
                "key": "what_they_want",
                "label": "What they want",
                "type": "text",
                "prompt": "The concrete want that drives the opening, before the larger story takes over.",
                "ai": True,
            },
            {
                "key": "already_wrong",
                "label": "What is already wrong or unstable",
                "type": "text",
                "prompt": "The fault line that exists before anything happens. Good openings show the crack, not just the calm.",
                "ai": True,
            },
            {
                "key": "world_to_understand",
                "label": "What the reader must understand about the world",
                "type": "text",
                "prompt": "The minimum the reader needs to follow the story, delivered through experience rather than explanation.",
                "ai": True,
            },
            {
                "key": "what_changes",
                "label": "What changes",
                "type": "text",
                "prompt": "The disruption itself, and what it makes impossible to continue.",
                "ai": True,
            },
            {
                "key": "opening_question",
                "label": "The question that makes the reader continue",
                "type": "text",
                "prompt": "The promise the opening makes. One question, asked clearly enough to pull.",
                "ai": True,
            },
        ],
    },
    {
        "key": "confrontation",
        "number": 2,
        "title": "Act 2 · Confrontation",
        "intro": "Response, escalation and the consequences that change the direction of the story.",
        "fields": [
            {
                "key": "response",
                "label": "How the character responds",
                "type": "text",
                "prompt": "The first attempt, and why it is not enough.",
                "ai": True,
            },
            {
                "key": "new_difficulties",
                "label": "New difficulties that arise",
                "type": "text",
                "prompt": "Pressure that comes from the character's own choices, not from coincidence.",
                "ai": True,
            },
            {
                "key": "discoveries",
                "label": "What they discover",
                "type": "text",
                "prompt": "Information that changes what the reader and the character believe.",
                "ai": True,
            },
            {
                "key": "relationships",
                "label": "How relationships develop",
                "type": "text",
                "prompt": "Who moves closer, who fractures, and over what.",
                "ai": True,
            },
            {
                "key": "world_complexity",
                "label": "How the world becomes more complex",
                "type": "text",
                "prompt": "The second layer of the world: institutions, costs, factions, history.",
                "ai": True,
            },
            {
                "key": "choices_consequences",
                "label": "Which choices create consequences",
                "type": "text",
                "prompt": "The decisions that cannot be undone, and what they cost.",
                "ai": True,
            },
            {
                "key": "direction_change",
                "label": "What changes the direction of the story",
                "type": "text",
                "prompt": "The midpoint turn — the moment the story stops being about what it was about.",
                "ai": True,
            },
            {
                "key": "misunderstanding",
                "label": "What the character misunderstands or gets wrong",
                "type": "text",
                "prompt": "The wrong belief that drives the middle. Name it precisely.",
                "ai": True,
            },
        ],
    },
    {
        "key": "resolution",
        "number": 3,
        "title": "Act 3 · Resolution",
        "intro": "The confrontation, the cost, and what is left standing afterwards.",
        "fields": [
            {
                "key": "final_confrontation",
                "label": "What forces the final confrontation or decision",
                "type": "text",
                "prompt": "The pressure that removes the option of waiting.",
                "ai": True,
            },
            {
                "key": "what_risk",
                "label": "What the protagonist risks",
                "type": "text",
                "prompt": "What they stand to lose, stated concretely.",
                "ai": True,
            },
            {
                "key": "choices_effect",
                "label": "How their choices affect the outcome",
                "type": "text",
                "prompt": "The causal link between who they became and how it ends.",
                "ai": True,
            },
            {
                "key": "threads_resolved",
                "label": "Which threads are resolved",
                "type": "text",
                "prompt": "The promises the book has to keep, and the ones it deliberately leaves open.",
                "ai": True,
            },
            {
                "key": "emotional_consequence",
                "label": "The emotional consequence",
                "type": "text",
                "prompt": "What the ending asks the reader to feel, and what it refuses to soften.",
                "ai": True,
            },
            {
                "key": "world_character_change",
                "label": "How the world or character has changed",
                "type": "text",
                "prompt": "The measurable difference between the first page and the last.",
                "ai": True,
            },
            {
                "key": "carries_forward",
                "label": "What continues into the next book",
                "type": "text",
                "prompt": "Threads left live on purpose, and the question the next book inherits.",
                "ai": True,
            },
        ],
    },
]

SECTION_BY_KEY = {s["key"]: s for s in SECTIONS}

GENERIC_FIELDS: list[dict[str, Any]] = [
    {"key": "act_purpose", "label": "What this act must accomplish", "type": "text",
     "prompt": "The job this act does in the whole book. If it were cut, what would the reader lose?", "ai": True},
    {"key": "what_changes", "label": "What changes by the end of the act", "type": "text",
     "prompt": "The state of the story at the curtain. Nothing should be where it was.", "ai": True},
    {"key": "who_drives", "label": "Who drives this act", "type": "short",
     "prompt": "Whose choices move the story here, and what do they want?", "ai": True},
    {"key": "escalation", "label": "How the pressure escalates", "type": "text",
     "prompt": "Each beat should cost more than the last. What is the ladder?", "ai": True},
    {"key": "relations", "label": "What shifts between people", "type": "text",
     "prompt": "Alliances, debts, resentments. Who is closer or further apart by the end?", "ai": True},
    {"key": "world", "label": "What the reader learns about the world", "type": "text",
     "prompt": "The world widening, or a rule becoming concrete under pressure.", "ai": True},
    {"key": "subplots", "label": "Subplots advanced", "type": "text",
     "prompt": "Which subplots move, and what do they add to the main line?", "ai": True},
    {"key": "mysteries", "label": "Mysteries opened, deepened or paid off", "type": "text",
     "prompt": "What the reader is now asking, and what they are allowed to close.", "ai": True},
    {"key": "turning_point", "label": "The turning point inside this act", "type": "text",
     "prompt": "The irreversible moment that spins the act toward its end.", "ai": True},
    {"key": "handoff", "label": "How it hands off to the next act", "type": "text",
     "prompt": "The open question or new problem that pulls the reader over the line.", "ai": True},
]


def act_section(key: str, title: str | None = None, position: int | None = None) -> dict[str, Any]:
    """Return the questionnaire for any act key, including ones the author adds later."""
    if key in SECTION_BY_KEY:
        section = dict(SECTION_BY_KEY[key])
        if title:
            section["title"] = title
        if position is not None:
            section["number"] = position
        return section
    number = position
    if number is None:
        try:
            number = int(key.rsplit("_", 1)[-1])
        except ValueError:
            number = 0
    return {
        "key": key,
        "number": number,
        "title": title or f"Act {number}",
        "intro": "An act the author defined. Same discipline as the first three: what it must accomplish and what it changes.",
        "fields": GENERIC_FIELDS,
    }

FIELDS = [f for s in SECTIONS for f in s["fields"]]
FIELD_BY_KEY = {f["key"]: f for f in FIELDS}


def blank_sections() -> dict[str, dict[str, str]]:
    return {s["key"]: {f["key"]: "" for f in s["fields"]} for s in SECTIONS}


def normalise(sections: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    raw = sections or {}
    out: dict[str, dict[str, str]] = {}
    keys = [s["key"] for s in SECTIONS]
    keys += [k for k in raw if k not in keys and str(k).startswith("act_")]
    for key in keys:
        section = act_section(key)
        given = raw.get(key) or {}
        out[key] = {
            f["key"]: str(given.get(f["key"], "") or "") for f in section["fields"]
        }
    return out


def merge_sections(
    existing: dict[str, Any] | None, incoming: dict[str, Any] | None
) -> dict[str, Any]:
    merged = normalise(existing)
    for key, values in (incoming or {}).items():
        if key in merged and isinstance(values, dict):
            merged[key].update({k: v for k, v in values.items() if k in merged[key]})
    return merged


def filled_count(sections: dict[str, Any] | None) -> int:
    body = normalise(sections)
    return sum(1 for section in body.values() for value in section.values() if str(value).strip())
