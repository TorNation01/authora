"""Chapter Outline - the chapter-by-chapter map.

One sheet per chapter: why it exists, what happens, who changes, where it sits
in the story, what thread it carries, and why the reader turns the page.
Compact enough to see the shape of the whole book, full enough to expose a
chapter that has no job.
"""

from __future__ import annotations

from typing import Any

SECTIONS: list[dict[str, Any]] = [
    {
        "key": "place",
        "number": 0,
        "title": "Place in the Story",
        "intro": "Where this chapter sits. If you cannot say where it sits, it may not need to be here.",
        "fields": [
            {
                "key": "book_section",
                "label": "Book section",
                "type": "short",
                "prompt": "Act, part, movement — which stretch of the book is this chapter in?",
                "ai": True,
            },
            {
                "key": "position_in_timeline",
                "label": "Position in timeline",
                "type": "short",
                "prompt": "Where this falls in story time — immediately after the last chapter, or later.",
                "ai": True,
            },
            {
                "key": "location",
                "label": "Location",
                "type": "short",
                "prompt": "Where the chapter happens. More than one place is fine; say so.",
                "ai": True,
            },
            {
                "key": "pov_character",
                "label": "Point-of-view character",
                "type": "short",
                "prompt": "Whose head are we in. One name unless the chapter is deliberately split.",
                "ai": True,
            },
        ],
    },
    {
        "key": "purpose",
        "number": 1,
        "title": "Chapter Purpose",
        "intro": "The one job this chapter does that no other chapter does.",
        "fields": [
            {
                "key": "purpose",
                "label": "What this chapter needs to achieve",
                "type": "text",
                "prompt": "One sentence. 'Establish the strain on the sanctuary, deepen the tension between Mara and Kael, end on a discovery that changes their priorities.'",
                "ai": True,
            },
        ],
    },
    {
        "key": "happens",
        "number": 2,
        "title": "What Happens",
        "intro": "The sequence, plainly. This is the map, not the prose.",
        "fields": [
            {
                "key": "opening_situation",
                "label": "Opening situation",
                "type": "text",
                "prompt": "The state of things on the first line — where, with whom, in what mood.",
                "ai": True,
            },
            {
                "key": "main_events",
                "label": "Main events",
                "type": "list",
                "prompt": "One event per line, in order. If this list gets long, the chapter may be two chapters.",
                "ai": True,
            },
            {
                "key": "complication",
                "label": "Complication or tension",
                "type": "text",
                "prompt": "What goes wrong, or what makes the obvious move impossible.",
                "ai": True,
            },
            {
                "key": "choice_or_discovery",
                "label": "Choice or discovery",
                "type": "text",
                "prompt": "The turn — what the character decides, or what they learn that they cannot unlearn.",
                "ai": True,
            },
            {
                "key": "consequence",
                "label": "Consequence",
                "type": "text",
                "prompt": "What is now different and cannot be put back.",
                "ai": True,
            },
            {
                "key": "ending",
                "label": "Ending",
                "type": "text",
                "prompt": "How the chapter closes. Not always a cliffhanger — sometimes a quiet realisation does more work.",
                "ai": True,
            },
        ],
    },
    {
        "key": "characters",
        "number": 3,
        "title": "Characters",
        "intro": "Who is in it, and what the chapter does to them.",
        "fields": [
            {
                "key": "characters_present",
                "label": "Characters present",
                "type": "list",
                "prompt": "One per line. Anyone who speaks or changes something.",
                "ai": True,
            },
            {
                "key": "viewpoint_wants",
                "label": "What the viewpoint character wants",
                "type": "text",
                "prompt": "In this chapter, not in the book.",
                "ai": True,
            },
            {
                "key": "obstacle",
                "label": "What stands in their way",
                "type": "text",
                "prompt": "A person, a rule, a shortage, a lie they believe.",
                "ai": True,
            },
            {
                "key": "character_change",
                "label": "What changes for them",
                "type": "text",
                "prompt": "A shift in what they know, want, or are willing to do.",
                "ai": True,
            },
            {
                "key": "relationship_development",
                "label": "Relationship development",
                "type": "text",
                "prompt": "Which bond moves, and in which direction.",
                "ai": True,
            },
        ],
    },
    {
        "key": "threads",
        "number": 4,
        "title": "Story Threads",
        "intro": "The threads this chapter pulls. A chapter that pulls none is a chapter to cut.",
        "fields": [
            {
                "key": "main_plot",
                "label": "Main plot",
                "type": "text",
                "prompt": "What the chapter does for the spine.",
                "ai": True,
            },
            {
                "key": "subplot",
                "label": "Subplot",
                "type": "text",
                "prompt": "The secondary story it advances — or deliberately parks.",
                "ai": True,
            },
            {
                "key": "mystery_clue",
                "label": "Mystery or clue",
                "type": "text",
                "prompt": "What is planted, what is paid off, what is deliberately withheld.",
                "ai": True,
            },
            {
                "key": "worldbuilding",
                "label": "Worldbuilding",
                "type": "text",
                "prompt": "What the reader learns about how this world works, because someone needed something.",
                "ai": True,
            },
            {
                "key": "theme",
                "label": "Theme",
                "type": "text",
                "prompt": "How the book's question shows up in action here, not in speech.",
                "ai": True,
            },
        ],
    },
    {
        "key": "continuity",
        "number": 5,
        "title": "Continuity",
        "intro": "What must be true going in, and what must still be true coming out.",
        "fields": [
            {
                "key": "what_they_know",
                "label": "What the characters know at this point",
                "type": "text",
                "prompt": "The state of knowledge — carefully, because it limits what they can say.",
                "ai": True,
            },
            {
                "key": "earlier_events",
                "label": "Relevant events from earlier chapters",
                "type": "text",
                "prompt": "The handful of prior facts this chapter leans on.",
                "ai": True,
            },
            {
                "key": "must_not_reveal",
                "label": "Information that must not be revealed",
                "type": "text",
                "prompt": "The reveal this chapter is not allowed to make.",
                "ai": True,
            },
            {
                "key": "carry_forward",
                "label": "Details to carry forward",
                "type": "text",
                "prompt": "Objects, injuries, promises, lies in play — what the next chapter must remember.",
                "ai": True,
            },
        ],
    },
    {
        "key": "pacing",
        "number": 6,
        "title": "Pacing",
        "intro": "How it reads, and whether the reader comes with you.",
        "fields": [
            {
                "key": "emotional_tone",
                "label": "Emotional tone",
                "type": "short",
                "prompt": "The dominant note — dread, relief, momentum, grief.",
                "ai": True,
            },
            {
                "key": "approx_length",
                "label": "Approximate length",
                "type": "short",
                "prompt": "A rough word count or page range, if useful. Not a target to pad to.",
                "ai": False,
            },
            {
                "key": "why_continue",
                "label": "Why the reader will continue",
                "type": "text",
                "prompt": "The question left open at the last line. If the answer is 'duty', fix the ending.",
                "ai": True,
            },
        ],
    },
]

SECTION_BY_KEY = {section["key"]: section for section in SECTIONS}
FIELD_BY_KEY = {field["key"]: field for section in SECTIONS for field in section["fields"]}
FIELDS: list[dict[str, Any]] = [f for s in SECTIONS for f in s["fields"]]
TOTAL_FIELDS = len(FIELD_BY_KEY)


def blank_sections() -> dict[str, Any]:
    return {
        section["key"]: {
            field["key"]: ([] if field["type"] == "list" else "")
            for field in section["fields"]
        }
        for section in SECTIONS
    }


def normalise(sections: dict[str, Any] | None) -> dict[str, Any]:
    merged = blank_sections()
    for key, body in (sections or {}).items():
        if key in merged and isinstance(body, dict):
            for field_key, value in body.items():
                if field_key in merged[key]:
                    merged[key][field_key] = value
    return merged


def completeness(sections: dict[str, Any] | None) -> dict[str, Any]:
    body = normalise(sections)
    filled = 0
    for section in SECTIONS:
        for field in section["fields"]:
            value = body[section["key"]][field["key"]]
            if isinstance(value, list):
                if any(str(item).strip() for item in value):
                    filled += 1
            elif str(value or "").strip():
                filled += 1
    return {
        "filled": filled,
        "total": TOTAL_FIELDS,
        "pct": round(filled / TOTAL_FIELDS * 100) if TOTAL_FIELDS else 0,
    }
