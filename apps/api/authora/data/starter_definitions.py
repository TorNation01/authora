"""Starter template definitions for AUTHORA quick-start.

Maps starter IDs to backend template slugs. Full metadata lives in frontend
starter-templates.ts. This module provides slug resolution for the API.
"""

STARTER_SLUGS = [
    "fiction",
    "fiction-romance",
    "fiction-fantasy",
    "fiction-thriller",
    "fiction-literary",
    "memoir",
    "nonfiction-personal-story",
    "nonfiction-business",
    "nonfiction-howto",
    "nonfiction-selfhelp",
    "workbook",
    "journal",
    "ghostwritten-book",
    # custom-blank has no template
]


def get_starter_metadata() -> list[dict]:
    """Return starter metadata for API. Frontend has full copy; this provides slug->id resolution."""
    return [
        {"id": "fiction-novel", "template_slug": "fiction"},
        {"id": "romance-novel", "template_slug": "fiction-romance"},
        {"id": "fantasy-speculative", "template_slug": "fiction-fantasy"},
        {"id": "thriller-mystery", "template_slug": "fiction-thriller"},
        {"id": "literary-fiction", "template_slug": "fiction-literary"},
        {"id": "memoir", "template_slug": "memoir"},
        {"id": "personal-story", "template_slug": "nonfiction-personal-story"},
        {"id": "business-authority", "template_slug": "nonfiction-business"},
        {"id": "how-to-nonfiction", "template_slug": "nonfiction-howto"},
        {"id": "self-help", "template_slug": "nonfiction-selfhelp"},
        {"id": "workbook", "template_slug": "workbook"},
        {"id": "guided-journal", "template_slug": "journal"},
        {"id": "ghostwritten", "template_slug": "ghostwritten-book"},
        {"id": "blank", "template_slug": None},
    ]
