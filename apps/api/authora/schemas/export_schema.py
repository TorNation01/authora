"""Export and publishing-prep schemas."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# Front matter block kinds
FRONT_MATTER_KINDS = (
    "title_page",
    "subtitle",
    "copyright",
    "dedication",
    "epigraph",
    "preface",
    "introduction",
    "foreword",
    "disclaimer",
    "custom",
)

# Back matter block kinds
BACK_MATTER_KINDS = (
    "acknowledgements",
    "about_author",
    "author_note",
    "resources",
    "next_book",
    "call_to_action",
    "workbook_appendix",
    "references",
    "glossary",
    "bonus_material",
    "custom",
)


class FrontMatterBlock(BaseModel):
    """Single front matter block."""

    kind: str = "custom"
    title: str | None = None
    content: str
    sort_order: int = 0


class BackMatterBlock(BaseModel):
    """Single back matter block."""

    kind: str = "custom"
    title: str | None = None
    content: str
    sort_order: int = 0


class ExportOptions(BaseModel):
    """Options for book export."""

    include_title_page: bool = True
    include_toc: bool = True
    include_acknowledgements: bool = False
    front_matter: str | None = None
    back_matter: str | None = None
    acknowledgements: str | None = None
    dedication: str | None = None
    epigraph: str | None = None
    copyright_notice: str | None = None
    author_bio: str | None = None
    author_name: str | None = None
    subtitle: str | None = None
    pen_name: str | None = None
    format_style: str = Field(default="manuscript", pattern="^(manuscript|print|ebook|workbook)$")
    front_matter_blocks: list[dict[str, Any]] | None = None
    back_matter_blocks: list[dict[str, Any]] | None = None


class ExportPreviewResponse(BaseModel):
    """Preview of export structure."""

    book_title: str
    chapter_count: int
    total_words: int
    chapters: list[dict[str, Any]]
    has_front_matter: bool
    has_back_matter: bool
    has_acknowledgements: bool


class PublishingPrepRequest(BaseModel):
    """Request for publishing-prep AI generation."""

    type: str = Field(..., pattern="^(synopsis|blurb|chapter_summaries|beta_pack|author_bio|handoff_pack)$")
    book_id: UUID
    extra_context: str | None = None
