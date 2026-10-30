"""The Chapter Brief questionnaire.

Single source of truth for the per-chapter brief: section order, field keys,
labels, control types and the prompt shown under each field. The API serves
this to the web app, so a new field only has to be added here.

Built directly from the author's CHAPTER BRIEF specification: a book bible
describes the whole book, a brief describes one chapter in enough detail that
a ghostwriter (or the AI) can draft it without guessing.
"""

from typing import Any

QUALITY_CHECKS: list[str] = [
    "Does the chapter contain a fully developed scene?",
    "Do characters make meaningful choices?",
    "Does the world feel present and lived in?",
    "Are reactions and consequences given enough space?",
    "Is dialogue distinct and natural?",
    "Is the chapter consistent with the bible?",
    "Does it move the story or relationships forward?",
    "Is the ending appropriate to this chapter?",
    "Does every fact here stay inside the bible\u2019s canon?",
    "Is the prose free of repetition and over-explanation?",
    "Are character voices distinct from one another?",
    "Is the length determined by what the scene needs, not by a target?",
]

SECTIONS: list[dict[str, Any]] = [
    {
        "key": "identity",
        "number": 0,
        "title": "Chapter Details",
        "intro": "The label on the tin. Most of this can be pulled straight from the bible.",
        "fields": [
            {"key": "book", "label": "Book", "type": "short", "prompt": "Which book this chapter belongs to."},
            {"key": "series", "label": "Series", "type": "short", "prompt": "The series, if there is one."},
            {"key": "chapter_number", "label": "Chapter number", "type": "short", "prompt": "Its number in the book."},
            {"key": "working_title", "label": "Working title", "type": "short", "prompt": "A working name for the chapter. Change it whenever."},
            {"key": "position_in_story", "label": "Position in story", "type": "short", "prompt": "Where it sits — Act 2, opening chapter, the turn before the climax."},
            {"key": "pov", "label": "Point of view", "type": "short", "prompt": "Whose head are we in, and what kind of POV?"},
            {"key": "tense", "label": "Tense", "type": "short", "prompt": "Past or present. Keep it the same as the book."},
            {"key": "location", "label": "Location", "type": "short", "prompt": "Where the chapter happens."},
            {"key": "time_date", "label": "Time / date", "type": "short", "prompt": "When it happens, relative to the last chapter."},
            {"key": "length_guidance", "label": "Length guidance", "type": "short", "prompt": "Target word count for this chapter."},
        ],
    },
    {
        "key": "purpose",
        "number": 1,
        "title": "Chapter Purpose",
        "intro": "If you cannot say these two things, the chapter should not exist yet.",
        "fields": [
            {"key": "what_must_accomplish", "label": "What this chapter must accomplish", "type": "text", "prompt": "The job it does for the book. One clear outcome.", "ai": True},
            {"key": "why_matters", "label": "Why this chapter matters to the book", "type": "text", "prompt": "What breaks if this chapter is cut?", "ai": True},
        ],
    },
    {
        "key": "starting_conditions",
        "number": 2,
        "title": "Starting Conditions",
        "intro": "The state of the world on the first line — so the chapter starts where the last one left off.",
        "fields": [
            {"key": "what_happened_before", "label": "What happened immediately before", "type": "text", "prompt": "The last beat of the previous chapter, in one or two sentences."},
            {"key": "where_character_is", "label": "Where the viewpoint character is", "type": "text", "prompt": "Room, city, weather, time of day — the physical reality of the opening."},
            {"key": "emotional_state", "label": "Their emotional state", "type": "text", "prompt": "What they are carrying in. Be specific — anger at whom, afraid of what."},
            {"key": "what_they_know", "label": "What they know", "type": "list", "prompt": "Facts in their possession at the start. Bullet points."},
            {"key": "what_they_believe", "label": "What they believe", "type": "list", "prompt": "Things they hold as true that may be wrong. This is where irony lives."},
            {"key": "what_they_do_not_know", "label": "What they do not know", "type": "list", "prompt": "The gaps the reader may or may not share."},
            {"key": "physical_continuity", "label": "Relevant physical continuity", "type": "text", "prompt": "Injuries, objects, clothing, who is holding what — anything a reader would notice."},
        ],
    },
    {
        "key": "characters_present",
        "number": 3,
        "title": "Characters Present",
        "intro": "Everyone in the scene gets a row. A character with no want and no worry is furniture.",
        "fields": [
            {
                "key": "characters",
                "label": "Characters in this chapter",
                "type": "rows",
                "prompt": "One row per important character.",
                "columns": [
                    {"key": "character", "label": "Character"},
                    {"key": "wants", "label": "What they want"},
                    {"key": "worrying", "label": "What is worrying them"},
                    {"key": "knows", "label": "What they know"},
                    {"key": "hiding", "label": "Hiding / avoiding"},
                    {"key": "under_pressure", "label": "Under pressure"},
                    {"key": "does_not_know", "label": "Does not know"},
                    {"key": "may_overlook", "label": "Might notice / overlook"},
                    {"key": "what_changes", "label": "What changes for them"},
                ],
            },
        ],
    },
    {
        "key": "scene_progression",
        "number": 4,
        "title": "Scene Progression",
        "intro": "One row per scene or movement. Add as many as the chapter needs.",
        "fields": [
            {
                "key": "scenes",
                "label": "Scenes / movements",
                "type": "rows",
                "prompt": "A scene ends when the situation changes. If nothing changes, it is not a scene.",
                "columns": [
                    {"key": "scene", "label": "Scene"},
                    {"key": "location", "label": "Location"},
                    {"key": "starting_situation", "label": "Starting situation"},
                    {"key": "objective", "label": "Objective"},
                    {"key": "opposition", "label": "Opposition"},
                    {"key": "key_events", "label": "Key events"},
                    {"key": "emotional_movement", "label": "Emotional movement"},
                    {"key": "outcome", "label": "Outcome"},
                    {"key": "carries_into", "label": "Carries into next"},
                ],
            },
        ],
    },
    {
        "key": "required_beats",
        "number": 5,
        "title": "Required Beats",
        "intro": "The non-negotiables. If a beat is here, it goes on the page.",
        "fields": [
            {"key": "beats", "label": "Required beats", "type": "list", "prompt": "Essential for plot or continuity. One per bullet, in the order they should land."},
            {"key": "beats_suggested", "label": "Suggested beats", "type": "list", "prompt": "One possible way to reach the objective. The writer may find a better one."},
            {"key": "beats_flexible", "label": "Flexible", "type": "list", "prompt": "The writer decides the approach. Note anything that must not be lost in the process."},
        ],
    },
    {
        "key": "character_development",
        "number": 6,
        "title": "Character and Relationship Development",
        "intro": "What changes inside people, and between them.",
        "fields": [
            {"key": "character_development", "label": "Character development", "type": "text", "prompt": "Who changes, in what way, and what causes it?"},
            {"key": "relationship_movement", "label": "Relationship movement", "type": "text", "prompt": "Which relationship shifts — closer, further, inverted — and why?"},
            {"key": "subtext", "label": "Subtext", "type": "text", "prompt": "What is really being said underneath the dialogue?"},
            {"key": "existing_tension", "label": "Existing tension or trust", "type": "text", "prompt": "The state of the bond on the first page — how much rope is left."},
            {"key": "what_each_wants_from_other", "label": "What each wants from the other", "type": "text", "prompt": "Named person by person. Two people can want opposite things from the same conversation."},
            {"key": "said_aloud", "label": "What is said aloud", "type": "text", "prompt": "The surface of the exchange — the version they are willing to be heard saying."},
            {"key": "remains_unspoken", "label": "What remains unspoken", "type": "text", "prompt": "The thing both of them know and neither will name."},
            {"key": "relationship_change", "label": "How the relationship changes", "type": "text", "prompt": "By the last line: closer, further, or the same but with the truth now in the room."},
        ],
    },
    {
        "key": "world_setting",
        "number": 7,
        "title": "World and Setting",
        "intro": "Worldbuilding only counts when it is doing work in a scene.",
        "fields": [
            {"key": "details_to_reveal", "label": "Details to reveal naturally", "type": "text", "prompt": "The specifics this chapter should surface — through action, not lecture."},
            {"key": "everyday_context", "label": "Everyday life or wider-world context", "type": "text", "prompt": "What life looks like around the characters right now."},
            {"key": "world_rules", "label": "Relevant world rules", "type": "text", "prompt": "The limits that constrain the scene — magic costs, law, technology, taboo."},
        ],
    },
    {
        "key": "plot_threads",
        "number": 8,
        "title": "Plot Threads",
        "intro": "Every chapter moves the main plot and at least one thread beside it.",
        "fields": [
            {"key": "main_plot_progression", "label": "Main plot progression", "type": "text", "prompt": "What the chapter adds to the spine of the book."},
            {"key": "subplots", "label": "Subplots", "type": "text", "prompt": "Which subplots advance, stall or twist here."},
            {"key": "mysteries_clues", "label": "Mysteries or clues", "type": "text", "prompt": "Clue planted, misdirection laid, question sharpened."},
            {"key": "information_revealed", "label": "Information revealed", "type": "text", "prompt": "What the reader learns, and how they learn it."},
            {"key": "questions_raised", "label": "Questions raised", "type": "text", "prompt": "What the reader now needs answered. Open loops keep pages turning."},
        ],
    },
    {
        "key": "themes_emotional",
        "number": 9,
        "title": "Themes and Emotional Experience",
        "intro": "Theme is a pressure, not a speech.",
        "fields": [
            {"key": "themes_expressed", "label": "Themes expressed through the scene", "type": "text", "prompt": "Which themes surface, and through whose choices."},
            {"key": "reader_feeling", "label": "What the reader should feel", "type": "text", "prompt": "Name the feeling and the moment it should peak."},
            {"key": "sensory_details", "label": "Emotional or sensory details to prioritise", "type": "text", "prompt": "The two or three concrete images that will carry the chapter."},
        ],
    },
    {
        "key": "continuity",
        "number": 10,
        "title": "Continuity and Restrictions",
        "intro": "The guardrails. A brief that breaks canon is worse than no brief.",
        "fields": [
            {"key": "established_canon", "label": "Established canon", "type": "text", "prompt": "Facts from earlier chapters or books this chapter must honour."},
            {"key": "knowledge_restrictions", "label": "Character knowledge restrictions", "type": "text", "prompt": "Who must not know what, on pain of breaking the plot."},
            {"key": "must_stay_consistent", "label": "Details that must remain consistent", "type": "text", "prompt": "Names, distances, dates, scars, accents, objects."},
            {"key": "must_not_reveal", "label": "Information that must not be revealed", "type": "text", "prompt": "The reveal this chapter is not allowed to make."},
            {"key": "reserved_for_later", "label": "Events reserved for later", "type": "text", "prompt": "Material that belongs to a later chapter — do not spend it here."},
            {"key": "characters_excluded", "label": "Characters who should not appear", "type": "text", "prompt": "Who is off the board in this chapter, and why bringing them in would break the plan."},
        ],
    },
    {
        "key": "chapter_ending",
        "number": 11,
        "title": "Chapter Ending",
        "intro": "The last line is a doorway, not a wall.",
        "fields": [
            {"key": "what_changes", "label": "What changes by the end", "type": "text", "prompt": "The state of things at the final line versus the first."},
            {"key": "emotional_note", "label": "Emotional note", "type": "text", "prompt": "What the reader closes the chapter feeling."},
            {"key": "carries_forward", "label": "What carries into the next chapter", "type": "text", "prompt": "The unresolved pressure that pulls the reader on."},
            {"key": "transition", "label": "Transition into the next chapter", "type": "short", "prompt": "Immediate continuation, or a shift in time, place or viewpoint? Say which."},
        ],
    },
    {
        "key": "writing_guidance",
        "number": 12,
        "title": "Writing Guidance",
        "intro": "How it should read, not what happens.",
        "fields": [
            {"key": "tone_voice", "label": "Tone and voice", "type": "text", "prompt": "The register of this chapter specifically — quieter, colder, faster."},
            {"key": "dialogue_guidance", "label": "Dialogue guidance", "type": "text", "prompt": "Who talks how, what is said versus avoided."},
            {"key": "pacing", "label": "Pacing", "type": "text", "prompt": "Where it speeds up, where it slows and lets the reader breathe."},
            {"key": "balance", "label": "Required balance of action, reflection and worldbuilding", "type": "text", "prompt": "Rough proportions, and which should dominate."},
            {"key": "avoid", "label": "Specific habits or phrases to avoid", "type": "text", "prompt": "The tics this chapter must not have."},
        ],
    },
    {
        "key": "quality_check",
        "number": 13,
        "title": "Quality Check",
        "intro": "Answer honestly at the end of drafting. Anything not 'yes' is a revision note.",
        "fields": [
            {"key": "checks", "label": "Final checks", "type": "checks", "prompt": "Yes, no, or not yet.", "items": QUALITY_CHECKS},
        ],
    },
    {
        "key": "post_draft",
        "number": 14,
        "title": "Post-Draft Record",
        "intro": "Fill this in after the chapter is written. It becomes canon for the next chapter.",
        "post_draft": True,
        "fields": [
            {"key": "what_changed", "label": "What changed from this brief", "type": "text", "prompt": "Where the written chapter departed from the plan, and why the departure is better."},
            {"key": "scenes_cut", "label": "Scenes or beats cut", "type": "list", "prompt": "What was planned and is no longer in the book."},
            {"key": "scenes_added", "label": "Scenes or beats added", "type": "list", "prompt": "What appeared while writing that the plan did not have."},
            {"key": "established", "label": "Facts established", "type": "list", "prompt": "New canon created by this chapter - physical details, dates, names, rules. These bind every later chapter."},
            {"key": "threads_advanced", "label": "Threads advanced", "type": "list", "prompt": "Which open threads moved, and how far."},
            {"key": "threads_opened", "label": "Threads opened", "type": "list", "prompt": "New promises made to the reader. Each one is now a debt."},
            {"key": "setups_planted", "label": "Setups planted", "type": "list", "prompt": "What was seeded for a later payoff, and where it must land."},
            {"key": "unresolved", "label": "Left unresolved", "type": "text", "prompt": "What the chapter deliberately leaves hanging."},
            {"key": "next_chapter", "label": "What the next chapter must know", "type": "text", "prompt": "The handoff in plain language, including anything the brief for the next chapter would otherwise get wrong."},
            {"key": "word_count", "label": "Drafted word count", "type": "short", "prompt": "Actual count, not the target."},
        ],
    },
]


def blank_sections() -> dict[str, Any]:
    """An empty brief with every field present, so the UI never has to guess."""
    out: dict[str, Any] = {}
    for section in SECTIONS:
        body: dict[str, Any] = {}
        for field in section["fields"]:
            if field["type"] == "list":
                body[field["key"]] = []
            elif field["type"] == "rows":
                body[field["key"]] = []
            elif field["type"] == "checks":
                body[field["key"]] = {item: "unset" for item in field.get("items", [])}
            else:
                body[field["key"]] = ""
        out[section["key"]] = body
    return out


def merge_sections(existing: dict[str, Any] | None, incoming: dict[str, Any]) -> dict[str, Any]:
    """Merge an update into an existing brief, ignoring unknown keys."""
    merged = dict(existing or {})
    for section in SECTIONS:
        key = section["key"]
        if key not in incoming or not isinstance(incoming[key], dict):
            continue
        current = dict(merged.get(key) or {})
        allowed = {f["key"]: f for f in section["fields"]}
        for field_key, value in incoming[key].items():
            if field_key in allowed:
                current[field_key] = value
        merged[key] = current
    return merged


def _field_filled(field: dict[str, Any], value: Any) -> bool:
    if field["type"] == "checks":
        return isinstance(value, dict) and any(v == "yes" for v in value.values())
    if field["type"] in ("list", "rows"):
        return isinstance(value, list) and len(value) > 0
    return bool(str(value or "").strip())


def completeness(sections: dict[str, Any]) -> dict[str, Any]:
    """How much of the brief is filled in, per section and overall."""
    total = 0
    filled = 0
    per_section: dict[str, Any] = {}
    for section in SECTIONS:
        if section.get("post_draft"):
            # Written after the chapter exists; it must not hold up readiness.
            continue
        body = sections.get(section["key"]) or {}
        s_total = len(section["fields"])
        s_filled = 0
        for field in section["fields"]:
            if _field_filled(field, body.get(field["key"])):
                s_filled += 1
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


def section_by_key(key: str) -> dict[str, Any] | None:
    for section in SECTIONS:
        if section["key"] == key:
            return section
    return None
