"""Revision pass schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class RevisionChecklistItemCreate(BaseModel):
    """Create checklist item."""

    title: str = Field(..., min_length=1, max_length=500)
    sort_order: int = 0


class RevisionChecklistItemResponse(BaseModel):
    """Checklist item in API response."""

    id: UUID
    revision_pass_id: UUID
    title: str
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class RevisionPassChapterResponse(BaseModel):
    """Chapter progress for a pass."""

    id: UUID
    chapter_id: UUID
    chapter_title: str
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RevisionPassCreate(BaseModel):
    """Create revision pass."""

    book_id: UUID | None = None
    pass_type: str = Field(
        ...,
        pattern="^(structural|clarity|pacing|emotional_depth|consistency|grammar_polish|custom)$",
    )
    name: str | None = Field(None, max_length=255)


class RevisionPassUpdate(BaseModel):
    """Update revision pass."""

    name: str | None = Field(None, max_length=255)
    sort_order: int | None = None
    completed: bool | None = None


class RevisionPassResponse(BaseModel):
    """Revision pass in API response."""

    id: UUID
    project_id: UUID
    book_id: UUID | None
    pass_type: str
    name: str | None
    sort_order: int
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    chapters_total: int = 0
    chapters_completed: int = 0
    unresolved_comments: int = 0
    checklist_items: list[RevisionChecklistItemResponse] = []

    model_config = {"from_attributes": True}


class RevisionPassSummaryResponse(BaseModel):
    """Summary of revision passes for a project."""

    passes: list[RevisionPassResponse]
    total_unresolved: int
