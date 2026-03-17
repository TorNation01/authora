"""Book and chapter schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChapterCreate(BaseModel):
    """Create chapter."""

    title: str = Field(..., min_length=1, max_length=500)
    sort_order: int = 0
    content: dict[str, Any] = Field(default_factory=dict)


class ChapterUpdate(BaseModel):
    """Update chapter. Use if_unchanged_since for conflict detection (returns 409 if changed)."""

    title: str | None = Field(None, min_length=1, max_length=500)
    sort_order: int | None = None
    content: dict[str, Any] | None = None
    section_status: str | None = Field(None, pattern="^(draft|revising|review|done)$")
    section_group: str | None = Field(None, max_length=255)
    tags: list[str] | None = None
    content_source: str | None = Field(None, pattern="^(user_written|ai_assisted|ai_generated)$")
    if_unchanged_since: datetime | None = Field(None, description="Conflict check: ISO datetime of last known update")


class ChaptersReorder(BaseModel):
    """Reorder chapters by id list."""

    chapter_ids: list[UUID] = Field(..., min_length=1)


class ChapterVersionResponse(BaseModel):
    """Chapter version in API response."""

    id: UUID
    chapter_id: UUID
    content: dict[str, Any]
    word_count: int
    content_source: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterResponse(BaseModel):
    """Chapter in API response."""

    id: UUID
    book_id: UUID
    title: str
    sort_order: int
    content: dict[str, Any]
    word_count: int
    section_status: str | None = None
    section_group: str | None = None
    tags: list[str] = Field(default_factory=list)
    content_source: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("tags", mode="before")
    @classmethod
    def coerce_tags(cls, v: Any) -> list[str]:
        return v if isinstance(v, list) else []


class BookCreate(BaseModel):
    """Create book."""

    title: str = Field(..., min_length=1, max_length=500)
    genre: str | None = None
    type: str = Field(default="fiction", pattern="^(fiction|nonfiction)$")
    planner_data: dict[str, Any] | None = None


class BookUpdate(BaseModel):
    """Update book."""

    title: str | None = Field(None, min_length=1, max_length=500)
    genre: str | None = None
    type: str | None = Field(None, pattern="^(fiction|nonfiction)$")
    framework_id: UUID | None = None
    planner_data: dict[str, Any] | None = None


class BookResponse(BaseModel):
    """Book in API response."""

    id: UUID
    project_id: UUID
    title: str
    genre: str | None
    type: str
    framework_id: UUID | None = None
    planner_data: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BookWithChaptersResponse(BookResponse):
    """Book with chapters."""

    chapters: list[ChapterResponse] = []
