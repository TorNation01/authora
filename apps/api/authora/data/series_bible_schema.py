"""The Series Bible questionnaire.

Canon that sits above any single book: what must be respected before new
material is written. Same shape as the book bible - sections, fields, prompts -
so the web app can render it with the same controls.
"""

from __future__ import annotations

from typing import Any

SECTIONS: list[dict[str, Any]] = [
    {
        "key": "series_identity",
        "number": 1,
        "title": "Series Identity",
        "intro": "What the series is, in the terms a reader would use to find it.",
        "fields": [
            {"key": "series_title", "label": "Series title", "type": "short", "prompt": "What is the series called?"},
            {"key": "genre", "label": "Genre and shelf", "type": "short", "prompt": "Where does this series sit in a bookshop?"},
            {"key": "audience", "label": "Target audience", "type": "short", "prompt": "Who reads book one, and who is still reading by book five?"},
            {"key": "series_promise", "label": "The promise of the series", "type": "text", "prompt": "What does a reader get from any book in this series, whatever the plot?", "ai": True},
            {"key": "tone_voice", "label": "Tone and voice", "type": "text", "prompt": "The register that must not drift between books."},
            {"key": "content_rules", "label": "Content rules", "type": "text", "prompt": "Language, violence, heat, on-page limits. Binding on every book."},
            {"key": "reading_order", "label": "Reading order", "type": "text", "prompt": "Publication order, chronological order, and which books can stand alone."},
        ],
    },
    {
        "key": "locked_canon",
        "number": 2,
        "title": "Locked Canon",
        "intro": "Hard facts. If a new draft contradicts one of these, the draft is wrong.",
        "fields": [
            {"key": "hard_facts", "label": "Facts that cannot change", "type": "list", "prompt": "One fact per line. Dates, deaths, names, outcomes already on the page."},
            {"key": "world_rules", "label": "Rules of the world", "type": "list", "prompt": "Physics, magic, technology, institutions - what is possible and what is not."},
            {"key": "geography", "label": "Geography and places", "type": "list", "prompt": "Fixed locations, distances, and what sits where."},
            {"key": "power_structures", "label": "Power structures", "type": "text", "prompt": "Who rules, who serves, who is outside the law - and how that changes across books."},
            {"key": "technology_or_magic_limits", "label": "Costs and limits", "type": "text", "prompt": "What every use of power costs, and what it can never do."},
            {"key": "retcon_rules", "label": "What may be retconned", "type": "text", "prompt": "The narrow set of things later books are allowed to reinterpret, and the condition."},
        ],
    },
    {
        "key": "continuing_characters",
        "number": 3,
        "title": "Continuing Characters",
        "intro": "Who carries over, and the state they must be in when a new book opens.",
        "fields": [
            {"key": "core_cast", "label": "Core cast and their locked state", "type": "rows", "prompt": "Name, role, where they stand at the start of the next book.", "columns": [{"key": "name", "label": "Name"}, {"key": "role", "label": "Role"}, {"key": "locked_state", "label": "Locked state"}]},
            {"key": "relationships_locked", "label": "Relationships that cannot be reset", "type": "list", "prompt": "Who knows what about whom, and who is permanently changed."},
            {"key": "deaths_and_exits", "label": "Deaths and exits", "type": "list", "prompt": "Who is gone, when, and how the world knows it."},
            {"key": "unavailable_characters", "label": "Characters who must not appear yet", "type": "text", "prompt": "Held back for a later book - and what would break if they appeared early."},
        ],
    },
    {
        "key": "series_arc",
        "number": 4,
        "title": "Series Arc",
        "intro": "The long story the individual books serve.",
        "fields": [
            {"key": "long_arc", "label": "The long arc", "type": "text", "prompt": "Where does the series end, and what has to be true of the world when it does?", "ai": True},
            {"key": "book_jobs", "label": "What each book must accomplish", "type": "rows", "prompt": "Book, its job in the arc, and the state it leaves behind.", "columns": [{"key": "book", "label": "Book"}, {"key": "job", "label": "Job in the arc"}, {"key": "end_state", "label": "Leaves the series"}]},
            {"key": "endgame_status", "label": "Endgame status", "type": "short", "prompt": "locked, working or undecided - and if undecided, the options still open."},
            {"key": "escalation", "label": "Escalation ladder", "type": "text", "prompt": "How the stakes grow without repeating the same crisis five times."},
        ],
    },
    {
        "key": "open_threads",
        "number": 5,
        "title": "Open Threads",
        "intro": "Debts the series owes the reader. Everything here must be paid off eventually.",
        "fields": [
            {"key": "unresolved_questions", "label": "Questions still unanswered", "type": "list", "prompt": "One per line, with the book that should answer it."},
            {"key": "planted_seeds", "label": "Seeds already planted", "type": "list", "prompt": "Details on the page that must pay off later."},
            {"key": "promised_reveals", "label": "Promised reveals", "type": "list", "prompt": "What the reader has been told they will eventually learn."},
            {"key": "dropped_threads", "label": "Threads deliberately dropped", "type": "text", "prompt": "Abandoned on purpose, with the reason, so it is a choice and not an omission."},
        ],
    },
    {
        "key": "prior_books",
        "number": 6,
        "title": "Prior Books",
        "intro": "The state of play after each published book. A new book starts from here.",
        "fields": [
            {"key": "summaries", "label": "Book-by-book state of play", "type": "rows", "prompt": "Book, what changed, what a new reader must know.", "columns": [{"key": "book", "label": "Book"}, {"key": "what_changed", "label": "What changed"}, {"key": "reader_must_know", "label": "Must know"}]},
            {"key": "ending_states", "label": "How each book ends", "type": "list", "prompt": "Final scene and the emotional note it lands on."},
            {"key": "carry_over_damage", "label": "Damage carried forward", "type": "text", "prompt": "Wounds, losses, reputations and consequences that persist."},
        ],
    },
    {
        "key": "decisions_log",
        "number": 7,
        "title": "Decisions Log",
        "intro": "Why canon is the way it is. Prevents the same argument being had twice.",
        "fields": [
            {"key": "locked_decisions", "label": "Locked decisions", "type": "rows", "prompt": "Decision, date, reason.", "columns": [{"key": "decision", "label": "Decision"}, {"key": "date", "label": "Date"}, {"key": "reason", "label": "Why"}]},
            {"key": "rejected_ideas", "label": "Rejected directions", "type": "list", "prompt": "Considered and set aside - so they are not proposed again."},
            {"key": "unresolved_decisions", "label": "Decisions still open", "type": "list", "prompt": "What has to be settled before the next book can be drafted."},
        ],
    },
    {
        "key": "continuity_guard",
        "number": 8,
        "title": "Continuity Guard",
        "intro": "The checks a new draft must survive before it is allowed to become canon.",
        "fields": [
            {"key": "contradiction_risks", "label": "Known contradiction risks", "type": "list", "prompt": "Places where the series is easy to break."},
            {"key": "naming_rules", "label": "Naming rules", "type": "text", "prompt": "How people, places and things are named, and names already used."},
            {"key": "timeline_anchors", "label": "Timeline anchors", "type": "list", "prompt": "Fixed dates and elapsed time between books."},
            {"key": "review_checklist", "label": "Before a draft becomes canon", "type": "text", "prompt": "The short list you actually run, in order."},
        ],
    },
]

SECTION_BY_KEY = {s["key"]: s for s in SECTIONS}


def blank_sections() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for section in SECTIONS:
        body: dict[str, Any] = {}
        for field in section["fields"]:
            body[field["key"]] = [] if field["type"] in ("list", "rows") else ""
        out[section["key"]] = body
    return out


def merge_sections(existing: dict[str, Any] | None, incoming: dict[str, Any]) -> dict[str, Any]:
    merged = dict(existing or {})
    for section in SECTIONS:
        key = section["key"]
        if key not in incoming or not isinstance(incoming[key], dict):
            continue
        current = dict(merged.get(key) or {})
        allowed = {f["key"] for f in section["fields"]}
        for field_key, value in incoming[key].items():
            if field_key in allowed:
                current[field_key] = value
        merged[key] = current
    return merged


def completeness(sections: dict[str, Any]) -> dict[str, Any]:
    total = 0
    filled = 0
    per_section: dict[str, Any] = {}
    for section in SECTIONS:
        body = sections.get(section["key"]) or {}
        s_total = len(section["fields"])
        s_filled = 0
        for field in section["fields"]:
            value = body.get(field["key"])
            if isinstance(value, list):
                hit = len(value) > 0
            else:
                hit = bool(str(value or "").strip())
            s_filled += 1 if hit else 0
        total += s_total
        filled += s_filled
        per_section[section["key"]] = {
            "title": section["title"],
            "filled": s_filled,
            "total": s_total,
            "pct": round(100 * s_filled / s_total) if s_total else 0,
        }
    return {
        "filled": filled,
        "total": total,
        "pct": round(100 * filled / total) if total else 0,
        "sections": per_section,
        "missing": [k for k, v in per_section.items() if v["pct"] < 100],
    }
