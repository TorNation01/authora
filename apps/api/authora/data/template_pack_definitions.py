"""Template pack definitions for premium add-ons.

Six premium packs with fully structured templates, guidance, and real usable content.
"""

TEMPLATE_PACK_DEFINITIONS = [
    {
        "slug": "write-your-first-book",
        "name": "Write Your First Book",
        "description": "Everything you need to go from blank page to finished first draft. Beginner fiction and nonfiction templates, step-by-step roadmap, chapter-by-chapter guide, and writing schedule. No overwhelm—just a clear path.",
        "price_cents": 2900,  # $29
        "stripe_price_id": None,
        "template_slugs": [
            "fiction-beginner",
            "nonfiction-beginner",
            "writing-roadmap",
            "chapter-guide",
            "writing-schedule",
        ],
        "sort_order": 1,
    },
    {
        "slug": "fiction-mastery-pack",
        "name": "Fiction Mastery Pack",
        "description": "Professional fiction toolkit: chapter builder, character builder, world building, advanced three-act structure, multi-plot builder, character arc system, pacing optimizer, and conflict escalation. Everything for serious fiction writers.",
        "price_cents": 4900,  # $49
        "stripe_price_id": None,
        "template_slugs": [
            "fiction-chapter-builder",
            "fiction-character-builder",
            "fiction-world-building",
            "fiction-advanced-three-act",
            "fiction-multi-plot",
            "fiction-character-arc",
            "fiction-pacing-optimizer",
            "fiction-conflict-escalation",
        ],
        "sort_order": 2,
    },
    {
        "slug": "nonfiction-authority-pack",
        "name": "Non-Fiction Authority Pack",
        "description": "Establish authority and deliver value. Book blueprint, chapter template, authority book, self-help structure, authority blueprint, personal brand, storytelling + lesson framework, and case study builder. For experts and thought leaders.",
        "price_cents": 4900,  # $49
        "stripe_price_id": None,
        "template_slugs": [
            "nonfiction-book-blueprint",
            "nonfiction-chapter-template",
            "nonfiction-authority-book",
            "nonfiction-self-help-structured",
            "nonfiction-authority-blueprint",
            "nonfiction-personal-brand",
            "nonfiction-storytelling-lesson",
            "nonfiction-case-study-builder",
        ],
        "sort_order": 3,
    },
    {
        "slug": "ai-writing-pack",
        "name": "AI Writing Pack",
        "description": "Maximize AI as your writing partner. Co-author prompts, chapter expansion templates, rewrite + polish workflows, and tone control. Structured prompts and workflows for consistent, high-quality AI collaboration.",
        "price_cents": 2900,  # $29
        "stripe_price_id": None,
        "template_slugs": [
            "ai-co-author-prompts",
            "ai-chapter-expansion",
            "ai-rewrite-polish",
            "ai-tone-control",
        ],
        "sort_order": 4,
    },
    {
        "slug": "finish-your-book-system",
        "name": "Finish Your Book System",
        "description": "Overcome procrastination and complete your manuscript. Completion roadmap, progress system, anti-procrastination templates, and writing accountability flows. Structured check-ins and momentum builders.",
        "price_cents": 2900,  # $29
        "stripe_price_id": None,
        "template_slugs": [
            "completion-roadmap",
            "progress-system",
            "anti-procrastination",
            "writing-accountability-flows",
        ],
        "sort_order": 5,
    },
    {
        "slug": "business-book-builder",
        "name": "Business Book Builder",
        "description": "Turn your book into a business asset. Lead generation book, course conversion book, authority positioning framework, and CTA structures. For coaches, consultants, and course creators.",
        "price_cents": 2900,  # $29
        "stripe_price_id": None,
        "template_slugs": [
            "business-lead-generation-book",
            "business-course-conversion-book",
            "business-authority-positioning",
            "business-cta-structures",
        ],
        "sort_order": 6,
    },
]
