"""The Book Bible questionnaire.

Single source of truth for the 15-section bible: section order, field keys,
labels, control types and the question shown under each field. The API serves
this to the web app, so a new field only has to be added here.
"""

from typing import Any

SECTIONS: list[dict[str, Any]] = [
    {
        "key": "book_details",
        "number": 1,
        "title": "Book Details",
        "intro": "The catalogue facts. These drive export metadata and publishing packs.",
        "fields": [
            {"key": "title", "label": "Title", "type": "short", "prompt": "What is this book called?"},
            {"key": "series", "label": "Series", "type": "short", "prompt": "Which series does it belong to? Leave blank for a standalone."},
            {"key": "series_position", "label": "Series position", "type": "short", "prompt": "Where does it sit in the series? e.g. Book 2, or a prequel."},
            {"key": "author", "label": "Author", "type": "short", "prompt": "The name that goes on the cover."},
            {"key": "genre", "label": "Genre", "type": "short", "prompt": "The shelf it belongs on."},
            {"key": "target_audience", "label": "Target audience", "type": "short", "prompt": "Who is this written for — age, reading taste, why they will pick it up?"},
            {"key": "preferred_length", "label": "Preferred length", "type": "short", "prompt": "Target word count or a range."},
            {"key": "content_rating", "label": "Content rating", "type": "short", "prompt": "e.g. clean, PG-13, mature. Keep it consistent with section 14."},
            {"key": "heat_level", "label": "Heat level", "type": "short", "prompt": "How much romance and intimacy is on the page, in plain terms."},
        ],
    },
    {
        "key": "story_foundation",
        "number": 2,
        "title": "Story Foundation",
        "intro": "If an AI or a ghostwriter only read one section, it would be this one.",
        "fields": [
            {"key": "premise", "label": "Premise", "type": "text", "prompt": "Two or three sentences: who, what they want, what stands in the way.", "ai": True},
            {"key": "reader_hook", "label": "Reader hook", "type": "text", "prompt": "The thing on page one that makes a reader refuse to put it down.", "ai": True},
            {"key": "promise", "label": "What this book promises", "type": "text", "prompt": "The experience you are selling. What must the reader feel by the last page?", "ai": True},
            {"key": "core_conflict", "label": "Core conflict", "type": "text", "prompt": "The single conflict everything else hangs from — and why it cannot be walked away from."},
            {"key": "main_stakes", "label": "Main stakes", "type": "text", "prompt": "What does the protagonist lose if they fail? Be specific and personal, not 'the world ends'."},
            {"key": "emotional_core", "label": "Emotional core", "type": "text", "prompt": "The feeling underneath the plot — grief, shame, hope, hunger. What is this book really about?"},
            {"key": "must_accomplish", "label": "What this book must accomplish", "type": "text", "prompt": "For the series and the reader: what has to be true by the end?"},
        ],
    },
    {
        "key": "narrative_format",
        "number": 3,
        "title": "Narrative Format",
        "intro": "The camera and the clock. These rules are binding on every chapter.",
        "fields": [
            {"key": "pov", "label": "Point of view", "type": "short", "prompt": "First person, third limited, omniscient, second — and whose head are we in?"},
            {"key": "tense", "label": "Tense", "type": "short", "prompt": "Past or present. Pick one and hold it."},
            {"key": "viewpoint_characters", "label": "Viewpoint characters", "type": "list", "prompt": "List every character who narrates or holds the camera."},
            {"key": "viewpoint_rules", "label": "Rules for viewpoint changes", "type": "text", "prompt": "How do we switch — chapter breaks only, scene breaks, named sections? Any POVs barred from certain knowledge?"},
            {"key": "narrative_distance", "label": "Narrative distance", "type": "short", "prompt": "Close and visceral, or cool and observational? How deep inside the head are we?"},
            {"key": "narrator_knowledge", "label": "What the narrator knows that the characters do not", "type": "text", "prompt": "If the answer is nothing, say so — that is a deliberate choice worth recording."},
            {"key": "viewpoint_distinctions", "label": "What makes each viewpoint distinct", "type": "text", "prompt": "For multiple viewpoints: what each person knows, misunderstands, and can never see from where they stand."},
            {"key": "deliberate_exceptions", "label": "Deliberate exceptions", "type": "text", "prompt": "Where the book breaks its own rules on purpose, and why."},
            {"key": "withheld_info", "label": "Information the reader must not receive too early", "type": "text", "prompt": "What must stay hidden, until when, and what would be spoiled if it leaked?"},
        ],
    },
    {
        "key": "tone_and_voice",
        "number": 4,
        "title": "Tone and Voice",
        "intro": "How the sentences should sound. This is the section that stops a draft reading like a different author.",
        "fields": [
            {"key": "overall_tone", "label": "Overall tone", "type": "short", "prompt": "Dark, wry, hopeful, elegiac — name it in a few words."},
            {"key": "prose_style", "label": "Prose style", "type": "text", "prompt": "Spare or lush? Long sentences or clipped? Concrete or lyrical? Give a reference author if it helps."},
            {"key": "dialogue_style", "label": "Dialogue style", "type": "text", "prompt": "How do people talk — overlap, subtext, formality, swearing, dialect?"},
            {"key": "action_style", "label": "Action style", "type": "text", "prompt": "Blow-by-blow or impressionistic? How much violence is shown on the page?"},
            {"key": "emotional_style", "label": "Emotional style", "type": "text", "prompt": "Restrained or operatic? How are grief, love and fear expressed physically?"},
            {"key": "humour", "label": "Humour", "type": "text", "prompt": "Where does the humour come from — wit, absurdity, dark comedy, banter? Who is funny?"},
            {"key": "exposition", "label": "Exposition", "type": "text", "prompt": "How is backstory delivered — dialogue, memory, documents, drip-fed detail? What is forbidden?"},
            {"key": "avoid_habits", "label": "Writing habits to avoid", "type": "list", "prompt": "Phrases, tics, clichés or structural habits the prose must never fall into."},
        ],
    },
    {
        "key": "world_and_setting",
        "number": 5,
        "title": "World and Setting",
        "intro": "Everything a ghostwriter needs to keep the world consistent without inventing against you.",
        "fields": [
            {"key": "time_period", "label": "Time period", "type": "short", "prompt": "When is this? Real year, or an invented era with a real-world analogue."},
            {"key": "major_locations", "label": "Major locations", "type": "list", "prompt": "The places the story actually visits, in order of importance."},
            {"key": "physical_environment", "label": "Physical environment", "type": "text", "prompt": "Climate, landscape, weather, sensory texture — what does it feel like to stand there?"},
            {"key": "history", "label": "History", "type": "text", "prompt": "What happened before the book that still shapes the present? Keep only what the plot leans on."},
            {"key": "technology_rules", "label": "Technology / speculative rules", "type": "text", "prompt": "What exists, what doesn't, and what are the hard limits? No rule may be broken for convenience."},
            {"key": "government_power", "label": "Government and power", "type": "text", "prompt": "Who rules, how do they enforce it, and who is outside the law?"},
            {"key": "culture_daily_life", "label": "Culture and everyday life", "type": "text", "prompt": "Food, work, money, family, faith, manners — the ordinary texture of a day."},
            {"key": "resources_economy", "label": "Resources and economy", "type": "text", "prompt": "What is scarce, what is valuable, and who controls it?"},
            {"key": "beliefs", "label": "Relevant beliefs", "type": "text", "prompt": "Religion, superstition, taboos, honour codes — what people believe and what it costs to break."},
            {"key": "world_rules", "label": "World rules and limitations", "type": "list", "prompt": "The non-negotiables. State each as a rule the story may not break."},
        ],
    },
    {
        "key": "characters",
        "number": 6,
        "title": "Characters",
        "intro": "Who is in the book. Link to the character library so profiles stay in one place.",
        "fields": [
            {"key": "major_characters", "label": "Major characters", "type": "rows", "prompt": "The handful the book is built around.", "columns": [
                {"key": "name", "label": "Name"}, {"key": "role", "label": "Role"}, {"key": "want", "label": "What they want"}, {"key": "arc", "label": "Arc in this book"}]},
            {"key": "supporting_characters", "label": "Supporting characters", "type": "rows", "prompt": "Everyone else who matters — and why they matter.", "columns": [
                {"key": "name", "label": "Name"}, {"key": "function", "label": "Function in the story"}]},
            {"key": "antagonists", "label": "Antagonists and opposing forces", "type": "rows", "prompt": "Person, institution or pressure. The best antagonists believe they are right — say why.", "columns": [
                {"key": "name", "label": "Name / force"}, {"key": "goal", "label": "What they want"}, {"key": "justification", "label": "Why they believe they're right"}]},
            {"key": "profile_links", "label": "Character profile links or full profiles", "type": "text", "prompt": "Library entries attached to this book, and anyone not yet in the library."},
        ],
    },
    {
        "key": "relationships",
        "number": 7,
        "title": "Relationships",
        "intro": "The wiring between people — and how it changes.",
        "fields": [
            {"key": "key_relationships", "label": "Key relationships", "type": "rows", "prompt": "Every pairing the story turns on.", "columns": [
                {"key": "pair", "label": "Between"}, {"key": "nature", "label": "Nature of the relationship"}]},
            {"key": "starting_dynamics", "label": "Starting dynamics", "type": "text", "prompt": "Where does each key relationship stand on page one? Who has the power?"},
            {"key": "tensions", "label": "Important tensions", "type": "text", "prompt": "What is unsaid, owed, resented or feared between them?"},
            {"key": "major_changes", "label": "Major changes", "type": "text", "prompt": "Which relationships break, deepen or invert, and at what point?"},
            {"key": "ending_dynamics", "label": "Ending dynamics", "type": "text", "prompt": "Where do they stand at the last page? Leave no pairing unchanged without reason."},
        ],
    },
    {
        "key": "themes",
        "number": 8,
        "title": "Themes",
        "intro": "What the book argues, without ever saying it out loud.",
        "fields": [
            {"key": "primary_themes", "label": "Primary themes", "type": "list", "prompt": "Two to four themes. More than four means none of them land."},
            {"key": "questions_explored", "label": "Questions explored", "type": "list", "prompt": "The questions the book asks rather than answers."},
            {"key": "theme_execution", "label": "How each theme appears through character and plot", "type": "text", "prompt": "For each theme: which character carries it, which scene proves it, and what the ending says about it."},
        ],
    },
    {
        "key": "structure",
        "number": 9,
        "title": "Story Structure",
        "intro": "The spine. Acts are built in the Acts panel — this is the shape of the journey.",
        "fields": [
            {"key": "setup", "label": "Setup", "type": "text", "prompt": "The world before the disruption, and the flaw already visible in it."},
            {"key": "inciting_incident", "label": "Inciting incident", "type": "text", "prompt": "The event that makes the old life impossible. When does it land?"},
            {"key": "confrontation_escalation", "label": "Confrontation and escalation", "type": "text", "prompt": "How do the obstacles get worse, and why can't the protagonist simply stop?"},
            {"key": "turning_points", "label": "Major turning points", "type": "rows", "prompt": "The reversals that change the direction of the story.", "columns": [
                {"key": "point", "label": "Turning point"}, {"key": "act", "label": "Where"}, {"key": "change", "label": "What changes"}]},
            {"key": "crisis", "label": "Crisis", "type": "text", "prompt": "The darkest moment — what is lost, and what does the protagonist choose?"},
            {"key": "climax", "label": "Climax", "type": "text", "prompt": "The confrontation the whole book has been loading. How is the core conflict resolved?"},
            {"key": "resolution", "label": "Resolution", "type": "text", "prompt": "The new normal. What is healed, what is scarred, what is left open?"},
        ],
    },
    {
        "key": "subplots",
        "number": 10,
        "title": "Subplots",
        "intro": "Every subplot must earn its pages by touching the main plot.",
        "fields": [
            {"key": "subplots", "label": "Subplots", "type": "rows", "prompt": "Each subplot, who carries it, and what it does for the book.", "columns": [
                {"key": "subplot", "label": "Subplot"}, {"key": "characters", "label": "Characters involved"},
                {"key": "purpose", "label": "Purpose"}, {"key": "connection", "label": "Connection to main plot"},
                {"key": "resolution", "label": "Resolution or continuation"}]},
        ],
    },
    {
        "key": "timeline",
        "number": 11,
        "title": "Timeline and Continuity",
        "intro": "The facts that must not drift between chapters or books.",
        "fields": [
            {"key": "before_book", "label": "Events before the book", "type": "text", "prompt": "What already happened, in order, and what does the reader need to know?"},
            {"key": "during_book", "label": "Events during the book", "type": "text", "prompt": "The chronology of the story itself — days, weeks or years."},
            {"key": "dates_time_gaps", "label": "Important dates and time gaps", "type": "list", "prompt": "Fixed dates, anniversaries, deadlines, and every skip forward in time."},
            {"key": "character_knowledge", "label": "Character knowledge", "type": "text", "prompt": "Who knows what, and when do they learn it? This prevents accidental omniscience."},
            {"key": "physical_continuity", "label": "Physical continuity", "type": "text", "prompt": "Injuries, weather, objects, locations — anything that must stay consistent."},
        ],
    },
    {
        "key": "mysteries",
        "number": 12,
        "title": "Mysteries and Reveals",
        "intro": "What the reader is chasing, and who is allowed to know.",
        "fields": [
            {"key": "mysteries", "label": "Mysteries", "type": "rows", "prompt": "Each question the book poses and how it pays off.", "columns": [
                {"key": "mystery", "label": "Mystery"}, {"key": "truth", "label": "Truth"},
                {"key": "who_knows", "label": "Who knows"}, {"key": "reader_knowledge", "label": "Reader knowledge"},
                {"key": "clues", "label": "Clues"}, {"key": "what_each_believes", "label": "What each believes"},
                {"key": "reveal_point", "label": "Reveal point"}, {"key": "reveal_changes", "label": "What the reveal changes"},
                {"key": "restrictions", "label": "Restrictions"}]},
        ],
    },
    {
        "key": "depth_and_experience",
        "number": 13,
        "title": "Depth and Reader Experience",
        "intro": "What the reader lives through, and what they carry out.",
        "fields": [
            {"key": "immersion", "label": "What makes it immersive", "type": "text", "prompt": "The specific thing that puts a reader inside this story rather than watching it."},
            {"key": "emotional_range", "label": "Emotional range", "type": "text", "prompt": "The full spread of feeling the book must move through, and where each lands."},
            {"key": "tension_relief", "label": "Where tension and relief fall", "type": "text", "prompt": "The rhythm of pressure and release across the book."},
            {"key": "character_depth", "label": "How character depth is revealed", "type": "text", "prompt": "Through choice under pressure, contradiction, habit, cost — name the method."},
            {"key": "interiority", "label": "Interiority", "type": "text", "prompt": "How much access the reader has to thought and feeling, and how it is delivered."},
            {"key": "inference", "label": "What the reader should infer", "type": "text", "prompt": "The things never stated but always legible."},
            {"key": "unspoken", "label": "What stays unspoken", "type": "text", "prompt": "Deliberate silences, and why they matter."},
            {"key": "memorable", "label": "What makes it memorable", "type": "text", "prompt": "The scene, image or line a reader repeats to someone else."},
            {"key": "carried_out", "label": "What the reader carries out", "type": "text", "prompt": "The thought or feeling that survives the last page."},
        ],
    },
    {
        "key": "ending_and_payoff",
        "number": 14,
        "title": "Ending and Payoff",
        "intro": "The ending, specified before the middle is written so it can be aimed at.",
        "fields": [
            {"key": "must_resolve", "label": "What must be resolved", "type": "list", "prompt": "Every question the book has to answer, one per line."},
            {"key": "promise_paid", "label": "How the promise is paid", "type": "text", "prompt": "The promise made in section 2, and the scene that honours it."},
            {"key": "emotional_payoff", "label": "Emotional payoff", "type": "text", "prompt": "What the reader should feel when it lands — and why they have earned it."},
            {"key": "final_image", "label": "Final image", "type": "text", "prompt": "The last thing on the page. Concrete, not thematic."},
            {"key": "left_open", "label": "What is deliberately left open", "type": "text", "prompt": "Open by design, not omission."},
            {"key": "setup_required", "label": "Setup the ending depends on", "type": "list", "prompt": "Everything that must be planted earlier for the ending to be honest."},
            {"key": "cost", "label": "What the ending costs", "type": "text", "prompt": "Resolution without cost reads as unearned."},
            {"key": "consequences", "label": "Consequences carried beyond the book", "type": "text", "prompt": "What this ending leaves in the world."},
        ],
    },
    {
        "key": "series_connection",
        "number": 15,
        "title": "Series Connection",
        "intro": "For a book in a series or saga: what it inherits, resolves and must protect.",
        "scope": "series",
        "fields": [
            {"key": "series_canon", "label": "Relevant series canon", "type": "text", "prompt": "The established facts this book must honour."},
            {"key": "threads_in", "label": "Threads carried into this book", "type": "list", "prompt": "Open threads from earlier books that this one picks up."},
            {"key": "threads_resolved", "label": "Threads resolved", "type": "list", "prompt": "What gets paid off here."},
            {"key": "threads_forward", "label": "Threads carried forward", "type": "list", "prompt": "What stays open for the next book, and the hook you leave."},
            {"key": "future_reveals", "label": "Future revelations to protect", "type": "text", "prompt": "The truths later books depend on. Nothing in this book may contradict them."},
        ],
    },
    {
        "key": "content_boundaries",
        "number": 16,
        "title": "Content and Style Boundaries",
        "intro": "Hard limits. A ghostwriter needs these in writing, not inferred.",
        "fields": [
            {"key": "rating", "label": "Content rating", "type": "short", "prompt": "Must match section 1."},
            {"key": "heat", "label": "Heat level", "type": "text", "prompt": "Exactly how explicit is intimacy, and what stays off the page?"},
            {"key": "violence", "label": "Violence", "type": "text", "prompt": "How graphic? On-page or implied? Any acts that never appear?"},
            {"key": "language", "label": "Language", "type": "text", "prompt": "Swearing, slurs, profanity — what is permitted and what is not."},
            {"key": "sensitive_material", "label": "Sensitive material", "type": "text", "prompt": "Trauma, abuse, self-harm, addiction, discrimination — how it is handled and what must be avoided."},
            {"key": "exclusions", "label": "Explicit exclusions", "type": "list", "prompt": "Anything the book must never contain. Treat each as a hard stop."},
        ],
    },
    {
        "key": "canon_status",
        "number": 17,
        "title": "Canon Status",
        "intro": "What is settled, what is still moving, and what needs your decision.",
        "fields": [
            {"key": "locked", "label": "Locked", "type": "list", "prompt": "Decisions that may not be changed without a rewrite."},
            {"key": "working", "label": "Working", "type": "list", "prompt": "Live decisions still open to change."},
            {"key": "undecided", "label": "Undecided", "type": "list", "prompt": "Questions you have not answered yet."},
            {"key": "contradictions", "label": "Contradictions requiring review", "type": "list", "prompt": "Anything that disagrees with itself or with the series."},
        ],
    },
]

SECTION_INDEX: dict[str, dict[str, Any]] = {s["key"]: s for s in SECTIONS}


def sections_for_scope(scope: str | None) -> list[dict[str, Any]]:
    """The questionnaire a given project scope actually uses.

    A standalone book has no series to connect to, so the series-only sections
    are dropped rather than shown empty.
    """
    if (scope or "series").lower() == "standalone":
        return [s for s in SECTIONS if s.get("scope") != "series"]
    return list(SECTIONS)


def blank_sections(scope: str | None = None) -> dict[str, Any]:
    """An empty bible with every applicable field present, so the UI never has to guess."""
    out: dict[str, Any] = {}
    for section in sections_for_scope(scope):
        body: dict[str, Any] = {}
        for field in section["fields"]:
            if field["type"] in ("list", "rows"):
                body[field["key"]] = []
            else:
                body[field["key"]] = ""
        out[section["key"]] = body
    return out


def merge_sections(existing: dict[str, Any] | None, incoming: dict[str, Any]) -> dict[str, Any]:
    """Merge an update into an existing bible, ignoring unknown keys."""
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


def completeness(
    sections: dict[str, Any], schema: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """How much of the bible is filled in, per section and overall."""
    total = 0
    filled = 0
    per_section: dict[str, Any] = {}
    for section in schema or SECTIONS:
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
