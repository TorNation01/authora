"""Schemas for pushing a book to a publishing house."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from authora.services.imprint import ANEMA_HOUSE_NAME


class SubmissionRequest(BaseModel):
    """What the author fills in for the house. Only the first four are required."""

    publisher_name: str = Field(default=ANEMA_HOUSE_NAME, max_length=255)
    author_name: str = Field(min_length=1, max_length=120)
    email: str = Field(min_length=5, max_length=200)
    title: str = Field(min_length=1, max_length=200)
    series: str = Field(default="", max_length=160)
    genre: str = Field(default="", max_length=80)
    word_count: int | None = Field(default=None, ge=0, le=5_000_000)
    pitch: str = Field(default="", max_length=4000)
    include_cover: bool = True

    @field_validator("email")
    @classmethod
    def _email_shape(cls, value: str) -> str:
        value = value.strip()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("A valid email address is required — the house replies to it.")
        return value


class SubmissionResponse(BaseModel):
    id: UUID
    book_id: UUID
    publisher_name: str
    publisher_url: str | None = None
    ref: str
    status: str
    message: str | None = None
    submitted_at: datetime
    checked_at: datetime | None = None
    files: list[dict[str, Any]] = []
