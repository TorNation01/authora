"""Poetry and additional template definitions for AUTHORA.

Expands the template library with poetry forms, script/speech, content transformation,
faith-based, children's, anthology, and life-story templates.
"""

from typing import Any

DEFAULT_ACCOUNTABILITY = {
    "reminder_frequency": "weekly",
    "goal_type": "words",
    "default_target_words": 500,
    "check_in_prompts": ["What did you write this week?", "What's your focus for next week?"],
}


def _poetry_base(
    slug: str,
    name: str,
    description: str,
    parent_slug: str,
    planning_sections: list[dict],
    chapter_skeletons: list[dict],
    milestones: list[dict],
    ai_prompts: dict[str, str],
    sort_order: int,
    **overrides: Any,
) -> dict[str, Any]:
    """Base poetry template."""
    return {
        "slug": slug,
        "category": "poetry",
        "parent_slug": parent_slug,
        "name": name,
        "description": description,
        "who_it_is_for": "Poets drafting, revising, and organizing poems.",
        "expected_outcome": "Polished poem(s) or collection ready for submission or publication.",
        "suggested_workflow": "Draft → Revise → Shape → Polish.",
        "book_type": "fiction",
        "genre": "Poetry",
        "structure_framework": "poetic_form",
        "default_structure": {"planning_sections": planning_sections},
        "default_milestones": milestones,
        "default_planning_prompts": {
            "theme": "What is this poem about?",
            "tone": "What emotional register are you aiming for?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": ai_prompts,
        "export_recommendations": ["docx", "pdf", "epub"],
        "setup_questions": [
            {"id": "form", "prompt": "What form or structure?", "type": "text"},
            {"id": "theme", "prompt": "What is the poem's theme or subject?", "type": "text"},
        ],
        "chapter_skeletons": chapter_skeletons,
        "sort_order": sort_order,
        "is_featured": False,
        "is_disabled": False,
        "access_level": "free",
        "premium_pack_slug": None,
        **overrides,
    }


def _creative_base(
    slug: str,
    name: str,
    description: str,
    category: str,
    parent_slug: str | None,
    planning_sections: list[dict],
    chapter_skeletons: list[dict],
    milestones: list[dict],
    ai_prompts: dict[str, str],
    sort_order: int,
    book_type: str = "nonfiction",
    **overrides: Any,
) -> dict[str, Any]:
    """Base for creative/nonfiction templates."""
    return {
        "slug": slug,
        "category": category,
        "parent_slug": parent_slug,
        "name": name,
        "description": description,
        "who_it_is_for": "Writers creating structured content.",
        "expected_outcome": "A complete, polished manuscript ready for export or publication.",
        "suggested_workflow": "Plan → Draft → Revise → Export.",
        "book_type": book_type,
        "genre": "General",
        "structure_framework": "custom",
        "default_structure": {"planning_sections": planning_sections},
        "default_milestones": milestones,
        "default_planning_prompts": {},
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": ai_prompts,
        "export_recommendations": ["docx", "pdf", "epub"],
        "setup_questions": [
            {"id": "purpose", "prompt": "What is the main purpose of this project?", "type": "text"},
        ],
        "chapter_skeletons": chapter_skeletons,
        "sort_order": sort_order,
        "is_featured": False,
        "is_disabled": False,
        "access_level": "free",
        "premium_pack_slug": None,
        **overrides,
    }


# ---------------------------------------------------------------------------
# POETRY PLANNING SECTIONS
# ---------------------------------------------------------------------------

POETRY_SINGLE_PLANNING = [
    {"id": "subject", "title": "Subject / Trigger", "type": "text", "guidance": "What sparked this poem? Image, memory, question, or observation."},
    {"id": "tone", "title": "Tone & Voice", "type": "text", "guidance": "Emotional register. Formal, intimate, ironic, meditative?"},
    {"id": "form_notes", "title": "Form Notes", "type": "section", "guidance": "Meter, rhyme, line length, stanza breaks. Or free verse constraints."},
    {"id": "draft", "title": "Draft", "type": "section", "guidance": "Raw draft. Let it flow."},
    {"id": "revision", "title": "Revision Notes", "type": "section", "guidance": "Line breaks, word choice, cuts, additions."},
]

POETRY_COLLECTION_PLANNING = [
    {"id": "theme", "title": "Collection Theme", "type": "text", "guidance": "What ties these poems together?"},
    {"id": "poem_list", "title": "Poem List", "type": "section", "guidance": "Titles and one-line summaries."},
    {"id": "sections", "title": "Section Grouping", "type": "section", "guidance": "How to group poems. Thematic, chronological, or structural."},
    {"id": "sequence", "title": "Sequence Planning", "type": "section", "guidance": "Order. Opening and closing poems. Emotional arc."},
    {"id": "revision", "title": "Revision Tracking", "type": "section", "guidance": "Poems to revise. Consistency across collection."},
]

POETRY_AI_PROMPTS = {
    "imagery": "Help me strengthen the imagery in this passage.",
    "rhythm": "Give feedback on the rhythm and line breaks.",
    "word_choice": "Suggest alternatives for [word/phrase] that maintain the tone.",
    "feedback": "Give feedback on this poem's imagery and rhythm.",
}

POETRY_MILESTONES = [
    {"id": "draft", "label": "First draft complete", "type": "draft"},
    {"id": "revision", "label": "Revision pass complete", "type": "revision"},
    {"id": "polish", "label": "Final polish", "type": "revision"},
]

# Single poem
SINGLE_POEM_SKELETON = [
    {"title": "Draft", "summary": "Raw draft – let it flow"},
    {"title": "Revision 1", "summary": "Line breaks, word choice, cuts"},
    {"title": "Revision 2", "summary": "Tighten. Sound. Rhythm."},
    {"title": "Final", "summary": "Polished version"},
]

# Free verse
FREE_VERSE_SKELETON = [
    {"title": "Subject & Trigger", "summary": "What sparked this? Image, memory, question."},
    {"title": "Draft", "summary": "No fixed meter or rhyme. Follow the breath."},
    {"title": "Line Breaks", "summary": "Where to break? Enjambment vs. end-stop."},
    {"title": "Revision", "summary": "Every word earns its place."},
]

# Sonnet (14 lines)
SONNET_SKELETON = [
    {"title": "Volta / Turn", "summary": "Where does the poem shift? Line 9 (Petrarchan) or 13 (Shakespearean)?"},
    {"title": "Quatrain 1", "summary": "Lines 1–4. Establish situation or image."},
    {"title": "Quatrain 2", "summary": "Lines 5–8. Develop or complicate."},
    {"title": "Quatrain 3", "summary": "Lines 9–12. Turn or deepen."},
    {"title": "Couplet", "summary": "Lines 13–14. Resolution, twist, or echo."},
]

# Haiku / short form
HAIKU_SKELETON = [
    {"title": "Moment", "summary": "Capture a single moment. Seasonal reference (kigo) if traditional."},
    {"title": "Line 1 (5)", "summary": "5 syllables. First image."},
    {"title": "Line 2 (7)", "summary": "7 syllables. Second image or shift."},
    {"title": "Line 3 (5)", "summary": "5 syllables. Resolution or echo."},
    {"title": "Variants", "summary": "Short form variants: tanka, senryu, etc."},
]

# Spoken word / performance
SPOKEN_WORD_SKELETON = [
    {"title": "Performance Notes", "summary": "Pace, pauses, emphasis. Where to breathe."},
    {"title": "Draft", "summary": "Written for the ear. Repetition, rhythm, call-and-response."},
    {"title": "Punch Lines", "summary": "Key moments that land. Emotional peaks."},
    {"title": "Revision", "summary": "Read aloud. Cut what doesn't land."},
]

# Lyric poem
LYRIC_POEM_SKELETON = [
    {"title": "Emotional Core", "summary": "What feeling drives this poem?"},
    {"title": "Draft", "summary": "First-person. Musical. Concentrated."},
    {"title": "Sound", "summary": "Assonance, rhyme, rhythm. How does it sound?"},
    {"title": "Revision", "summary": "Tighten. Every word carries weight."},
]

# Narrative poem
NARRATIVE_POEM_SKELETON = [
    {"title": "Story", "summary": "What happens? Who, what, when, where."},
    {"title": "Draft", "summary": "Tell the story in verse. Plot + character."},
    {"title": "Pacing", "summary": "Where to speed up, slow down, or add detail."},
    {"title": "Revision", "summary": "Story clarity + poetic craft."},
]

# Thematic poetry collection
THEMATIC_COLLECTION_SKELETON = [
    {"title": "Section I", "summary": "First thematic grouping – establish tone"},
    {"title": "Section II", "summary": "Middle – development, tension, or shift"},
    {"title": "Section III", "summary": "Final – resolution, echo, or open ending"},
]

# Chapbook
CHAPBOOK_SKELETON = [
    {"title": "Opening Poem", "summary": "Sets the tone. Invites the reader in."},
    {"title": "Poem 2", "summary": ""},
    {"title": "Poem 3", "summary": ""},
    {"title": "Poem 4", "summary": ""},
    {"title": "Poem 5", "summary": ""},
    {"title": "Poem 6", "summary": ""},
    {"title": "Poem 7", "summary": ""},
    {"title": "Poem 8", "summary": ""},
    {"title": "Poem 9", "summary": ""},
    {"title": "Closing Poem", "summary": "Resonance. Echo. Last word."},
]

# Poetry revision
POETRY_REVISION_SKELETON = [
    {"title": "Original", "summary": "Current version."},
    {"title": "Line Breaks", "summary": "Experiment. Where to break? Why?"},
    {"title": "Word Choice", "summary": "Replace weak words. Cut filler."},
    {"title": "Sound", "summary": "Read aloud. Rhythm, assonance, rhyme."},
    {"title": "Revised", "summary": "New draft."},
]

# Ekphrastic poem
EKPHRASIS_SKELETON = [
    {"title": "Artwork", "summary": "Describe the artwork. Artist, title, medium. What do you see?"},
    {"title": "Response", "summary": "Your reaction. What does it evoke? What story does it tell?"},
    {"title": "Draft", "summary": "Poem that speaks to or from the artwork."},
    {"title": "Revision", "summary": "Balance description and response."},
]

# Devotional / meditative poetry
DEVOTIONAL_POEM_SKELETON = [
    {"title": "Focus", "summary": "Spiritual or meditative focus. Scripture, prayer, or contemplation."},
    {"title": "Draft", "summary": "Quiet, reverent, attentive."},
    {"title": "Revision", "summary": "Clarity. Avoid preachiness. Show, don't tell."},
]


# ---------------------------------------------------------------------------
# ADDITIONAL TEMPLATE PLANNING SECTIONS
# ---------------------------------------------------------------------------

SCRIPT_PLANNING = [
    {"id": "logline", "title": "Logline", "type": "text", "guidance": "One sentence: protagonist, goal, obstacle."},
    {"id": "characters", "title": "Core Characters", "type": "section", "guidance": "Protagonist, antagonist, key supporting. Wants and arcs."},
    {"id": "structure", "title": "Three-Act Structure", "type": "section", "guidance": "Act I setup, Act II confrontation, Act III resolution."},
    {"id": "scenes", "title": "Scene Outline", "type": "section", "guidance": "Scene-by-scene. Location, characters, action."},
    {"id": "dialogue_notes", "title": "Dialogue Notes", "type": "section", "guidance": "Voice, subtext, key moments."},
    {"id": "revision", "title": "Revision Notes", "type": "section", "guidance": "Pacing, clarity, punch."},
]

SPEECH_PLANNING = [
    {"id": "audience", "title": "Audience", "type": "text", "guidance": "Who are they? What do they care about?"},
    {"id": "purpose", "title": "Purpose", "type": "text", "guidance": "Inform, persuade, inspire, celebrate?"},
    {"id": "key_points", "title": "Key Points", "type": "section", "guidance": "3–5 main points. One idea per point."},
    {"id": "opening", "title": "Opening", "type": "section", "guidance": "Hook. Story, question, or bold statement."},
    {"id": "closing", "title": "Closing", "type": "section", "guidance": "Call to action. Memorable takeaway."},
    {"id": "timing", "title": "Timing Notes", "type": "section", "guidance": "Word count for pace. ~150 words/min."},
]

CONTENT_TRANSFORM_PLANNING = [
    {"id": "source_material", "title": "Source Material", "type": "section", "guidance": "Episodes, posts, newsletters. What to include."},
    {"id": "theme", "title": "Unifying Theme", "type": "text", "guidance": "What ties this into a book?"},
    {"id": "structure", "title": "Book Structure", "type": "section", "guidance": "Chapters. How to group and order content."},
    {"id": "gaps", "title": "Gaps to Fill", "type": "section", "guidance": "New material needed. Transitions."},
    {"id": "revision", "title": "Revision Notes", "type": "section", "guidance": "Consistency. Flow. Cut repetition."},
]

FAITH_PLANNING = [
    {"id": "scripture", "title": "Scripture / Text", "type": "section", "guidance": "Key passages. Context."},
    {"id": "theme", "title": "Theme / Message", "type": "text", "guidance": "One main idea. Takeaway."},
    {"id": "structure", "title": "Structure", "type": "section", "guidance": "Points. Flow. Application."},
    {"id": "illustrations", "title": "Illustrations / Stories", "type": "section", "guidance": "Examples. Personal stories. Analogies."},
    {"id": "application", "title": "Application", "type": "section", "guidance": "What should listeners/readers do?"},
]

CHILDREN_PLANNING = [
    {"id": "age_range", "title": "Age Range", "type": "text", "guidance": "Target age. Affects vocabulary, length, themes."},
    {"id": "premise", "title": "Premise", "type": "text", "guidance": "Simple. One clear idea or story."},
    {"id": "characters", "title": "Characters", "type": "section", "guidance": "Protagonist. Relatable. Clear want."},
    {"id": "structure", "title": "Structure", "type": "section", "guidance": "Beginning, middle, end. Satisfying."},
    {"id": "page_spread", "title": "Page/Spread Notes", "type": "section", "guidance": "For picture books: text per spread."},
]

LIFE_STORY_PLANNING = [
    {"id": "subject", "title": "Subject", "type": "text", "guidance": "Who is this about? Scope."},
    {"id": "sources", "title": "Sources", "type": "section", "guidance": "Interviews, documents, research."},
    {"id": "timeline", "title": "Timeline", "type": "section", "guidance": "Key events. Chronology."},
    {"id": "themes", "title": "Themes", "type": "section", "guidance": "What to emphasize. Arc."},
    {"id": "voice", "title": "Voice & Tone", "type": "text", "guidance": "Objective. Intimate. Authorized?"},
]


# ---------------------------------------------------------------------------
# BUILD TEMPLATE LISTS
# ---------------------------------------------------------------------------

POETRY_TEMPLATE_DEFINITIONS: list[dict[str, Any]] = [
    _poetry_base("poetry-single", "Single Poem Drafting", "Draft and revise a single poem with structure and guidance.", "poetry", POETRY_SINGLE_PLANNING, SINGLE_POEM_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 81),
    _poetry_base("poetry-free-verse", "Free Verse", "Unmetered, unrhymed. Focus on line breaks, image, and sound.", "poetry", POETRY_SINGLE_PLANNING, FREE_VERSE_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 82),
    _poetry_base("poetry-sonnet", "Sonnet", "14 lines. Petrarchan or Shakespearean. Volta. Rhyme.", "poetry", POETRY_SINGLE_PLANNING, SONNET_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 83),
    _poetry_base("poetry-haiku", "Haiku / Short Form", "5-7-5 or variants. Moment. Image. Seasonal.", "poetry", POETRY_SINGLE_PLANNING, HAIKU_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 84),
    _poetry_base("poetry-spoken-word", "Spoken Word / Performance", "Written for the ear. Pace, rhythm, punch. Performance notes.", "poetry", POETRY_SINGLE_PLANNING, SPOKEN_WORD_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 85),
    _poetry_base("poetry-lyric", "Lyric Poem", "First-person. Musical. Concentrated feeling. Sound.", "poetry", POETRY_SINGLE_PLANNING, LYRIC_POEM_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 86),
    _poetry_base("poetry-narrative", "Narrative Poem", "Tells a story in verse. Plot, character, pacing.", "poetry", POETRY_SINGLE_PLANNING, NARRATIVE_POEM_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 87),
    _poetry_base("poetry-thematic-collection", "Thematic Poetry Collection", "Organize poems by theme. Flow, sequence, emotional arc.", "poetry", POETRY_COLLECTION_PLANNING, THEMATIC_COLLECTION_SKELETON, [{"id": "poems", "label": "Poems selected", "type": "planning"}, {"id": "sections", "label": "Sections organized", "type": "planning"}, {"id": "sequence", "label": "Sequence finalized", "type": "planning"}, {"id": "revision", "label": "Revision complete", "type": "revision"}], POETRY_AI_PROMPTS, 88),
    _poetry_base("poetry-chapbook", "Chapbook", "Short collection (20–40 pages). Cohesive. Opening and closing poems.", "poetry", POETRY_COLLECTION_PLANNING, CHAPBOOK_SKELETON, [{"id": "poems", "label": "Poems selected", "type": "planning"}, {"id": "order", "label": "Order finalized", "type": "planning"}, {"id": "revision", "label": "Revision complete", "type": "revision"}], POETRY_AI_PROMPTS, 89),
    _poetry_base("poetry-revision", "Poetry Revision", "Structured revision process. Line breaks, word choice, sound.", "poetry", POETRY_SINGLE_PLANNING, POETRY_REVISION_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 90),
    _poetry_base("poetry-ekphrastic", "Ekphrastic Poem", "Poem in response to art. Describe, dialogue, or inhabit.", "poetry", POETRY_SINGLE_PLANNING, EKPHRASIS_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 91),
    _poetry_base("poetry-devotional", "Devotional / Meditative Poetry", "Spiritual, contemplative. Focus on presence, prayer, or scripture.", "poetry", POETRY_SINGLE_PLANNING, DEVOTIONAL_POEM_SKELETON, POETRY_MILESTONES, POETRY_AI_PROMPTS, 92),
]

ADDITIONAL_TEMPLATE_DEFINITIONS: list[dict[str, Any]] = [
    # Script / Screenplay
    _creative_base(
        "script-screenplay",
        "Script / Screenplay Concept",
        "Develop a screenplay or script concept. Logline, structure, scene outline.",
        "script",
        None,
        SCRIPT_PLANNING,
        [
            {"title": "Act I", "summary": "Setup. Inciting incident. ~25%"},
            {"title": "Act II", "summary": "Confrontation. Midpoint. Complications. ~50%"},
            {"title": "Act III", "summary": "Climax. Resolution. ~25%"},
        ],
        [{"id": "outline", "label": "Outline complete", "type": "planning"}, {"id": "draft", "label": "First draft", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"structure": "Help me structure this scene.", "dialogue": "Help me tighten this dialogue."},
        130,
        book_type="fiction",
    ),
    # Speech
    _creative_base(
        "speech-writing",
        "Speech Writing",
        "Write a speech for any occasion. Audience, purpose, key points, opening, closing.",
        "speech",
        None,
        SPEECH_PLANNING,
        [
            {"title": "Opening", "summary": "Hook. 1–2 min."},
            {"title": "Point 1", "summary": "First main point with evidence or story."},
            {"title": "Point 2", "summary": "Second main point."},
            {"title": "Point 3", "summary": "Third main point."},
            {"title": "Closing", "summary": "Call to action. Memorable takeaway."},
        ],
        [{"id": "outline", "label": "Outline complete", "type": "planning"}, {"id": "draft", "label": "Draft complete", "type": "draft"}, {"id": "timing", "label": "Timing checked", "type": "revision"}],
        {"opening": "Help me write a strong opening for this speech.", "closing": "Help me write a memorable closing."},
        131,
    ),
    # Keynote
    _creative_base(
        "keynote-presentation",
        "Keynote / Presentation Narrative",
        "Structure a keynote or presentation. Story arc, key messages, slides narrative.",
        "presentation",
        None,
        SPEECH_PLANNING + [{"id": "slides", "title": "Slide Notes", "type": "section", "guidance": "Key message per slide. Visual cues."}],
        [
            {"title": "Opening", "summary": "Hook. Why this matters."},
            {"title": "Section 1", "summary": "First main message."},
            {"title": "Section 2", "summary": "Second main message."},
            {"title": "Section 3", "summary": "Third main message."},
            {"title": "Closing", "summary": "Call to action. Takeaway."},
        ],
        [{"id": "outline", "label": "Outline complete", "type": "planning"}, {"id": "draft", "label": "Narrative draft", "type": "draft"}],
        {"story": "Help me find the story in this presentation."},
        132,
    ),
    # Podcast-to-book
    _creative_base(
        "podcast-to-book",
        "Podcast-to-Book",
        "Transform podcast episodes into a cohesive book. Structure, theme, new material.",
        "content_transformation",
        None,
        CONTENT_TRANSFORM_PLANNING,
        [
            {"title": "Introduction", "summary": "Hook. Book purpose. Roadmap."},
            {"title": "Chapter 1", "summary": "From episode(s). Reworked for reading."},
            {"title": "Chapter 2", "summary": ""},
            {"title": "Chapter 3", "summary": ""},
            {"title": "Chapter 4", "summary": ""},
            {"title": "Chapter 5", "summary": ""},
            {"title": "Conclusion", "summary": "Recap. Call to action."},
        ],
        [{"id": "mapping", "label": "Episode-to-chapter mapping", "type": "planning"}, {"id": "draft", "label": "First draft", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"transition": "Help me write a transition between these sections."},
        133,
    ),
    # Sermon / Teaching
    _creative_base(
        "sermon-teaching",
        "Sermon / Teaching Message",
        "Structure a sermon or teaching message. Scripture, theme, points, application.",
        "faith",
        None,
        FAITH_PLANNING,
        [
            {"title": "Introduction", "summary": "Hook. Why this matters."},
            {"title": "Point 1", "summary": "First point. Scripture. Illustration."},
            {"title": "Point 2", "summary": "Second point."},
            {"title": "Point 3", "summary": "Third point."},
            {"title": "Application", "summary": "What should listeners do?"},
            {"title": "Closing", "summary": "Call to action. Benediction."},
        ],
        [{"id": "outline", "label": "Outline complete", "type": "planning"}, {"id": "draft", "label": "Draft complete", "type": "draft"}],
        {"illustration": "Suggest an illustration for this point."},
        134,
    ),
    # Devotional
    _creative_base(
        "devotional",
        "Devotional",
        "Daily or weekly devotional. Scripture, reflection, application.",
        "faith",
        None,
        FAITH_PLANNING,
        [
            {"title": "Entry 1", "summary": "Scripture, reflection, prayer."},
            {"title": "Entry 2", "summary": ""},
            {"title": "Entry 3", "summary": ""},
            {"title": "Entry 4", "summary": ""},
            {"title": "Entry 5", "summary": ""},
        ],
        [{"id": "theme", "label": "Theme defined", "type": "planning"}, {"id": "draft", "label": "Entries drafted", "type": "draft"}],
        {"reflection": "Help me write a reflection on this passage."},
        135,
    ),
    # Prayer / Reflection Journal
    _creative_base(
        "prayer-reflection-journal",
        "Prayer / Reflection Journal",
        "Guided journal for prayer and reflection. Prompts, scripture, space for response.",
        "faith",
        None,
        FAITH_PLANNING + [{"id": "prompts", "title": "Prompt Bank", "type": "section", "guidance": "Questions for reflection. Scripture prompts."}],
        [
            {"title": "Introduction", "summary": "How to use this journal."},
            {"title": "Week 1", "summary": "Daily or themed prompts."},
            {"title": "Week 2", "summary": ""},
            {"title": "Week 3", "summary": ""},
            {"title": "Week 4", "summary": ""},
        ],
        [{"id": "prompts", "label": "Prompts complete", "type": "planning"}, {"id": "draft", "label": "Entries drafted", "type": "draft"}],
        {"prompt": "Suggest a reflection prompt for [theme]."},
        136,
    ),
    # Newsletter-to-book
    _creative_base(
        "newsletter-to-book",
        "Newsletter-to-Book",
        "Transform newsletter content into a book. Theme, structure, new material.",
        "content_transformation",
        None,
        CONTENT_TRANSFORM_PLANNING,
        [
            {"title": "Introduction", "summary": "Hook. Book purpose."},
            {"title": "Chapter 1", "summary": "From newsletter(s). Reworked."},
            {"title": "Chapter 2", "summary": ""},
            {"title": "Chapter 3", "summary": ""},
            {"title": "Chapter 4", "summary": ""},
            {"title": "Conclusion", "summary": "Recap. Next steps."},
        ],
        [{"id": "mapping", "label": "Content mapping", "type": "planning"}, {"id": "draft", "label": "First draft", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"transition": "Help me write a transition between these chapters."},
        137,
    ),
    # Blog-to-book
    _creative_base(
        "blog-to-book",
        "Blog-to-Book",
        "Transform blog posts into a cohesive book. Theme, structure, new material.",
        "content_transformation",
        None,
        CONTENT_TRANSFORM_PLANNING,
        [
            {"title": "Introduction", "summary": "Hook. Book purpose."},
            {"title": "Chapter 1", "summary": "From post(s). Reworked."},
            {"title": "Chapter 2", "summary": ""},
            {"title": "Chapter 3", "summary": ""},
            {"title": "Chapter 4", "summary": ""},
            {"title": "Conclusion", "summary": "Recap. Call to action."},
        ],
        [{"id": "mapping", "label": "Post-to-chapter mapping", "type": "planning"}, {"id": "draft", "label": "First draft", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"transition": "Help me write a transition between these chapters."},
        138,
    ),
    # Anthology / Collected works
    _creative_base(
        "anthology-collected",
        "Anthology / Collected Works",
        "Curate and organize an anthology. Theme, selection, order, permissions.",
        "anthology",
        None,
        [
            {"id": "theme", "title": "Anthology Theme", "type": "text", "guidance": "What ties these works together?"},
            {"id": "selection", "title": "Selection Criteria", "type": "section", "guidance": "What to include. Quality bar."},
            {"id": "contents", "title": "Contents List", "type": "section", "guidance": "Works. Order. Permissions."},
            {"id": "intro", "title": "Introduction", "type": "section", "guidance": "Editor's introduction. Context."},
        ],
        [
            {"title": "Introduction", "summary": "Editor's introduction. Context."},
            {"title": "Section I", "summary": "First grouping."},
            {"title": "Section II", "summary": "Second grouping."},
            {"title": "Section III", "summary": "Third grouping."},
        ],
        [{"id": "selection", "label": "Selection complete", "type": "planning"}, {"id": "order", "label": "Order finalized", "type": "planning"}, {"id": "intro", "label": "Introduction draft", "type": "draft"}],
        {"intro": "Help me write an introduction for this anthology."},
        139,
    ),
    # Children's story
    _creative_base(
        "children-story",
        "Children's Story",
        "Write a story for children. Age-appropriate. Clear structure. Satisfying.",
        "children",
        None,
        CHILDREN_PLANNING,
        [
            {"title": "Beginning", "summary": "Introduce character and problem."},
            {"title": "Middle", "summary": "Try. Fail. Try again."},
            {"title": "End", "summary": "Resolution. Satisfying."},
        ],
        [{"id": "outline", "label": "Outline complete", "type": "planning"}, {"id": "draft", "label": "Draft complete", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"story": "Help me simplify this for a child audience."},
        140,
        book_type="fiction",
    ),
    # Picture book
    _creative_base(
        "picture-book",
        "Picture Book Planning",
        "Plan a picture book. Page spreads. Text per spread. Visual notes.",
        "children",
        None,
        CHILDREN_PLANNING,
        [
            {"title": "Spread 1", "summary": "Opening. Hook."},
            {"title": "Spread 2", "summary": ""},
            {"title": "Spread 3", "summary": ""},
            {"title": "Spread 4", "summary": ""},
            {"title": "Spread 5", "summary": ""},
            {"title": "Spread 6", "summary": ""},
            {"title": "Spread 7", "summary": ""},
            {"title": "Spread 8", "summary": "Closing. Satisfying."},
        ],
        [{"id": "outline", "label": "Spread outline complete", "type": "planning"}, {"id": "draft", "label": "Text draft", "type": "draft"}],
        {"spread": "Help me write text for this spread."},
        141,
        book_type="fiction",
    ),
    # Novella
    _creative_base(
        "novella",
        "Novella",
        "20,000–40,000 words. Focused. One main plot. Fewer subplots.",
        "fiction",
        "fiction",
        [
            {"id": "premise", "title": "Premise", "type": "text", "guidance": "One sentence. One main story."},
            {"id": "characters", "title": "Core Characters", "type": "section", "guidance": "Protagonist. Antagonist. Few."},
            {"id": "structure", "title": "Structure", "type": "section", "guidance": "Setup, confrontation, resolution. Tight."},
            {"id": "chapters", "title": "Chapter Outline", "type": "section", "guidance": "5–10 chapters. Focused."},
        ],
        [
            {"title": "Chapter 1", "summary": "Setup. Hook."},
            {"title": "Chapter 2", "summary": "Inciting incident."},
            {"title": "Chapter 3", "summary": "Rising action."},
            {"title": "Chapter 4", "summary": "Midpoint."},
            {"title": "Chapter 5", "summary": "Crisis. Climax."},
            {"title": "Chapter 6", "summary": "Resolution."},
        ],
        [{"id": "outline", "label": "Outline complete", "type": "planning"}, {"id": "draft", "label": "Draft complete", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"scene": "Help me write a scene that shows [emotion/conflict]."},
        142,
        book_type="fiction",
    ),
    # Short story cycle
    _creative_base(
        "short-story-cycle",
        "Short Story Cycle",
        "Linked stories. Shared characters, setting, or theme. Standalone but connected.",
        "short_story_collection",
        "short-story-collection",
        [
            {"id": "link", "title": "Linking Element", "type": "text", "guidance": "What connects these stories? Character, place, theme?"},
            {"id": "stories", "title": "Story List", "type": "section", "guidance": "Each story. Order and connection."},
            {"id": "sequence", "title": "Sequence", "type": "section", "guidance": "Order. Echoes. Arc."},
        ],
        [
            {"title": "Story 1", "summary": "First story. Establishes world."},
            {"title": "Story 2", "summary": ""},
            {"title": "Story 3", "summary": ""},
            {"title": "Story 4", "summary": ""},
            {"title": "Story 5", "summary": "Final story. Resonance."},
        ],
        [{"id": "stories", "label": "Stories drafted", "type": "draft"}, {"id": "links", "label": "Links strengthened", "type": "revision"}],
        {"link": "Help me create a subtle link between these stories."},
        143,
        book_type="fiction",
    ),
    # Anthology editor
    _creative_base(
        "anthology-editor",
        "Anthology Editor",
        "Editor workflow. Selection, permissions, introduction, order.",
        "anthology",
        None,
        [
            {"id": "theme", "title": "Anthology Theme", "type": "text", "guidance": "What ties these works together?"},
            {"id": "selection", "title": "Selection Criteria", "type": "section", "guidance": "What to include."},
            {"id": "contents", "title": "Contents & Permissions", "type": "section", "guidance": "Works. Order. Permissions tracking."},
            {"id": "intro", "title": "Introduction", "type": "section", "guidance": "Editor's introduction."},
        ],
        [
            {"title": "Introduction", "summary": "Editor's introduction."},
            {"title": "Section I", "summary": "First grouping."},
            {"title": "Section II", "summary": "Second grouping."},
            {"title": "Section III", "summary": "Third grouping."},
        ],
        [{"id": "selection", "label": "Selection complete", "type": "planning"}, {"id": "permissions", "label": "Permissions secured", "type": "planning"}, {"id": "intro", "label": "Introduction draft", "type": "draft"}],
        {"intro": "Help me write an introduction for this anthology."},
        144,
    ),
    # Client ghostwriting intake
    _creative_base(
        "ghostwriting-intake",
        "Client Ghostwriting Intake",
        "Structured intake for ghostwriting projects. Client profile, voice, objectives, timeline.",
        "ghostwritten_book",
        "ghostwritten-book",
        [
            {"id": "client_profile", "title": "Client Profile", "type": "section", "guidance": "Name, background, expertise. Audience."},
            {"id": "voice_notes", "title": "Voice Notes", "type": "section", "guidance": "Key phrases. Tone. Style."},
            {"id": "objectives", "title": "Book Objectives", "type": "text", "guidance": "What does the client want to achieve?"},
            {"id": "source_material", "title": "Source Material", "type": "section", "guidance": "Interviews, documents, existing content."},
            {"id": "timeline", "title": "Timeline", "type": "section", "guidance": "Milestones. Approval points."},
        ],
        [
            {"title": "Intake Summary", "summary": "Client profile. Objectives. Voice."},
            {"title": "Outline", "summary": "Proposed structure."},
            {"title": "Sample Chapter", "summary": "Voice sample for approval."},
        ],
        [{"id": "intake", "label": "Intake complete", "type": "planning"}, {"id": "outline_approved", "label": "Outline approved", "type": "planning"}],
        {"voice": "Help me match this passage to the client's voice."},
        145,
    ),
    # Biography
    _creative_base(
        "biography",
        "Biography",
        "Life story of another person. Research, timeline, themes. Authorized or independent.",
        "life_story",
        None,
        LIFE_STORY_PLANNING,
        [
            {"title": "Introduction", "summary": "Why this person? Why now?"},
            {"title": "Early Life", "summary": "Origins. Formative years."},
            {"title": "Rise / Key Period", "summary": "Major achievements. Turning points."},
            {"title": "Later Life", "summary": "Legacy. Later years."},
            {"title": "Conclusion", "summary": "Assessment. Significance."},
        ],
        [{"id": "research", "label": "Research complete", "type": "planning"}, {"id": "outline", "label": "Outline approved", "type": "planning"}, {"id": "draft", "label": "Draft complete", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"synthesis": "Help me synthesize these sources into a coherent paragraph."},
        146,
    ),
    # Autobiography
    _creative_base(
        "autobiography",
        "Autobiography",
        "Your own life story. First-person. Chronological or thematic.",
        "life_story",
        None,
        LIFE_STORY_PLANNING,
        [
            {"title": "Introduction", "summary": "Why this story? Why now?"},
            {"title": "Early Life", "summary": "Origins. Formative years."},
            {"title": "Key Periods", "summary": "Major phases. Turning points."},
            {"title": "Later Life", "summary": "Where you are now."},
            {"title": "Reflection", "summary": "What it means. Lessons."},
        ],
        [{"id": "outline", "label": "Outline complete", "type": "planning"}, {"id": "draft", "label": "Draft complete", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"memory": "Help me turn this memory into a scene."},
        147,
    ),
    # Case-study collection
    _creative_base(
        "case-study-collection",
        "Case Study Collection",
        "Multiple case studies. Unified theme. Analysis framework.",
        "nonfiction",
        "nonfiction",
        [
            {"id": "framework", "title": "Analytical Framework", "type": "section", "guidance": "How will you analyze each case?"},
            {"id": "cases", "title": "Case List", "type": "section", "guidance": "Cases to include. Selection criteria."},
            {"id": "structure", "title": "Structure", "type": "section", "guidance": "Intro, cases, synthesis."},
        ],
        [
            {"title": "Introduction", "summary": "Framework. Why these cases."},
            {"title": "Case 1", "summary": "Background, analysis, takeaways."},
            {"title": "Case 2", "summary": ""},
            {"title": "Case 3", "summary": ""},
            {"title": "Synthesis", "summary": "Cross-case analysis. Implications."},
        ],
        [{"id": "framework", "label": "Framework defined", "type": "planning"}, {"id": "draft", "label": "Cases drafted", "type": "draft"}, {"id": "synthesis", "label": "Synthesis complete", "type": "draft"}],
        {"analysis": "Help me analyze this case using the framework."},
        148,
    ),
    # Interview-based book
    _creative_base(
        "interview-based-book",
        "Interview-Based Book",
        "Book built from interviews. Oral history, narrative, or thematic organization.",
        "life_story",
        None,
        LIFE_STORY_PLANNING + [{"id": "interviews", "title": "Interview Log", "type": "section", "guidance": "Interviews conducted. Key quotes."}],
        [
            {"title": "Introduction", "summary": "Context. What this book reveals."},
            {"title": "Chapter 1", "summary": "Thematic or narrative grouping."},
            {"title": "Chapter 2", "summary": ""},
            {"title": "Chapter 3", "summary": ""},
            {"title": "Chapter 4", "summary": ""},
            {"title": "Conclusion", "summary": "Synthesis. Significance."},
        ],
        [{"id": "interviews", "label": "Interviews complete", "type": "planning"}, {"id": "draft", "label": "Draft complete", "type": "draft"}, {"id": "revision", "label": "Revision", "type": "revision"}],
        {"quote": "Help me integrate this quote into the narrative."},
        149,
    ),
]
