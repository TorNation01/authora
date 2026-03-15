"""Export and publishing-prep schemas."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ExportOptions(BaseModel):
    """Options for book export."""

    include_title_page: bool = True
    include_toc: bool = True
    include_acknowledgements: bool = False
    front_matter: str | None = None  # Dedication, epigraph, etc.
    back_matter: str | None = None  # About the author, etc.
    acknowledgements: str | None = None
    author_name: str | None = None
    format_style: str = Field(default="manuscript", pattern="^(manuscript|print|ebook)$")


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
