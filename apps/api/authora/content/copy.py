"""Built-in copy: onboarding, tooltips, empty states, AI explanations."""

from typing import Any

# --- ONBOARDING COPY ---

ONBOARDING_COPY: dict[str, Any] = {
    "welcome": {
        "title": "Welcome to AUTHORA",
        "subtitle": "Your guided writing journey from idea to finished book",
        "description": "We'll ask a few questions to personalize your experience. You can change these anytime.",
    },
    "book_type": {
        "title": "Fiction or non-fiction?",
        "description": "This helps us suggest the right structure and tools.",
        "fiction_label": "Fiction",
        "fiction_desc": "Novels, stories, creative writing",
        "nonfiction_label": "Non-fiction",
        "nonfiction_desc": "Memoir, how-to, business, academic",
    },
    "writing_mode": {
        "title": "How do you want to write?",
        "description": "Choose the level of AI assistance that feels right.",
        "solo_label": "Write myself",
        "solo_desc": "I write alone, AI assists when I ask",
        "cowrite_label": "Co-write with AI",
        "cowrite_desc": "AI suggests and drafts, I edit and steer",
        "ghostwriter_label": "Ghostwriter mode",
        "ghostwriter_desc": "AI drafts heavily, I guide and refine",
    },
    "writing_goals": {
        "title": "What are your writing goals?",
        "placeholder": "e.g. finish my first draft, publish by next year, build a daily habit",
    },
    "target_timeline": {
        "title": "Target completion",
        "description": "When do you hope to finish? No pressure—you can change this.",
    },
    "writing_schedule": {
        "title": "When do you usually write?",
        "description": "We'll use this for gentle reminders if you want them.",
    },
    "accountability": {
        "title": "Encouragement style",
        "description": "How do you like to be nudged?",
        "gentle_label": "Gentle",
        "gentle_desc": "Soft reminders, no pressure",
        "structured_label": "Structured",
        "structured_desc": "Clear goals and check-ins",
        "buddy_label": "Buddy",
        "buddy_desc": "Community and encouragement",
    },
    "ai_comfort": {
        "title": "How much AI help do you want?",
        "description": "You can change this anytime in settings.",
        "minimal_label": "Minimal",
        "minimal_desc": "Only when I ask",
        "moderate_label": "Moderate",
        "moderate_desc": "Suggestions and prompts",
        "full_label": "Full",
        "full_desc": "AI drafting, rewriting, expansion",
    },
    "genre": {
        "title": "Genre or topic",
        "placeholder": "e.g. romance, thriller, memoir, business",
    },
    "complete": {
        "title": "You're all set",
        "subtitle": "Your journey starts now",
        "description": "Create a project and add your first book. We'll guide you through each step.",
        "cta": "Create your first project",
    },
}

# --- HELP TOOLTIPS ---

HELP_TOOLTIPS: dict[str, str] = {
    "ghostwriter_mode": "Light = AI assists with outlines and suggestions. Heavy = AI drafts chapters from briefs. Full = AI handles most drafting; you guide and refine.",
    "chapter_brief": "A short summary of what happens in this chapter. The AI uses it to generate a draft.",
    "outline": "Your book's structure. Add chapters and summaries. You can reorder anytime.",
    "notes": "Research, ideas, and scratchpad. Link notes to chapters for easy reference while writing.",
    "ai_actions": "Select text and choose an action: rewrite, expand, shorten, change tone, or continue writing.",
    "version_history": "See previous versions of this chapter. Restore any version if you want to go back.",
    "export": "Export your manuscript as DOCX, PDF, EPUB, or plain text. Choose format and options.",
    "accountability_goals": "Set daily or weekly word goals. We'll nudge you gently (or firmly) based on your preference.",
    "gamification": "Earn XP, badges, and streaks as you write. Optional—turn off in settings if you prefer a quiet workspace.",
    "writing_plan": "Set a target finish date and we'll help you break it into milestones and chapter targets.",
    "reference_panel": "Look up definitions, synonyms, and get readability analysis. Select text to analyze.",
    "autosave": "Your work saves automatically as you type. No need to hit save.",
    "distraction_free": "Hide the sidebar and panels for a clean, focused writing view.",
    "publishing_prep": "Generate synopsis, blurb, and other materials for querying agents or self-publishing.",
}

# --- EMPTY STATE COPY ---

EMPTY_STATE_COPY: dict[str, dict[str, str]] = {
    "no_projects": {
        "title": "No projects yet",
        "description": "Create a project to organize your books. A project can hold one book or a series.",
        "action": "Create project",
    },
    "no_books": {
        "title": "No books yet",
        "description": "Add your first book to this project. Choose a template or start from scratch.",
        "action": "Add book",
    },
    "no_chapters": {
        "title": "No chapters yet",
        "description": "Add your first chapter to start writing. You can reorder and add more anytime.",
        "action": "Add chapter",
    },
    "no_notes": {
        "title": "No notes yet",
        "description": "Capture ideas, research, and quotes. Link notes to chapters for easy reference.",
        "action": "Add note",
    },
    "no_highlights": {
        "title": "No highlights",
        "description": "Select text to highlight. Highlights help you track important passages.",
    },
    "no_versions": {
        "title": "No version history",
        "description": "Versions are saved as you write. Edit this chapter to build history.",
    },
    "no_achievements": {
        "title": "No achievements yet",
        "description": "Write consistently to earn badges and XP. Your first achievement is just a few words away.",
    },
    "no_goals": {
        "title": "No goals set",
        "description": "Set a daily or weekly word goal to stay on track. We'll nudge you when you want.",
        "action": "Set goal",
    },
    "no_exports": {
        "title": "No exports yet",
        "description": "Export your manuscript when you're ready. We support DOCX, PDF, EPUB, and more.",
        "action": "Export",
    },
    "empty_chapter": {
        "title": "Start writing",
        "description": "This chapter is empty. Type here or use AI to generate a draft from your outline.",
    },
    "empty_editor": {
        "title": "Your manuscript",
        "description": "Select a chapter from the sidebar to start writing. Or add a new chapter.",
    },
}

# --- FRAMEWORK & FINISH MODE COPY ---

FRAMEWORK_EDITOR_COPY: dict[str, str] = {
    "current_framework_stage": "Current framework stage",
    "you_are_here": "You are here",
    "next_suggested_step": "Next suggested step",
    "missing_key_section": "Missing key section",
    "on_track": "On track",
    "needs_attention": "Needs attention",
    "keep_moving": "Keep moving",
    "finish_this_stage": "Finish this stage",
}

FINISH_MODE_COPY: list[str] = [
    "You do not need perfect. You need progress.",
    "Complete this stage, then move forward.",
    "One finished section beats ten unfinished ideas.",
    "Momentum creates books.",
]

# --- AI EXPLANATION COPY ---

AI_EXPLANATION_COPY: dict[str, str] = {
    "ai_overview": "AUTHORA's AI helps you write faster without replacing your voice. It can suggest, expand, rewrite, or draft—you stay in control.",
    "ai_rewrite": "Rewrites your selected text in a different style. Use it to try a new tone or simplify complex sentences.",
    "ai_expand": "Adds detail and depth to your selection. Good for scenes that feel thin or passages that need more development.",
    "ai_shorten": "Condenses your text while keeping the meaning. Useful for tight prose or cutting word count.",
    "ai_improve": "Improves clarity and flow. Fixes awkward phrasing and strengthens weak sentences.",
    "ai_fix_grammar": "Corrects grammar, punctuation, and common errors. Does not change your voice or meaning.",
    "ai_suggest": "Suggests alternative phrasings. Pick one, edit it, or ignore—your choice.",
    "ai_continue": "Continues writing from your cursor or selection. Use it when you're stuck on the next sentence.",
    "ai_ghostwriter": "Generates a full chapter draft from your outline and brief. You can edit, approve, or reject. Your story, AI-assisted.",
    "ai_api_key": "Add your own API key to use AI features. Without a key, some actions may be limited. Keys are stored securely and never shared.",
    "ai_privacy": "Your text is sent to the AI provider only when you trigger an action. We do not train models on your content.",
}
