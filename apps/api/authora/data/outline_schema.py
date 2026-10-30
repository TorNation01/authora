"""Turning points - the Overall Outline layer.

A book's spine, built as an ordered list of turning points. Each one answers
the same eleven questions, so a section can be judged before it is written:
what happens, who is in it, what they want, what stands in the way, how it
moves them, what it reveals, what it costs, what it sets up, and roughly
which chapters it covers.
"""

from __future__ import annotations

from typing import Any

TITLE_FIELD = "title"

FIELDS: list[dict[str, Any]] = [
    {
        "key": "what_happens",
        "label": "What happens",
        "type": "text",
        "prompt": "The event, in plain sequence. If it needs two paragraphs, it is probably two turning points.",
        "ai": True,
    },
    {
        "key": "characters_involved",
        "label": "Characters involved",
        "type": "list",
        "prompt": "Who is in the scene that matters, one per line.",
        "ai": True,
    },
    {
        "key": "character_objective",
        "label": "Character objective",
        "type": "text",
        "prompt": "What the viewpoint character is trying to achieve in this section — not the book's goal, this scene's.",
        "ai": True,
    },
    {
        "key": "opposition",
        "label": "Opposition or complication",
        "type": "text",
        "prompt": "What stands in the way here: a person, a rule, a lie, their own flaw.",
        "ai": True,
    },
    {
        "key": "emotional_movement",
        "label": "Emotional movement",
        "type": "text",
        "prompt": "Where the feeling starts and where it ends. 'Relief into dread' is enough.",
        "ai": True,
    },
    {
        "key": "relationship_development",
        "label": "Relationship development",
        "type": "text",
        "prompt": "Which bond changes, and how. One-way bonds count — she may decide he is a rival while he never notices.",
        "ai": True,
    },
    {
        "key": "worldbuilding",
        "label": "Worldbuilding revealed through the action",
        "type": "text",
        "prompt": "What the reader learns about how this world works because someone needed something, not because it was explained.",
        "ai": True,
    },
    {
        "key": "new_information",
        "label": "New information / clues",
        "type": "text",
        "prompt": "What the reader or the character now knows that they did not before. Be exact about who learns it.",
        "ai": True,
    },
    {
        "key": "consequence",
        "label": "Consequence",
        "type": "text",
        "prompt": "What cannot be undone after this. The story should be unable to go back to how it was.",
        "ai": True,
    },
    {
        "key": "sets_up",
        "label": "What this sets up",
        "type": "text",
        "prompt": "The debt this section creates, and roughly when it must be paid.",
        "ai": True,
    },
    {
        "key": "chapter_range",
        "label": "Approximate chapter range",
        "type": "short",
        "prompt": "A range is fine — 'ch 4-6'. It will move; write it down anyway so the shape is visible.",
        "ai": False,
    },
]

FIELD_BY_KEY = {field["key"]: field for field in FIELDS}
TOTAL_FIELDS = len(FIELDS)


def blank_fields() -> dict[str, Any]:
    return {field["key"]: ([] if field["type"] == "list" else "") for field in FIELDS}


def normalise(fields: dict[str, Any] | None) -> dict[str, Any]:
    merged = blank_fields()
    for key, value in (fields or {}).items():
        if key in merged:
            merged[key] = value
    return merged


def filled_count(fields: dict[str, Any] | None) -> int:
    body = normalise(fields)
    count = 0
    for field in FIELDS:
        value = body.get(field["key"])
        if isinstance(value, list):
            if any(str(item).strip() for item in value):
                count += 1
        elif str(value or "").strip():
            count += 1
    return count
