"""Note schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


NOTE_TYPES = ("idea", "scratchpad", "research", "quote", "general")


class NoteAttachmentResponse(BaseModel):
    """Attachment in API response."""

    id: UUID
    file_key: str
    filename: str
    content_type: str | None
    file_size: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class NoteCreate(BaseModel):
    """Create note."""

    title: str = Field(..., min_length=1, max_length=500)
    content: str = ""
    note_type: str = Field(default="general", pattern="^(idea|scratchpad|research|quote|general)$")
    book_id: UUID | None = None
    chapter_id: UUID | None = None
    source: str | None = Field(None, max_length=500)
    source_url: str | None = Field(None, max_length=1000)
    pinned: bool = False
    is_inspiration: bool = False
    category: str | None = Field(None, max_length=100)
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    """Update note."""

    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    note_type: str | None = Field(None, pattern="^(idea|scratchpad|research|quote|general)$")
    book_id: UUID | None = None
    chapter_id: UUID | None = None
    source: str | None = Field(None, max_length=500)
    source_url: str | None = Field(None, max_length=1000)
    pinned: bool | None = None
    is_inspiration: bool | None = None
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None


class NoteResponse(BaseModel):
    """Note in API response."""

    id: UUID
    project_id: UUID
    book_id: UUID | None
    chapter_id: UUID | None
    user_id: UUID
    title: str
    content: str
    note_type: str
    source: str | None
    source_url: str | None
    pinned: bool
    is_inspiration: bool
    category: str | None
    tags: list[str]
    sort_order: int
    created_at: datetime
    updated_at: datetime
    attachments: list[NoteAttachmentResponse] = []

    model_config = {"from_attributes": True}


class NoteLinkChapter(BaseModel):
    """Link note to chapter (drag into chapter)."""

    chapter_id: UUID | None = None
