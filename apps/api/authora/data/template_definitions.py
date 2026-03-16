"""Project template definitions for AUTHORA.

All 10 top-level categories plus genre-specific sub-templates.
Each template includes default structure, milestones, planning prompts,
accountability, AI prompts, export recommendations, and setup questions.

First-wave premium templates (Romance, Fantasy, Thriller, Sci-fi, Memoir,
Self-help, Business, Workbook) are enhanced with polished setup flows,
revision checklists, export readiness checklists, and writing prompts.
"""

from typing import Any

from authora.data.premium_templates import get_premium_overrides

# Shared fiction planning sections
FICTION_PLANNING_SECTIONS = [
    {"id": "premise", "title": "Book Premise", "type": "text"},
    {"id": "characters", "title": "Core Characters", "type": "section"},
    {"id": "setting", "title": "Setting / World", "type": "section"},
    {"id": "themes", "title": "Themes", "type": "text"},
    {"id": "plot_arc", "title": "Plot Arc", "type": "section"},
    {"id": "act_structure", "title": "Act Structure", "type": "section"},
    {"id": "chapter_roadmap", "title": "Chapter Roadmap", "type": "section"},
    {"id": "scene_ideas", "title": "Scene Ideas", "type": "section"},
    {"id": "research", "title": "Research Notes", "type": "section"},
    {"id": "revision", "title": "Revision Notes", "type": "section"},
]

# Shared nonfiction planning sections
NONFICTION_PLANNING_SECTIONS = [
    {"id": "core_idea", "title": "Core Idea", "type": "text"},
    {"id": "reader_problem", "title": "Reader Problem", "type": "text"},
    {"id": "promised_outcome", "title": "Promised Outcome", "type": "text"},
    {"id": "positioning", "title": "Book Positioning", "type": "text"},
    {"id": "chapter_outline", "title": "Chapter Outline", "type": "section"},
    {"id": "frameworks", "title": "Frameworks and Models", "type": "section"},
    {"id": "stories", "title": "Stories and Examples", "type": "section"},
    {"id": "research", "title": "Research Notes", "type": "section"},
    {"id": "references", "title": "References", "type": "section"},
    {"id": "revision", "title": "Revision Notes", "type": "section"},
]

# Memoir planning sections
MEMOIR_PLANNING_SECTIONS = [
    {"id": "why_matters", "title": "Why This Story Matters", "type": "text"},
    {"id": "defining_moments", "title": "Defining Moments", "type": "section"},
    {"id": "emotional_turning", "title": "Emotional Turning Points", "type": "section"},
    {"id": "relationships", "title": "Important Relationships", "type": "section"},
    {"id": "timeline", "title": "Timeline", "type": "section"},
    {"id": "chapter_map", "title": "Chapter Map", "type": "section"},
    {"id": "reflection_themes", "title": "Reflection Themes", "type": "section"},
    {"id": "sensitive_content", "title": "Sensitive Content Notes", "type": "text"},
    {"id": "revision", "title": "Revision Notes", "type": "section"},
]

# Default milestones
DEFAULT_MILESTONES = {
    "fiction": [
        {"id": "outline", "label": "Outline complete", "type": "planning"},
        {"id": "act1", "label": "Act I draft complete", "type": "draft"},
        {"id": "act2", "label": "Act II draft complete", "type": "draft"},
        {"id": "act3", "label": "Act III draft complete", "type": "draft"},
        {"id": "first_revision", "label": "First revision pass", "type": "revision"},
        {"id": "beta", "label": "Beta reader feedback", "type": "feedback"},
        {"id": "final", "label": "Final polish", "type": "revision"},
    ],
    "nonfiction": [
        {"id": "outline", "label": "Chapter outline complete", "type": "planning"},
        {"id": "intro", "label": "Introduction draft", "type": "draft"},
        {"id": "core_chapters", "label": "Core chapters draft", "type": "draft"},
        {"id": "conclusion", "label": "Conclusion draft", "type": "draft"},
        {"id": "first_revision", "label": "First revision pass", "type": "revision"},
        {"id": "expert_review", "label": "Expert review", "type": "feedback"},
        {"id": "final", "label": "Final polish", "type": "revision"},
    ],
}

# Default accountability
DEFAULT_ACCOUNTABILITY = {
    "reminder_frequency": "weekly",
    "goal_type": "words",
    "default_target_words": 1000,
    "check_in_prompts": ["What did you accomplish this week?", "What's your focus for next week?"],
}


def _fiction_base(slug: str, name: str, description: str, genre: str, **overrides: Any) -> dict[str, Any]:
    """Base fiction template."""
    return {
        "slug": slug,
        "category": "fiction",
        "parent_slug": None,
        "name": name,
        "description": description,
        "who_it_is_for": "Fiction writers who want structure without losing creative freedom.",
        "expected_outcome": "A complete novel draft with clear plot, characters, and pacing.",
        "suggested_workflow": "Plan → Draft Act I → Draft Act II → Draft Act III → Revise → Polish.",
        "book_type": "fiction",
        "genre": genre,
        "structure_framework": "three_act",
        "default_structure": {"planning_sections": FICTION_PLANNING_SECTIONS},
        "default_milestones": DEFAULT_MILESTONES["fiction"],
        "default_planning_prompts": {
            "premise": "What is the one-sentence premise of your story?",
            "protagonist": "Who is your protagonist and what do they want?",
            "conflict": "What stands in their way?",
            "theme": "What is the story really about?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "brainstorm": "Help me brainstorm plot twists for my [genre] novel.",
            "character": "Help me deepen my character's motivation and arc.",
            "scene": "Help me write a scene that shows [emotion/conflict].",
        },
        "export_recommendations": ["docx", "epub", "pdf"],
        "setup_questions": [
            {"id": "premise", "prompt": "What's your story's core premise in one sentence?", "type": "text"},
            {"id": "genre", "prompt": "What genre best fits your book?", "type": "select", "options": "fiction_genres"},
            {"id": "pov", "prompt": "What point of view will you use?", "type": "select", "options": ["first", "third_limited", "third_omniscient"]},
            {"id": "tense", "prompt": "Past or present tense?", "type": "select", "options": ["past", "present"]},
            {"id": "structure", "prompt": "Which structure framework?", "type": "select", "options": ["three_act", "hero_journey", "romance_beats", "save_the_cat", "custom"]},
        ],
        "chapter_skeletons": [
            {"title": "Chapter 1", "summary": "Opening – hook and establish stakes"},
            {"title": "Chapter 2", "summary": "Introduce world and supporting characters"},
            {"title": "Chapter 3", "summary": "Inciting incident"},
            {"title": "Chapter 4", "summary": "First major obstacle"},
            {"title": "Chapter 5", "summary": "Rising action"},
            {"title": "Chapter 6", "summary": "Midpoint – revelation or reversal"},
            {"title": "Chapter 7", "summary": "Complications"},
            {"title": "Chapter 8", "summary": "All is lost"},
            {"title": "Chapter 9", "summary": "Climax"},
            {"title": "Chapter 10", "summary": "Resolution"},
        ],
        "sort_order": 0,
        "is_featured": False,
        "is_disabled": False,
        **overrides,
    }


def _nonfiction_base(slug: str, name: str, description: str, genre: str, **overrides: Any) -> dict[str, Any]:
    """Base nonfiction template."""
    return {
        "slug": slug,
        "category": "nonfiction",
        "parent_slug": None,
        "name": name,
        "description": description,
        "who_it_is_for": "Experts, coaches, and thought leaders who want to share knowledge in book form.",
        "expected_outcome": "A complete nonfiction manuscript that transforms readers.",
        "suggested_workflow": "Define problem → Outline solution → Draft chapters → Add examples → Revise → Polish.",
        "book_type": "nonfiction",
        "genre": genre,
        "structure_framework": "problem_solution_result",
        "default_structure": {"planning_sections": NONFICTION_PLANNING_SECTIONS},
        "default_milestones": DEFAULT_MILESTONES["nonfiction"],
        "default_planning_prompts": {
            "core_idea": "What is the one big idea of your book?",
            "reader_problem": "What problem does your reader have?",
            "outcome": "What transformation do you promise?",
            "authority": "Why are you the right person to write this?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "outline": "Help me outline a chapter on [topic].",
            "example": "Suggest a case study or story that illustrates [concept].",
            "cta": "Help me write a strong call to action for this section.",
        },
        "export_recommendations": ["docx", "pdf", "epub"],
        "setup_questions": [
            {"id": "purpose", "prompt": "What is the main purpose of your book?", "type": "text"},
            {"id": "target_reader", "prompt": "Who is your ideal reader?", "type": "text"},
            {"id": "transformation", "prompt": "What transformation do you promise?", "type": "text"},
            {"id": "structure", "prompt": "Which structure fits best?", "type": "select", "options": ["problem_solution_result", "step_by_step", "authority", "instructional", "modular", "custom"]},
        ],
        "chapter_skeletons": [
            {"title": "Introduction", "summary": "Hook, promise, roadmap"},
            {"title": "Chapter 1", "summary": "Define the problem"},
            {"title": "Chapter 2", "summary": "Why existing solutions fall short"},
            {"title": "Chapter 3", "summary": "Introduce your framework"},
            {"title": "Chapter 4", "summary": "Step 1 – with examples"},
            {"title": "Chapter 5", "summary": "Step 2 – with examples"},
            {"title": "Chapter 6", "summary": "Step 3 – with examples"},
            {"title": "Chapter 7", "summary": "Getting started – first 30 days"},
            {"title": "Chapter 8", "summary": "Common pitfalls"},
            {"title": "Conclusion", "summary": "Recap, call to action"},
        ],
        "sort_order": 0,
        "is_featured": False,
        "is_disabled": False,
        **overrides,
    }


def _apply_premium(defn: dict[str, Any]) -> dict[str, Any]:
    """Apply premium overrides if this template has them."""
    overrides = get_premium_overrides()
    slug = defn.get("slug")
    if slug and slug in overrides:
        return {**defn, **overrides[slug]}
    return defn


# ---------------------------------------------------------------------------
# TOP-LEVEL TEMPLATES (parent_slug=None)
# ---------------------------------------------------------------------------

TEMPLATE_DEFINITIONS_RAW: list[dict[str, Any]] = [
    # 1. FICTION (parent)
    _fiction_base(
        "fiction",
        "Fiction Novel",
        "Build stories with structure, character, tension, and momentum.",
        "General Fiction",
        who_it_is_for="Fiction writers of any genre who want a structured approach.",
        is_featured=False,
        sort_order=10,
    ),
    # Fiction sub-templates
    _fiction_base("fiction-romance", "Romance", "Romance novel with meet-cute, tension, and HEA.", "Romance", parent_slug="fiction", structure_framework="romance_beats", sort_order=11),
    _fiction_base("fiction-fantasy", "Fantasy", "Epic or contemporary fantasy with worldbuilding.", "Fantasy", parent_slug="fiction", sort_order=12),
    _fiction_base("fiction-thriller", "Thriller / Mystery", "Suspense-driven plot with clues and twists.", "Thriller", parent_slug="fiction", structure_framework="mystery_thriller", sort_order=13),
    _fiction_base("fiction-scifi", "Sci-Fi", "Science fiction with technology and speculative elements.", "Science Fiction", parent_slug="fiction", sort_order=14),
    _fiction_base("fiction-horror", "Horror", "Horror with atmosphere, dread, and payoff.", "Horror", parent_slug="fiction", sort_order=15),
    _fiction_base("fiction-historical", "Historical Fiction", "Period-accurate historical narrative.", "Historical Fiction", parent_slug="fiction", sort_order=16),
    _fiction_base("fiction-literary", "Literary Fiction", "Character-driven literary fiction.", "Literary Fiction", parent_slug="fiction", sort_order=17),
    _fiction_base("fiction-ya", "Young Adult", "YA fiction with coming-of-age themes.", "Young Adult", parent_slug="fiction", sort_order=18),
    _fiction_base("fiction-contemporary", "Contemporary Fiction", "Modern-day realistic fiction.", "Contemporary Fiction", parent_slug="fiction", sort_order=19),
    _fiction_base("fiction-short", "Short Story / Novella", "Shorter fiction form.", "Short Story", parent_slug="fiction", chapter_skeletons=[{"title": "Scene 1", "summary": ""}, {"title": "Scene 2", "summary": ""}, {"title": "Scene 3", "summary": ""}], sort_order=20),
    _fiction_base("fiction-series", "Series Fiction", "First book in a planned series.", "Series", parent_slug="fiction", sort_order=21),
    _fiction_base("fiction-general", "General Fiction", "Fiction without strict genre constraints.", "General Fiction", parent_slug="fiction", sort_order=22),
    # 2. NON-FICTION (parent)
    _nonfiction_base(
        "nonfiction",
        "Non-Fiction Book",
        "A complete nonfiction template with problem-solution structure and reader transformation.",
        "General Non-fiction",
        who_it_is_for="Experts, coaches, entrepreneurs, and thought leaders.",
        is_featured=False,
        sort_order=30,
    ),
    # Nonfiction sub-templates
    _nonfiction_base("nonfiction-selfhelp", "Self-Help", "Transformational self-help book.", "Self-Help", parent_slug="nonfiction", sort_order=31),
    _nonfiction_base("nonfiction-business", "Business", "Business book for professionals.", "Business", parent_slug="nonfiction", sort_order=32),
    _nonfiction_base("nonfiction-finance", "Finance", "Personal finance or investing book.", "Finance", parent_slug="nonfiction", sort_order=33),
    _nonfiction_base("nonfiction-health", "Health / Wellness", "Health, wellness, or fitness book.", "Health", parent_slug="nonfiction", sort_order=34),
    _nonfiction_base("nonfiction-parenting", "Parenting", "Parenting advice and guidance.", "Parenting", parent_slug="nonfiction", sort_order=35),
    _nonfiction_base("nonfiction-relationships", "Relationships", "Relationship book.", "Relationships", parent_slug="nonfiction", sort_order=36),
    _nonfiction_base("nonfiction-educational", "Educational / Teaching", "Teaching or educational resource.", "Educational", parent_slug="nonfiction", sort_order=37),
    _nonfiction_base("nonfiction-thought-leadership", "Thought Leadership", "Positioning as industry authority.", "Thought Leadership", parent_slug="nonfiction", sort_order=38),
    _nonfiction_base("nonfiction-howto", "How-to / Instructional", "Step-by-step instructional guide.", "How-To", parent_slug="nonfiction", structure_framework="instructional", sort_order=39),
    _nonfiction_base("nonfiction-faith", "Faith / Spirituality", "Faith-based or spiritual book.", "Faith", parent_slug="nonfiction", sort_order=40),
    _nonfiction_base("nonfiction-professional", "Professional Authority Book", "Establish expertise in your field.", "Professional", parent_slug="nonfiction", structure_framework="authority", sort_order=41),
    _nonfiction_base("nonfiction-general", "General Non-fiction", "Nonfiction without strict category.", "General Non-fiction", parent_slug="nonfiction", sort_order=42),
    # 3. MEMOIR
    {
        "slug": "memoir",
        "category": "memoir",
        "parent_slug": None,
        "name": "Memoir",
        "description": "Shape lived experience into a story with meaning, emotion, and reflection.",
        "who_it_is_for": "Writers sharing their life story with meaning and structure.",
        "expected_outcome": "A compelling memoir that resonates with readers.",
        "suggested_workflow": "Map timeline → Identify themes → Group by life stage → Draft → Reflect → Revise.",
        "book_type": "nonfiction",
        "genre": "Memoir",
        "structure_framework": "emotional_arc",
        "default_structure": {"planning_sections": MEMOIR_PLANNING_SECTIONS},
        "default_milestones": [
            {"id": "timeline", "label": "Timeline mapped", "type": "planning"},
            {"id": "themes", "label": "Themes identified", "type": "planning"},
            {"id": "outline", "label": "Chapter map complete", "type": "planning"},
            {"id": "first_half", "label": "First half draft", "type": "draft"},
            {"id": "second_half", "label": "Second half draft", "type": "draft"},
            {"id": "sensitivity", "label": "Sensitivity review", "type": "revision"},
            {"id": "final", "label": "Final polish", "type": "revision"},
        ],
        "default_planning_prompts": {
            "why": "Why does this story need to be told?",
            "defining_moments": "What are the 3–5 defining moments?",
            "emotional_arc": "What is the emotional journey?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "memory": "Help me turn this memory into a scene.",
            "reflection": "Help me articulate the lesson from this experience.",
        },
        "export_recommendations": ["docx", "epub", "pdf"],
        "setup_questions": [
            {"id": "central_theme", "prompt": "What central life theme does your memoir explore?", "type": "text"},
            {"id": "timeframe", "prompt": "What time period does it cover?", "type": "text"},
            {"id": "sensitive", "prompt": "Any sensitive content to handle carefully?", "type": "text"},
        ],
        "chapter_skeletons": [
            {"title": "Prologue", "summary": "Hook – a defining moment"},
            {"title": "Chapter 1", "summary": "Early life / setup"},
            {"title": "Chapter 2", "summary": "First turning point"},
            {"title": "Chapter 3", "summary": "Rising action"},
            {"title": "Chapter 4", "summary": "Crisis or climax"},
            {"title": "Chapter 5", "summary": "Resolution and reflection"},
            {"title": "Epilogue", "summary": "Where you are now"},
        ],
        "sort_order": 50,
        "is_featured": True,
        "is_disabled": False,
    },
    # 4. WORKBOOK
    {
        "slug": "workbook",
        "category": "workbook",
        "parent_slug": None,
        "name": "Workbook",
        "description": "Create guided content with prompts, exercises, and action-oriented structure.",
        "who_it_is_for": "Coaches, educators, and facilitators creating hands-on learning experiences.",
        "expected_outcome": "A printable, export-ready workbook readers can work through.",
        "suggested_workflow": "Define outcomes → Design modules → Write prompts → Add worksheets → Test → Export.",
        "book_type": "nonfiction",
        "genre": "Workbook",
        "structure_framework": "module_exercise",
        "default_structure": {
            "planning_sections": [
                {"id": "outcomes", "title": "Learning Outcomes", "type": "section"},
                {"id": "modules", "title": "Module Structure", "type": "section"},
                {"id": "prompts", "title": "Prompt Sets", "type": "section"},
                {"id": "worksheets", "title": "Worksheet Sections", "type": "section"},
                {"id": "reflections", "title": "Reflection Blocks", "type": "section"},
                {"id": "action_plans", "title": "Action Plans", "type": "section"},
                {"id": "export_notes", "title": "Printable/Export Notes", "type": "section"},
            ]
        },
        "default_milestones": [
            {"id": "outcomes", "label": "Learning outcomes defined", "type": "planning"},
            {"id": "modules", "label": "Module structure complete", "type": "planning"},
            {"id": "draft", "label": "All modules drafted", "type": "draft"},
            {"id": "exercises", "label": "Exercises and worksheets done", "type": "draft"},
            {"id": "test", "label": "Test run with beta users", "type": "feedback"},
            {"id": "export", "label": "Export-ready", "type": "revision"},
        ],
        "default_planning_prompts": {
            "outcomes": "What will readers be able to do after completing this workbook?",
            "modules": "How many modules and what is each one teaching?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "prompt": "Help me write a reflection prompt for [topic].",
            "exercise": "Suggest an exercise for [learning outcome].",
        },
        "export_recommendations": ["docx", "pdf"],
        "setup_questions": [
            {"id": "purpose", "prompt": "What is the workbook's main purpose?", "type": "text"},
            {"id": "modules", "prompt": "How many modules or sections?", "type": "number"},
        ],
        "chapter_skeletons": [
            {"title": "Introduction", "summary": "How to use this workbook"},
            {"title": "Module 1", "summary": "Teaching + exercises"},
            {"title": "Module 2", "summary": "Teaching + exercises"},
            {"title": "Module 3", "summary": "Teaching + exercises"},
            {"title": "Module 4", "summary": "Teaching + exercises"},
            {"title": "Module 5", "summary": "Teaching + exercises"},
            {"title": "Conclusion", "summary": "Next steps and action plan"},
        ],
        "sort_order": 60,
        "is_featured": False,
        "is_disabled": False,
    },
    # 5. JOURNAL
    {
        "slug": "journal",
        "category": "journal",
        "parent_slug": None,
        "name": "Journal",
        "description": "Design reflective writing experiences with prompts, rhythms, and themes.",
        "who_it_is_for": "Writers creating guided journals for readers.",
        "expected_outcome": "A journal template ready for print or digital use.",
        "suggested_workflow": "Define purpose → Create prompt bank → Build entry structure → Design layout.",
        "book_type": "nonfiction",
        "genre": "Journal",
        "structure_framework": "prompt_based",
        "default_structure": {
            "planning_sections": [
                {"id": "purpose", "title": "Journal Purpose", "type": "text"},
                {"id": "prompt_bank", "title": "Prompt Bank", "type": "section"},
                {"id": "entry_structure", "title": "Entry Structure", "type": "section"},
                {"id": "time_sections", "title": "Time-Based Sections", "type": "section"},
                {"id": "themes", "title": "Themes", "type": "section"},
                {"id": "tone_layout", "title": "Notes on Tone and Layout", "type": "text"},
            ]
        },
        "default_milestones": [
            {"id": "prompts", "label": "Prompt bank complete", "type": "planning"},
            {"id": "structure", "label": "Entry structure defined", "type": "planning"},
            {"id": "draft", "label": "Sample entries drafted", "type": "draft"},
            {"id": "layout", "label": "Layout notes complete", "type": "draft"},
            {"id": "export", "label": "Export-ready", "type": "revision"},
        ],
        "default_planning_prompts": {
            "purpose": "What is the journal's purpose?",
            "tone": "What tone should entries have?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "prompt": "Suggest a daily reflection prompt for [theme].",
        },
        "export_recommendations": ["pdf", "docx"],
        "setup_questions": [
            {"id": "purpose", "prompt": "What is this journal for?", "type": "text"},
            {"id": "frequency", "prompt": "Daily, weekly, or themed?", "type": "select", "options": ["daily", "weekly", "themed"]},
        ],
        "chapter_skeletons": [
            {"title": "Introduction", "summary": "How to use this journal"},
            {"title": "Week 1 Prompts", "summary": ""},
            {"title": "Week 2 Prompts", "summary": ""},
            {"title": "Week 3 Prompts", "summary": ""},
            {"title": "Week 4 Prompts", "summary": ""},
        ],
        "sort_order": 70,
        "is_featured": False,
        "is_disabled": False,
    },
    # 6. POETRY
    {
        "slug": "poetry",
        "category": "poetry",
        "parent_slug": None,
        "name": "Poetry Collection",
        "description": "Organize a collection with flow, sequence, and emotional shape.",
        "who_it_is_for": "Poets organizing a cohesive collection.",
        "expected_outcome": "A polished poetry collection ready for submission or publication.",
        "suggested_workflow": "Define theme → List poems → Group into sections → Order → Revise → Submit.",
        "book_type": "fiction",
        "genre": "Poetry",
        "structure_framework": "section_sequence",
        "default_structure": {
            "planning_sections": [
                {"id": "theme", "title": "Collection Theme", "type": "text"},
                {"id": "poem_list", "title": "Poem List", "type": "section"},
                {"id": "sections", "title": "Section Grouping", "type": "section"},
                {"id": "tone", "title": "Emotional Tone", "type": "text"},
                {"id": "sequence", "title": "Sequence Planning", "type": "section"},
                {"id": "revision", "title": "Revision Tracking", "type": "section"},
            ]
        },
        "default_milestones": [
            {"id": "theme", "label": "Theme defined", "type": "planning"},
            {"id": "poems", "label": "Poems selected", "type": "planning"},
            {"id": "sections", "label": "Sections organized", "type": "planning"},
            {"id": "sequence", "label": "Sequence finalized", "type": "planning"},
            {"id": "revision", "label": "Revision pass complete", "type": "revision"},
            {"id": "submit", "label": "Submission ready", "type": "revision"},
        ],
        "default_planning_prompts": {
            "theme": "What ties these poems together?",
            "tone": "What emotional journey does the collection take?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "feedback": "Give feedback on this poem's imagery and rhythm.",
        },
        "export_recommendations": ["docx", "pdf", "epub"],
        "setup_questions": [
            {"id": "theme", "prompt": "What is the collection's theme?", "type": "text"},
            {"id": "sections", "prompt": "How many sections?", "type": "number"},
        ],
        "chapter_skeletons": [
            {"title": "Section I", "summary": ""},
            {"title": "Section II", "summary": ""},
            {"title": "Section III", "summary": ""},
        ],
        "sort_order": 80,
        "is_featured": False,
        "is_disabled": False,
    },
    # 7. SHORT STORY COLLECTION
    {
        "slug": "short-story-collection",
        "category": "short_story_collection",
        "parent_slug": None,
        "name": "Short Story Collection",
        "description": "Build a cohesive set of stories with shared themes and strong structure.",
        "who_it_is_for": "Short story writers preparing a collection for submission.",
        "expected_outcome": "A cohesive short story collection ready for submission.",
        "suggested_workflow": "Select stories → Identify themes → Order → Revise for cohesion → Submit.",
        "book_type": "fiction",
        "genre": "Short Story",
        "structure_framework": "collection_sequence",
        "default_structure": {
            "planning_sections": [
                {"id": "theme", "title": "Collection Theme", "type": "text"},
                {"id": "story_cards", "title": "Individual Story Cards", "type": "section"},
                {"id": "structure", "title": "Story Structure Tracking", "type": "section"},
                {"id": "shared_themes", "title": "Shared Themes", "type": "section"},
                {"id": "sequence", "title": "Order/Sequence Planning", "type": "section"},
                {"id": "submission", "title": "Revision and Submission Readiness", "type": "section"},
            ]
        },
        "default_milestones": [
            {"id": "stories", "label": "Stories selected", "type": "planning"},
            {"id": "order", "label": "Order finalized", "type": "planning"},
            {"id": "revision", "label": "Revision for cohesion", "type": "revision"},
            {"id": "submit", "label": "Submission ready", "type": "revision"},
        ],
        "default_planning_prompts": {
            "theme": "What connects these stories?",
            "order": "What order creates the best reading experience?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "story": "Help me tighten this story's ending.",
        },
        "export_recommendations": ["docx", "pdf", "epub"],
        "setup_questions": [
            {"id": "theme", "prompt": "What theme ties the collection together?", "type": "text"},
            {"id": "count", "prompt": "How many stories?", "type": "number"},
        ],
        "chapter_skeletons": [
            {"title": "Story 1", "summary": ""},
            {"title": "Story 2", "summary": ""},
            {"title": "Story 3", "summary": ""},
            {"title": "Story 4", "summary": ""},
            {"title": "Story 5", "summary": ""},
        ],
        "sort_order": 90,
        "is_featured": False,
        "is_disabled": False,
    },
    # 8. SERIES PROJECT
    {
        "slug": "series-project",
        "category": "series_project",
        "parent_slug": None,
        "name": "Series Project",
        "description": "Plan connected books with continuity, lore, and long-form story arcs.",
        "who_it_is_for": "Writers planning a book series with recurring characters and world.",
        "expected_outcome": "A series bible and first book (or more) with clear continuity.",
        "suggested_workflow": "Series bible → Book 1 outline → Draft Book 1 → Plan Book 2 → Repeat.",
        "book_type": "fiction",
        "genre": "Series",
        "structure_framework": "series_arc",
        "default_structure": {
            "planning_sections": [
                {"id": "series_premise", "title": "Series Premise", "type": "text"},
                {"id": "installment_arcs", "title": "Installment Arcs", "type": "section"},
                {"id": "recurring_characters", "title": "Recurring Characters", "type": "section"},
                {"id": "world_lore", "title": "World/Lore Continuity", "type": "section"},
                {"id": "series_timeline", "title": "Series Timeline", "type": "section"},
                {"id": "per_book_goals", "title": "Per-Book Goals", "type": "section"},
                {"id": "cross_book_notes", "title": "Cross-Book Notes", "type": "section"},
                {"id": "continuity_tracker", "title": "Continuity Tracker", "type": "section"},
            ]
        },
        "default_milestones": [
            {"id": "bible", "label": "Series bible complete", "type": "planning"},
            {"id": "book1_outline", "label": "Book 1 outline", "type": "planning"},
            {"id": "book1_draft", "label": "Book 1 draft", "type": "draft"},
            {"id": "book2_plan", "label": "Book 2 planned", "type": "planning"},
            {"id": "book1_revision", "label": "Book 1 revised", "type": "revision"},
        ],
        "default_planning_prompts": {
            "series_premise": "What is the overarching series premise?",
            "book_arcs": "What happens in each book?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "continuity": "Help me check continuity for [element].",
            "arc": "Help me plan the arc for book [n].",
        },
        "export_recommendations": ["docx", "epub", "pdf"],
        "setup_questions": [
            {"id": "series_premise", "prompt": "What is the series premise?", "type": "text"},
            {"id": "book_count", "prompt": "How many books planned?", "type": "number"},
        ],
        "chapter_skeletons": [
            {"title": "Chapter 1", "summary": "Series opener"},
            {"title": "Chapter 2", "summary": ""},
            {"title": "Chapter 3", "summary": ""},
            {"title": "Chapter 4", "summary": ""},
            {"title": "Chapter 5", "summary": ""},
            {"title": "Chapter 6", "summary": ""},
            {"title": "Chapter 7", "summary": ""},
            {"title": "Chapter 8", "summary": ""},
            {"title": "Chapter 9", "summary": ""},
            {"title": "Chapter 10", "summary": "Book 1 conclusion / series hook"},
        ],
        "sort_order": 100,
        "is_featured": False,
        "is_disabled": False,
    },
    # 9. GHOSTWRITTEN BOOK
    {
        "slug": "ghostwritten-book",
        "category": "ghostwritten_book",
        "parent_slug": None,
        "name": "Ghostwritten Book",
        "description": "Capture a client's message, voice, and source material in a structured writing flow.",
        "who_it_is_for": "Ghostwriters managing client projects professionally.",
        "expected_outcome": "A completed manuscript in the client's voice, approved and delivery-ready.",
        "suggested_workflow": "Client intake → Voice capture → Outline approval → Draft → Revision rounds → Delivery.",
        "book_type": "nonfiction",
        "genre": "Ghostwritten",
        "structure_framework": "client_workflow",
        "default_structure": {
            "planning_sections": [
                {"id": "client_profile", "title": "Client Profile", "type": "section"},
                {"id": "voice_notes", "title": "Client Voice Notes", "type": "section"},
                {"id": "source_material", "title": "Source Material Intake", "type": "section"},
                {"id": "interview_notes", "title": "Interview Notes", "type": "section"},
                {"id": "book_objective", "title": "Book Objective", "type": "text"},
                {"id": "chapter_plan", "title": "Chapter Plan", "type": "section"},
                {"id": "tone_guidance", "title": "Tone Guidance", "type": "text"},
                {"id": "approval_workflow", "title": "Approval Workflow", "type": "section"},
                {"id": "revision_rounds", "title": "Revision Rounds", "type": "section"},
                {"id": "delivery", "title": "Delivery Readiness", "type": "section"},
            ]
        },
        "default_milestones": [
            {"id": "intake", "label": "Client intake complete", "type": "planning"},
            {"id": "outline_approved", "label": "Outline approved", "type": "planning"},
            {"id": "draft", "label": "First draft complete", "type": "draft"},
            {"id": "revision1", "label": "Revision round 1", "type": "revision"},
            {"id": "revision2", "label": "Revision round 2", "type": "revision"},
            {"id": "delivery", "label": "Delivery ready", "type": "revision"},
        ],
        "default_planning_prompts": {
            "client_voice": "What are the client's key phrases and tone?",
            "objective": "What is the book's primary objective?",
        },
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {
            "voice": "Help me match this passage to the client's voice.",
        },
        "export_recommendations": ["docx", "pdf"],
        "setup_questions": [
            {"id": "client_name", "prompt": "Client name (for your reference)", "type": "text"},
            {"id": "book_objective", "prompt": "What is the book's primary objective?", "type": "text"},
        ],
        "chapter_skeletons": [
            {"title": "Introduction", "summary": ""},
            {"title": "Chapter 1", "summary": ""},
            {"title": "Chapter 2", "summary": ""},
            {"title": "Chapter 3", "summary": ""},
            {"title": "Chapter 4", "summary": ""},
            {"title": "Chapter 5", "summary": ""},
            {"title": "Chapter 6", "summary": ""},
            {"title": "Chapter 7", "summary": ""},
            {"title": "Chapter 8", "summary": ""},
            {"title": "Conclusion", "summary": ""},
        ],
        "sort_order": 110,
        "is_featured": False,
        "is_disabled": False,
    },
    # 10. CUSTOM / BLANK
    {
        "slug": "custom-blank",
        "category": "custom",
        "parent_slug": None,
        "name": "Custom / Blank Project",
        "description": "Start from scratch with a clean manuscript and build your own structure your way.",
        "who_it_is_for": "Writers who prefer full creative control and no template constraints.",
        "expected_outcome": "A project you shape entirely yourself.",
        "suggested_workflow": "Create → Add structure as you go → Write.",
        "book_type": None,
        "genre": None,
        "structure_framework": "custom",
        "default_structure": {"planning_sections": [{"id": "notes", "title": "Notes", "type": "section"}]},
        "default_milestones": [
            {"id": "started", "label": "Project started", "type": "planning"},
            {"id": "draft", "label": "First draft complete", "type": "draft"},
            {"id": "revision", "label": "Revision complete", "type": "revision"},
        ],
        "default_planning_prompts": {},
        "default_accountability": DEFAULT_ACCOUNTABILITY,
        "ai_prompts": {},
        "export_recommendations": ["docx", "pdf", "epub", "txt"],
        "setup_questions": [
            {"id": "project_name", "prompt": "What will you call this project?", "type": "text"},
        ],
        "chapter_skeletons": [{"title": "Chapter 1", "summary": ""}],
        "sort_order": 120,
        "is_featured": False,
        "is_disabled": False,
    },
]

# Apply premium overrides to flagship launch templates
TEMPLATE_DEFINITIONS = [_apply_premium(d) for d in TEMPLATE_DEFINITIONS_RAW]
