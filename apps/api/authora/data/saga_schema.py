"""The saga questionnaires - the tier above the series and the book.

Three documents, each at its own altitude:

* the saga concept and saga bible (one questionnaire, fourteen sections) -
  only what must hold true across every book;
* the saga outline - the major movements of the whole story;
* the series/phase plan - the identity, conflict and book map of one
  constituent series.

Same mechanics as the book and series bibles: the schema drives the
questionnaire, the client sends partial sections, the server merges and
reports completeness. Generic helpers live here so any of the three documents
can use them with its own section list.
"""

from __future__ import annotations

from typing import Any

# --------------------------------------------------------------------------
# 1. Saga concept + saga bible
# --------------------------------------------------------------------------

SAGA_SECTIONS: list[dict[str, Any]] = [
    {
        "key": "saga_concept",
        "number": 1,
        "title": "Saga Concept",
        "intro": "What holds the entire undertaking together, before any book is planned.",
        "fields": [
            {"key": "working_title", "label": "Working saga title", "type": "short", "prompt": "What is the whole undertaking called?"},
            {"key": "author", "label": "Author", "type": "short", "prompt": "The name that goes on every cover."},
            {"key": "genre_audience", "label": "Genre and audience", "type": "short", "prompt": "Where it sits, and who reads the whole thing from book one to the last."},
            {"key": "core_premise", "label": "Core premise", "type": "text", "prompt": "The overarching story in a few sentences - what is this really about?", "ai": True},
            {"key": "distinctive", "label": "What makes it distinctive", "type": "text", "prompt": "The thing no other saga does. If you cannot name it, the scope is not justified yet."},
            {"key": "why_multi_book", "label": "Why it needs several books or series", "type": "text", "prompt": "What genuinely cannot be told at one book's scale?"},
            {"key": "connective_tissue", "label": "What connects its parts", "type": "text", "prompt": "The people, question, place or conflict that makes separate series one saga."},
            {"key": "reader_promise", "label": "Reader promise", "type": "text", "prompt": "The experience a reader is buying into, and what must stay recognisable across every book.", "ai": True},
            {"key": "promise_expansion", "label": "How the experience expands", "type": "text", "prompt": "How the saga widens or deepens without becoming a different thing."},
            {"key": "emotional_anchors", "label": "Whose experience anchors the saga", "type": "text", "prompt": "Which people and relationships carry the emotional weight as the scale grows."},
            {"key": "caring_at_scale", "label": "Why readers still care at scale", "type": "text", "prompt": "The personal stakes that survive empires falling."},
            {"key": "central_conflict", "label": "Central conflict", "type": "text", "prompt": "The fundamental problem driving the whole saga - and the forces that keep it alive."},
            {"key": "conflict_evolution", "label": "How the conflict changes", "type": "text", "prompt": "What it looks like at the start, the middle and the end - so it never resets to the same crisis."},
            {"key": "resolution_conditions", "label": "What a meaningful resolution requires", "type": "text", "prompt": "The conditions that must be met for the ending to count as an answer."},
            {"key": "central_questions", "label": "Central thematic questions", "type": "list", "prompt": "One question per line. These are argued, not answered in a paragraph."},
            {"key": "theme_perspectives", "label": "How different parts explore them", "type": "text", "prompt": "Which series or phase takes which angle on the same question."},
            {"key": "time_span", "label": "Time span", "type": "short", "prompt": "Years, generations or centuries covered."},
            {"key": "world_scope", "label": "Geographical or world scope", "type": "short", "prompt": "One city, one world, several worlds."},
            {"key": "proposed_parts", "label": "Proposed series or major phases", "type": "list", "prompt": "Working names, in order. You can change them later; having them changes what book one must do."},
            {"key": "book_count", "label": "Approximate number of books", "type": "short", "prompt": "A range is fine. 'Unknown' is also an answer."},
            {"key": "left_flexible", "label": "Deliberately left flexible", "type": "text", "prompt": "What you refuse to lock now, and what would have to be true to lock it."},
            {"key": "final_state", "label": "Intended final state", "type": "text", "prompt": "What the world looks like when the saga closes."},
            {"key": "answered_question", "label": "The question answered at the end", "type": "text", "prompt": "The one the whole saga has been asking."},
            {"key": "emotional_payoff", "label": "Emotional payoff", "type": "text", "prompt": "What the reader should feel on the last page."},
            {"key": "still_unresolved", "label": "What may deliberately remain unresolved", "type": "text", "prompt": "Open by design, not by accident."},
            {"key": "locked_foundations", "label": "Locked foundations", "type": "list", "prompt": "Decisions that cannot move now. One per line."},
            {"key": "working_ideas", "label": "Working ideas", "type": "list", "prompt": "Live but not committed."},
            {"key": "open_questions", "label": "Questions still to answer", "type": "list", "prompt": "What has to be settled before book one can be drafted."},
        ],
    },
    {
        "key": "saga_identity",
        "number": 2,
        "title": "Saga Identity",
        "intro": "The same promise, compressed to the facts every collaborator needs.",
        "fields": [
            {"key": "premise", "label": "Premise", "type": "text", "prompt": "The saga in two or three sentences.", "ai": True},
            {"key": "genre", "label": "Genre", "type": "short", "prompt": "The shelf, stated plainly."},
            {"key": "audience", "label": "Audience", "type": "short", "prompt": "Who it is written for."},
            {"key": "reader_promise", "label": "Reader promise", "type": "text", "prompt": "What every book in the saga delivers, whatever its plot."},
            {"key": "emotional_core", "label": "Emotional core", "type": "text", "prompt": "The feeling underneath everything."},
            {"key": "themes", "label": "Overarching themes", "type": "list", "prompt": "One per line, stated as a question where possible."},
        ],
    },
    {
        "key": "fundamental_truths",
        "number": 3,
        "title": "Fundamental Truths",
        "intro": "What is objectively true in this universe - as distinct from what its people believe.",
        "fields": [
            {"key": "objective_truths", "label": "What is objectively true", "type": "list", "prompt": "One hard truth per line. These outrank any book's convenience."},
            {"key": "popular_beliefs", "label": "What inhabitants believe", "type": "list", "prompt": "The accepted story, including the parts that are wrong."},
            {"key": "belief_vs_reality", "label": "Where belief differs from reality", "type": "text", "prompt": "The gap that the saga's reveals live in."},
            {"key": "undecided_truths", "label": "Truths still undecided", "type": "list", "prompt": "Marked honestly, so no book commits to one by accident."},
        ],
    },
    {
        "key": "world_history",
        "number": 4,
        "title": "World and History",
        "intro": "The stage and how it got this way.",
        "fields": [
            {"key": "worlds_regions", "label": "Worlds and major regions", "type": "list", "prompt": "One per line, with the one-line character of each."},
            {"key": "historical_periods", "label": "Relevant historical periods", "type": "list", "prompt": "Only the periods the saga actually uses."},
            {"key": "foundational_events", "label": "Foundational events", "type": "rows", "prompt": "Event, when, and what it made permanent.", "columns": [{"key": "event", "label": "Event"}, {"key": "when", "label": "When"}, {"key": "consequence", "label": "Left behind"}]},
            {"key": "cultures", "label": "Cultures and societies", "type": "text", "prompt": "How people live, what they value, what they fear."},
            {"key": "institutions", "label": "Institutions and power structures", "type": "text", "prompt": "Who rules, who administers, who is outside the law."},
            {"key": "languages_beliefs", "label": "Languages and beliefs", "type": "text", "prompt": "What is spoken, what is sacred, what is forbidden."},
            {"key": "everyday_life", "label": "Everyday life and material conditions", "type": "text", "prompt": "What a normal day costs and looks like - the detail that makes scale believable."},
        ],
    },
    {
        "key": "rules_limits",
        "number": 5,
        "title": "Rules and Limitations",
        "intro": "The physics of your world. Limits create tension; powers without cost create none.",
        "fields": [
            {"key": "technology", "label": "Technology level", "type": "text", "prompt": "What exists, what does not, and what is unevenly distributed."},
            {"key": "speculative_systems", "label": "Speculative or supernatural systems", "type": "text", "prompt": "Magic, the gift, the engine - whatever the saga runs on."},
            {"key": "capabilities", "label": "What it can do", "type": "list", "prompt": "Capability per line, stated concretely."},
            {"key": "costs", "label": "What it costs", "type": "list", "prompt": "Every use has a price. Name it."},
            {"key": "limitations", "label": "What it can never do", "type": "list", "prompt": "The walls. These are what make the endings honest."},
            {"key": "exceptions", "label": "Exceptions and why they exist", "type": "rows", "prompt": "Exception, reason, and what it costs to use.", "columns": [{"key": "exception", "label": "Exception"}, {"key": "reason", "label": "Why it exists"}, {"key": "cost", "label": "Cost"}]},
            {"key": "societal_consequences", "label": "Consequences for society", "type": "text", "prompt": "How the rules shape law, war, work and family."},
        ],
    },
    {
        "key": "master_chronology",
        "number": 6,
        "title": "Master Chronology",
        "intro": "The spine of time. Books hang from this; it does not move to suit them.",
        "fields": [
            {"key": "before_saga", "label": "Events before the saga", "type": "rows", "prompt": "Event, date or era, why it still matters.", "columns": [{"key": "event", "label": "Event"}, {"key": "when", "label": "When"}, {"key": "why_it_matters", "label": "Still matters because"}]},
            {"key": "phase_events", "label": "Events during each phase", "type": "rows", "prompt": "Phase, event, consequence.", "columns": [{"key": "phase", "label": "Phase"}, {"key": "event", "label": "Event"}, {"key": "consequence", "label": "Consequence"}]},
            {"key": "overlaps", "label": "Overlapping events", "type": "text", "prompt": "What happens simultaneously in different places, and who does not know about what."},
            {"key": "travel_communication", "label": "Travel and communication constraints", "type": "text", "prompt": "How long things take. This governs every plot convenience you are allowed."},
            {"key": "ages_gaps", "label": "Character ages and time gaps", "type": "text", "prompt": "Who is how old when, and where the gaps fall."},
        ],
    },
    {
        "key": "saga_characters",
        "number": 7,
        "title": "Characters",
        "intro": "Saga-level people only - the ones whose lives span more than one book.",
        "fields": [
            {"key": "profiles", "label": "Saga-level profiles", "type": "rows", "prompt": "Name, role, what they want across the whole saga, planned outcome.", "columns": [{"key": "name", "label": "Name"}, {"key": "role", "label": "Role"}, {"key": "long_want", "label": "Wants across the saga"}, {"key": "outcome", "label": "Planned outcome"}]},
            {"key": "first_appearances", "label": "First appearances", "type": "text", "prompt": "Who arrives when, and what the reader knows of them before."},
            {"key": "relationships", "label": "Relationships that carry weight", "type": "text", "prompt": "The bonds the saga is actually about."},
            {"key": "knowledge_development", "label": "How their knowledge changes", "type": "text", "prompt": "What each learns, when, and what it costs them."},
            {"key": "planned_outcomes", "label": "Established outcomes", "type": "text", "prompt": "Fates already fixed. Everything else stays open."},
        ],
    },
    {
        "key": "factions",
        "number": 8,
        "title": "Factions and Institutions",
        "intro": "The organised forces. Each one needs a goal it will pay for.",
        "fields": [
            {"key": "faction_rows", "label": "Factions", "type": "rows", "prompt": "Name, public position, private activity, what it wants.", "columns": [{"key": "name", "label": "Name"}, {"key": "public", "label": "Public position"}, {"key": "private", "label": "Private activity"}, {"key": "goal", "label": "Goal"}]},
            {"key": "resources", "label": "Resources and reach", "type": "text", "prompt": "Money, people, legitimacy, information - who has which."},
            {"key": "internal_divisions", "label": "Internal divisions", "type": "text", "prompt": "The fault lines that let a faction break or be used."},
            {"key": "change_over_time", "label": "How they change", "type": "text", "prompt": "What each becomes by the end."},
        ],
    },
    {
        "key": "overarching_conflict",
        "number": 9,
        "title": "Overarching Conflict",
        "intro": "The engine of the saga, stated so any book can be checked against it.",
        "fields": [
            {"key": "origins", "label": "Origins", "type": "text", "prompt": "Where the conflict starts, and who started it."},
            {"key": "opposing_interests", "label": "Opposing interests", "type": "text", "prompt": "What each side cannot give up. Both must be defensible."},
            {"key": "escalation", "label": "Escalation ladder", "type": "text", "prompt": "How stakes rise across the phases without repeating a crisis."},
            {"key": "transformations", "label": "Major transformations", "type": "text", "prompt": "What the conflict becomes - and what it destroys on the way."},
            {"key": "resolution_conditions", "label": "Conditions for resolution", "type": "text", "prompt": "What has to be true for it to end, and what that ending costs."},
        ],
    },
    {
        "key": "knowledge_revelations",
        "number": 10,
        "title": "Knowledge and Revelations",
        "intro": "Truth versus belief. This section is the saga's integrity.",
        "fields": [
            {"key": "underlying_truths", "label": "Underlying truths", "type": "list", "prompt": "What is actually going on, one truth per line."},
            {"key": "who_knows", "label": "Who knows each truth", "type": "rows", "prompt": "Truth, who knows it, who believes otherwise.", "columns": [{"key": "truth", "label": "Truth"}, {"key": "knows", "label": "Knows"}, {"key": "believes_otherwise", "label": "Believes otherwise"}]},
            {"key": "reader_belief", "label": "What the reader initially believes", "type": "text", "prompt": "The default reading you are setting up to overturn."},
            {"key": "clues", "label": "Clues and partial discoveries", "type": "list", "prompt": "One per line, with where it appears."},
            {"key": "reveal_points", "label": "Intended reveal points", "type": "rows", "prompt": "Truth, revealed in which book or phase, to whom.", "columns": [{"key": "truth", "label": "Truth"}, {"key": "where", "label": "Revealed in"}, {"key": "to_whom", "label": "To whom"}]},
            {"key": "consequences", "label": "Consequences of each revelation", "type": "text", "prompt": "What changes in the world once it is known."},
        ],
    },
    {
        "key": "long_term_threads",
        "number": 11,
        "title": "Long-Term Threads",
        "intro": "Every promise here is a debt. Tracked in the thread ledger, paid before the last page.",
        "fields": [
            {"key": "promises", "label": "Promises made to the reader", "type": "list", "prompt": "One per line. If it is not paid, it is a broken promise, not a mystery."},
            {"key": "mysteries", "label": "Mysteries opened", "type": "list", "prompt": "The question, and the book that answers it."},
            {"key": "significant_objects", "label": "Objects, places or events with later significance", "type": "list", "prompt": "What it is, and what it is for."},
            {"key": "relationship_payoffs", "label": "Relationships requiring payoff", "type": "text", "prompt": "Which bonds have to land, and how."},
            {"key": "unresolved_consequences", "label": "Unresolved consequences", "type": "text", "prompt": "Damage still working its way through the saga."},
        ],
    },
    {
        "key": "series_or_phases",
        "number": 12,
        "title": "Series or Phases",
        "intro": "The parts of the saga, at a glance. Full plans live in the series planner.",
        "fields": [
            {"key": "parts", "label": "Parts of the saga", "type": "rows", "prompt": "Name, purpose, where and when, its own conflict, what it contributes.", "columns": [{"key": "name", "label": "Name"}, {"key": "purpose", "label": "Purpose"}, {"key": "setting", "label": "Where and when"}, {"key": "conflict", "label": "Its own conflict"}, {"key": "contribution", "label": "Contribution"}]},
            {"key": "distinct_identities", "label": "What makes each distinct", "type": "text", "prompt": "Each part must be recognisably its own thing, not more of the same."},
            {"key": "handoffs", "label": "Handoffs between parts", "type": "text", "prompt": "What the end of one hands to the start of the next."},
        ],
    },
    {
        "key": "continuity_boundaries",
        "number": 13,
        "title": "Continuity and Boundaries",
        "intro": "What may never break, and what may vary between books.",
        "fields": [
            {"key": "locked_facts", "label": "Locked facts", "type": "list", "prompt": "One per line. A draft that contradicts one is wrong."},
            {"key": "permitted_variation", "label": "Permitted variation between books", "type": "text", "prompt": "Voice, length, POV - what may legitimately differ."},
            {"key": "content_boundaries", "label": "Content boundaries", "type": "text", "prompt": "Language, violence, heat, on-page limits. Binding everywhere."},
            {"key": "naming_conventions", "label": "Naming conventions", "type": "text", "prompt": "How people, places and things are named; names already spent."},
            {"key": "research_needed", "label": "Details requiring research", "type": "list", "prompt": "What must be checked before it is written as fact."},
            {"key": "contradictions", "label": "Contradictions needing a decision", "type": "list", "prompt": "Known conflicts in the material, and who decides."},
        ],
    },
    {
        "key": "final_resolution",
        "number": 14,
        "title": "Final Resolution",
        "intro": "The ending, written down early so the middle can aim at it.",
        "fields": [
            {"key": "must_resolve", "label": "What the saga must resolve", "type": "text", "prompt": "The questions that cannot be left open."},
            {"key": "character_outcomes", "label": "Character and relationship outcomes", "type": "text", "prompt": "Where each person the reader loves ends up, and with whom."},
            {"key": "world_consequences", "label": "World consequences", "type": "text", "prompt": "What is permanently different about the world."},
            {"key": "required_payoffs", "label": "Payoffs required", "type": "list", "prompt": "Every promise that must land, one per line."},
            {"key": "open_by_design", "label": "Deliberately open questions", "type": "list", "prompt": "Left open on purpose, with the reason."},
        ],
    },
]

# --------------------------------------------------------------------------
# 2. Saga outline
# --------------------------------------------------------------------------

SAGA_OUTLINE_SECTIONS: list[dict[str, Any]] = [
    {
        "key": "opening_state",
        "number": 1,
        "title": "Opening State",
        "intro": "Where the world and the reader stand on page one.",
        "fields": [
            {"key": "world_state", "label": "Opening state of the world", "type": "text", "prompt": "What is normal, and what is already straining."},
            {"key": "reader_understanding", "label": "Initial reader understanding", "type": "text", "prompt": "What the reader thinks is going on - the belief the saga will test."},
            {"key": "ensemble", "label": "Central people or ensemble", "type": "text", "prompt": "Who we follow at the widest level."},
            {"key": "dramatic_question", "label": "Overarching dramatic question", "type": "text", "prompt": "The question the whole saga answers. One sentence."},
        ],
    },
    {
        "key": "phase_map",
        "number": 2,
        "title": "Phase Map",
        "intro": "Each movement of the saga, and the change it leaves behind.",
        "fields": [
            {"key": "phases", "label": "Movements", "type": "rows", "prompt": "One row per series or major phase.", "columns": [
                {"key": "name", "label": "Name"},
                {"key": "conflict", "label": "Its conflict"},
                {"key": "start", "label": "Starts with"},
                {"key": "events", "label": "Major events"},
                {"key": "end", "label": "Ends with"},
                {"key": "into_next", "label": "Leads into"},
            ]},
            {"key": "escalation_logic", "label": "Why each phase must follow", "type": "text", "prompt": "What makes the next phase necessary rather than optional."},
        ],
    },
    {
        "key": "saga_climax",
        "number": 3,
        "title": "Saga Climax",
        "intro": "The decisive point the entire saga has been building toward.",
        "fields": [
            {"key": "decisive_point", "label": "What brings the conflict to a decision", "type": "text", "prompt": "The event or choice that makes the ending inevitable."},
            {"key": "decision_makers", "label": "Who makes the decisive choices", "type": "text", "prompt": "And what it costs each of them."},
            {"key": "setup", "label": "How earlier events make it possible", "type": "text", "prompt": "The chain of causes - every link must already exist in a book."},
            {"key": "price", "label": "What resolution costs", "type": "text", "prompt": "Victory without cost reads as unearned."},
        ],
    },
    {
        "key": "saga_ending",
        "number": 4,
        "title": "Saga Ending",
        "intro": "The last page, specified while the middle is still soft.",
        "fields": [
            {"key": "resolved", "label": "What is resolved", "type": "list", "prompt": "One per line, tied to a promise made earlier."},
            {"key": "changed_permanently", "label": "What changes permanently", "type": "text", "prompt": "The world after - and why it cannot go back."},
            {"key": "people_outcomes", "label": "What happens to the people readers care about", "type": "text", "prompt": "Specific, not thematic."},
            {"key": "final_payoffs", "label": "Early promises paid off", "type": "list", "prompt": "The promise, and where it lands."},
            {"key": "final_feeling", "label": "Final emotional experience", "type": "text", "prompt": "The feeling on the last line."},
        ],
    },
]

# --------------------------------------------------------------------------
# 3. Series / major-phase plan
# --------------------------------------------------------------------------

SERIES_PLAN_SECTIONS: list[dict[str, Any]] = [
    {
        "key": "identity",
        "number": 1,
        "title": "Identity",
        "intro": "This part of the saga on its own terms.",
        "fields": [
            {"key": "name", "label": "Name", "type": "short", "prompt": "Working title for this series or phase."},
            {"key": "position", "label": "Position within the saga", "type": "short", "prompt": "First, second, a bridge, the last."},
            {"key": "book_count", "label": "Proposed book count", "type": "short", "prompt": "A range is fine."},
            {"key": "time_span", "label": "Time span", "type": "short", "prompt": "How long this part covers."},
            {"key": "settings", "label": "Primary settings", "type": "short", "prompt": "Where it happens."},
            {"key": "premise", "label": "Premise", "type": "text", "prompt": "What this part is about, in two sentences."},
            {"key": "reader_promise", "label": "Distinct reader promise", "type": "text", "prompt": "What a reader gets here that they do not get elsewhere in the saga."},
            {"key": "central_conflict", "label": "Central conflict", "type": "text", "prompt": "This part's own engine."},
            {"key": "emotional_core", "label": "Emotional core", "type": "text", "prompt": "The feeling that carries it."},
            {"key": "themes", "label": "Primary themes", "type": "list", "prompt": "Which saga questions this part argues hardest."},
        ],
    },
    {
        "key": "characters",
        "number": 2,
        "title": "Characters",
        "intro": "Who carries this part, who returns, who arrives.",
        "fields": [
            {"key": "main_cast", "label": "Main cast", "type": "rows", "prompt": "Name, role, what they want here, where they end.", "columns": [{"key": "name", "label": "Name"}, {"key": "role", "label": "Role"}, {"key": "want", "label": "Wants here"}, {"key": "ends_at", "label": "Ends at"}]},
            {"key": "returning", "label": "Returning characters", "type": "list", "prompt": "Who comes in from earlier books, in what state."},
            {"key": "new", "label": "New characters", "type": "list", "prompt": "Who arrives, and what they bring that the others cannot."},
            {"key": "development", "label": "Character development across this phase", "type": "text", "prompt": "Who they are at the start, and what changes them."},
            {"key": "relationships", "label": "Relationship development", "type": "text", "prompt": "Which bonds form, break or change, and in which book."},
        ],
    },
    {
        "key": "story",
        "number": 3,
        "title": "Story",
        "intro": "The arc of this part, from opening situation to resolution.",
        "fields": [
            {"key": "opening", "label": "Opening situation", "type": "text", "prompt": "What is true when book one of this part begins."},
            {"key": "developments", "label": "Major developments", "type": "list", "prompt": "One per line, in order."},
            {"key": "discoveries", "label": "Central discoveries", "type": "list", "prompt": "What is learned, and in which book."},
            {"key": "climax", "label": "Climax", "type": "text", "prompt": "The decisive moment of this part."},
            {"key": "resolution", "label": "Resolution", "type": "text", "prompt": "How this part lands, and what it leaves standing."},
        ],
    },
    {
        "key": "saga_connection",
        "number": 4,
        "title": "Saga Connection",
        "intro": "What this part inherits, contributes, and passes on.",
        "fields": [
            {"key": "established_facts", "label": "Relevant established facts", "type": "list", "prompt": "Saga truths this part must respect."},
            {"key": "inherited", "label": "Consequences inherited", "type": "text", "prompt": "What earlier parts left behind, still working."},
            {"key": "contribution", "label": "What this part contributes", "type": "text", "prompt": "The permanent change it makes to the saga."},
            {"key": "answers", "label": "Saga questions it answers", "type": "list", "prompt": "One per line."},
            {"key": "complicates", "label": "Questions it complicates", "type": "list", "prompt": "What it makes harder rather than clearer."},
            {"key": "threads_resolved", "label": "Threads resolved", "type": "list", "prompt": "Promises paid here."},
            {"key": "threads_forward", "label": "Threads passed forward", "type": "list", "prompt": "Debts handed to the next part."},
        ],
    },
    {
        "key": "book_map",
        "number": 5,
        "title": "Book Map",
        "intro": "One row per proposed book. This is the plan the book records hang from.",
        "fields": [
            {"key": "books", "label": "Proposed books", "type": "rows", "prompt": "Working title, premise, conflict, movement, resolution, contribution.", "columns": [
                {"key": "title", "label": "Working title"},
                {"key": "premise", "label": "Premise"},
                {"key": "conflict", "label": "Central conflict"},
                {"key": "movement", "label": "Character movement"},
                {"key": "resolution", "label": "Main resolution"},
                {"key": "series_job", "label": "Job in this series"},
                {"key": "saga_job", "label": "Job in the saga"},
            ]},
        ],
    },
    {
        "key": "ending",
        "number": 6,
        "title": "Ending",
        "intro": "What closes here, and what the next part inherits.",
        "fields": [
            {"key": "concludes", "label": "What concludes here", "type": "list", "prompt": "One per line."},
            {"key": "remains_active", "label": "What remains active", "type": "list", "prompt": "Deliberately left live."},
            {"key": "inherited_conditions", "label": "Conditions inherited by the next part", "type": "text", "prompt": "State of the world, the cast and the debts."},
        ],
    },
]

# --------------------------------------------------------------------------
# 4. Book-level connection block
# --------------------------------------------------------------------------

BOOK_CONNECTION_SECTIONS: list[dict[str, Any]] = [
    {
        "key": "position",
        "number": 1,
        "title": "Position",
        "intro": "Where this book sits, and what it must respect.",
        "fields": [
            {"key": "position", "label": "Position", "type": "short", "prompt": "Saga, series, and number within the series."},
            {"key": "references", "label": "Relevant saga and series references", "type": "list", "prompt": "The canon documents and sections this book depends on."},
            {"key": "already_happened", "label": "What has already happened", "type": "text", "prompt": "The state of play when this book opens."},
            {"key": "reader_knows", "label": "What the reader is expected to know", "type": "text", "prompt": "Assume this, and no more."},
            {"key": "characters_know", "label": "What the characters know", "type": "text", "prompt": "Including what they wrongly believe."},
            {"key": "unresolved_entering", "label": "Unresolved consequences entering", "type": "list", "prompt": "Debts this book inherits."},
        ],
    },
    {
        "key": "contribution",
        "number": 2,
        "title": "This Book's Contribution",
        "intro": "What this book is for, beyond itself.",
        "fields": [
            {"key": "own_story", "label": "Its own central story", "type": "text", "prompt": "Readable on its own terms."},
            {"key": "own_journey", "label": "Its own emotional journey", "type": "text", "prompt": "What the reader feels here specifically."},
            {"key": "own_climax", "label": "Its own climax and resolution", "type": "text", "prompt": "How this book lands."},
            {"key": "saga_change", "label": "What changes in the wider saga", "type": "text", "prompt": "The permanent difference this book makes."},
        ],
    },
    {
        "key": "continuity",
        "number": 3,
        "title": "Continuity",
        "intro": "The locks this book must not break.",
        "fields": [
            {"key": "applicable_facts", "label": "Saga facts that apply", "type": "list", "prompt": "The specific truths this story touches."},
            {"key": "still_hidden", "label": "Information still hidden", "type": "list", "prompt": "What must not be revealed yet."},
            {"key": "reserved", "label": "Events reserved for later", "type": "list", "prompt": "What this book must not spend."},
            {"key": "threads_introduced", "label": "Threads introduced", "type": "list", "prompt": "New debts opened here."},
            {"key": "threads_paid", "label": "Threads paid off", "type": "list", "prompt": "Debts settled here."},
            {"key": "threads_carried", "label": "Threads carried forward", "type": "list", "prompt": "What the next book inherits."},
        ],
    },
    {
        "key": "ending_conditions",
        "number": 4,
        "title": "Ending Conditions",
        "intro": "The state this book hands to the next one.",
        "fields": [
            {"key": "character_states", "label": "Character states", "type": "text", "prompt": "Where everyone stands, physically and emotionally."},
            {"key": "relationship_states", "label": "Relationship states", "type": "text", "prompt": "What has changed between people."},
            {"key": "world_state", "label": "World state", "type": "text", "prompt": "What is different in the world."},
            {"key": "inherited_next", "label": "What the next book inherits", "type": "text", "prompt": "The handoff, in plain terms."},
        ],
    },
]

# --------------------------------------------------------------------------
# Generic helpers
# --------------------------------------------------------------------------

SECTION_BY_KEY = {s["key"]: s for s in SAGA_SECTIONS}
OUTLINE_SECTION_BY_KEY = {s["key"]: s for s in SAGA_OUTLINE_SECTIONS}
SERIES_SECTION_BY_KEY = {s["key"]: s for s in SERIES_PLAN_SECTIONS}


def blank_sections(sections: list[dict[str, Any]] = SAGA_SECTIONS) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for section in sections:
        body: dict[str, Any] = {}
        for field in section["fields"]:
            body[field["key"]] = [] if field["type"] in ("list", "rows") else ""
        out[section["key"]] = body
    return out


def merge_sections(
    existing: dict[str, Any] | None,
    incoming: dict[str, Any],
    sections: list[dict[str, Any]] = SAGA_SECTIONS,
) -> dict[str, Any]:
    merged = dict(existing or {})
    for section in sections:
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


def completeness(
    data: dict[str, Any],
    sections: list[dict[str, Any]] = SAGA_SECTIONS,
) -> dict[str, Any]:
    total = 0
    filled = 0
    per_section: dict[str, Any] = {}
    for section in sections:
        body = data.get(section["key"]) or {}
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
