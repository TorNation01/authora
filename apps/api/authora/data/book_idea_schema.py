"""The Overall Book Idea - the first layer of the planning ladder.

A single structured sheet per book: the pitch, the story spine, the emotional
core, themes, the promise made to the reader, the ending, and how the book
sits in the series. Deliberately blunt fields - one question per field, the
author answers in prose.
"""

from __future__ import annotations

from typing import Any

SECTIONS: list[dict[str, Any]] = [
    {
        "key": "header",
        "number": 0,
        "title": "The Book",
        "intro": "The facts that sit on the cover and in the metadata. Fill them once.",
        "fields": [
            {"key": "working_title", "label": "Working title", "type": "short", "prompt": "What you are calling it for now."},
            {"key": "series", "label": "Series", "type": "short", "prompt": "Leave blank if it stands alone."},
            {"key": "position_in_series", "label": "Position in series", "type": "short", "prompt": "Book one, book two, a prequel, a side story."},
            {"key": "author", "label": "Author", "type": "short", "prompt": "The name that goes on the spine."},
            {"key": "genre", "label": "Genre and subgenre", "type": "short", "prompt": "Be specific enough that a reader could find it on a shelf."},
            {"key": "target_audience", "label": "Target audience", "type": "short", "prompt": "Who this is written for, and what they already read."},
            {"key": "preferred_length", "label": "Preferred length", "type": "short", "prompt": "Target word count."},
            {
                "key": "reading_experience",
                "label": "Intended reading experience",
                "type": "short",
                "prompt": "What the reader should feel: dread, wonder, urgency, heartbreak, hope.",
                "ai": False,
            },
            {
                "key": "standalone_or_series",
                "label": "Standalone or series-dependent",
                "type": "short",
                "prompt": "How much resolves in this book, and what carries forward.",
                "ai": False,
            },
            {
                "key": "length_flexibility",
                "label": "Length flexibility / review point",
                "type": "short",
                "prompt": "How much the length may move, and the point where you would stop and reassess.",
            },
        ],
    },
    {
        "key": "core",
        "number": 1,
        "title": "The Core Idea",
        "intro": "If you could only keep one page, it would be this one.",
        "fields": [
            {"key": "one_sentence_premise", "label": "One-sentence premise", "type": "text", "prompt": "Who wants what, what stands in the way, and what it costs. One sentence, no commas doing the work of a paragraph.", "ai": True},
            {"key": "short_premise", "label": "Short premise", "type": "text", "prompt": "One paragraph. The version you would say out loud to someone in a lift.", "ai": True},
            {"key": "distinctive", "label": "What makes this book distinctive", "type": "text", "prompt": "Why this book and not the twenty others in the same genre. Be honest about what is genuinely new here.", "ai": True},
        ],
    },
    {
        "key": "story",
        "number": 2,
        "title": "The Story",
        "intro": "The spine. Situation, disruption, objective, opposition, stakes.",
        "fields": [
            {"key": "main_characters", "label": "Main character or characters", "type": "text", "prompt": "Who the book belongs to, in one line each.", "ai": True},
            {"key": "situation_at_start", "label": "The situation at the beginning", "type": "text", "prompt": "Life before anything changes. What is already wrong that they have learned to live with.", "ai": True},
            {"key": "disrupting_event", "label": "The event that disrupts the situation", "type": "text", "prompt": "The door that opens or closes. After this, the old life is not available.", "ai": True},
            {"key": "main_objective", "label": "The main objective", "type": "text", "prompt": "What they are now trying to do — concrete enough that the reader can tell whether they are winning.", "ai": True},
            {"key": "opposition", "label": "Primary opposition or obstacle", "type": "text", "prompt": "The person, force or flaw that stands in the way, and why it cannot simply be walked around.", "ai": True},
            {"key": "what_happens_if_they_fail", "label": "What happens if the characters fail", "type": "text", "prompt": "The cost of losing. Make it specific and personal, not 'the world ends'.", "ai": True},
        ],
    },
    {
        "key": "emotional",
        "number": 3,
        "title": "Emotional Core",
        "intro": "The book beneath the plot.",
        "fields": [
            {"key": "really_about", "label": "What the story is really about emotionally", "type": "text", "prompt": "The human question the plot is carrying.", "ai": True},
            {"key": "key_relationships", "label": "Key relationships", "type": "text", "prompt": "The two or three bonds the book turns on, and the tension inside each.", "ai": True},
            {"key": "reader_feeling", "label": "What the reader should feel", "type": "text", "prompt": "Along the way, and at the moment it lands.", "ai": True},
            {"key": "what_remains", "label": "What should remain with the reader after the ending", "type": "text", "prompt": "The thought that follows them out of the last page.", "ai": True},
        ],
    },
    {
        "key": "themes",
        "number": 4,
        "title": "Themes",
        "intro": "The ideas the book explores. Each row pairs a theme with the question it asks, who feels it differently, and where it bites.",
        "fields": [
            {
                "key": "theme_rows",
                "label": "Themes, one row each",
                "type": "rows",
                "prompt": "Theme, the question it asks, who experiences it differently, and the choice that puts it under pressure.",
                "columns": [
                    {"key": "theme", "label": "Theme"},
                    {"key": "story_question", "label": "Story question"},
                    {"key": "character_connection", "label": "Which characters experience it differently"},
                    {"key": "dramatic_expression", "label": "How it appears through choices and consequences"},
                ],
                "ai": False,
            },
            {
                "key": "how_they_appear",
                "label": "How those questions surface through events",
                "type": "text",
                "prompt": "Which scene forces each question. The theme should land through the story, never through a character explaining it.",
                "ai": True,
            },
        ],
    },
    {
        "key": "questions",
        "number": 5,
        "title": "The Story Questions",
        "intro": "The four questions the idea must answer that the sections above do not already cover.",
        "fields": [
            {
                "key": "whose_story",
                "label": "Whose story is this",
                "type": "short",
                "prompt": "The person the book belongs to — not necessarily the narrator.",
                "ai": True,
            },
            {
                "key": "why_now",
                "label": "Why the story has to happen now",
                "type": "text",
                "prompt": "What makes this moment different from every earlier moment these people could have acted.",
                "ai": True,
            },
            {
                "key": "emotional_journey",
                "label": "The emotional journey",
                "type": "text",
                "prompt": "The feeling the reader enters with, and the one they leave with.",
                "ai": True,
            },
            {
                "key": "distinctive_in_genre",
                "label": "What makes it different from others in the genre",
                "type": "text",
                "prompt": "The specific thing this book does that the shelf does not.",
                "ai": True,
            },
        ],
    },
    {
        "key": "promise",
        "number": 6,
        "title": "Reader Promise",
        "intro": "What the cover and the first page promise. Break it and readers leave.",
        "fields": [
            {"key": "hook", "label": "The hook", "type": "text", "prompt": "The line or image that makes someone open it.", "ai": True},
            {"key": "what_readers_expect", "label": "What readers will expect the story to deliver", "type": "text", "prompt": "Given the genre, the title and the opening — what they have been promised.", "ai": True},
            {"key": "balance", "label": "Intended balance of action, character, worldbuilding and mystery", "type": "text", "prompt": "Rough proportions, and which one this book is really selling.", "ai": True},
        ],
    },
    {
        "key": "ending",
        "number": 7,
        "title": "Ending",
        "intro": "Know where it lands before you write chapter one.",
        "fields": [
            {"key": "main_resolution", "label": "Main resolution", "type": "text", "prompt": "How the central problem is settled, and who settles it.", "ai": True},
            {"key": "character_change", "label": "Character change", "type": "text", "prompt": "Who they are at the end that they could not have been at the start.", "ai": True},
            {"key": "emotional_payoff", "label": "Emotional payoff", "type": "text", "prompt": "The moment the reader has been waiting for, and why it earns itself.", "ai": True},
            {"key": "questions_left_open", "label": "Questions left open", "type": "list", "prompt": "What is deliberately unanswered, one per line.", "ai": True},
            {"key": "leads_into_next", "label": "What leads into the next book", "type": "text", "prompt": "The thread that pulls the reader forward without cheating this ending.", "ai": True},
        ],
    },
    {
        "key": "series",
        "number": 8,
        "title": "Series Connection",
        "intro": "The book's job inside the larger story.",
        "fields": [
            {"key": "contributes", "label": "What this book contributes to the wider series", "type": "text", "prompt": "The piece of the larger story that only this book delivers.", "ai": True},
            {"key": "established_canon", "label": "Important established canon", "type": "text", "prompt": "Facts from earlier books this one must honour.", "ai": True},
            {"key": "must_not_reveal", "label": "Future events that must not be revealed too early", "type": "text", "prompt": "What the draft is not allowed to spend yet, however tempting.", "ai": True},
        ],
    },
    {
        "key": "open",
        "number": 9,
        "title": "Open Questions",
        "intro": "Park what you have not decided. A written question stops circling your head.",
        "fields": [
            {"key": "decisions", "label": "Decisions still to make", "type": "list", "prompt": "One per line.", "ai": False},
            {"key": "ideas", "label": "Ideas to explore", "type": "list", "prompt": "One per line. No commitment.", "ai": False},
        ],
    },
]

TOTAL_FIELDS = sum(len(section["fields"]) for section in SECTIONS)


def section_by_key(key: str) -> dict[str, Any] | None:
    return next((section for section in SECTIONS if section["key"] == key), None)


def blank_sections() -> dict[str, dict[str, Any]]:
    blank: dict[str, dict[str, Any]] = {}
    for section in SECTIONS:
        values: dict[str, Any] = {}
        for field in section["fields"]:
            values[field["key"]] = [] if field["type"] == "list" else ""
        blank[section["key"]] = values
    return blank


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                if any(str(v).strip() for v in item.values()):
                    return True
            elif str(item).strip():
                return True
        return False
    return bool(value)


def completeness(sections: dict[str, Any] | None) -> dict[str, Any]:
    sections = sections or {}
    filled_total = 0
    per_section: dict[str, dict[str, Any]] = {}
    for section in SECTIONS:
        values = sections.get(section["key"]) or {}
        filled = sum(1 for field in section["fields"] if _is_filled(values.get(field["key"])))
        total = len(section["fields"])
        filled_total += filled
        per_section[section["key"]] = {
            "title": section["title"],
            "filled": filled,
            "total": total,
            "pct": round(filled / total * 100) if total else 0,
        }
    return {
        "pct": round(filled_total / TOTAL_FIELDS * 100) if TOTAL_FIELDS else 0,
        "filled": filled_total,
        "total": TOTAL_FIELDS,
        "sections": per_section,
    }


def merge_sections(current: dict[str, Any] | None, incoming: dict[str, Any] | None) -> dict[str, Any]:
    merged = blank_sections()
    for section_key, values in (current or {}).items():
        if section_key in merged and isinstance(values, dict):
            merged[section_key].update(values)
    for section_key, values in (incoming or {}).items():
        if section_key not in merged or not isinstance(values, dict):
            continue
        section = section_by_key(section_key)
        allowed = {field["key"] for field in (section or {}).get("fields", [])}
        for field_key, value in values.items():
            if field_key in allowed:
                merged[section_key][field_key] = value
    return merged
