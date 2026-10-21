"""Schemas for publishing metadata, covers, readiness and release records."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from authora.services.imprint import ANEMA_HOUSE_NAME
from authora.services.publishing import normalise_isbn


class PublicationUpdate(BaseModel):
    """Editable publishing metadata. All fields optional; omitted fields are left alone."""

    title: str | None = Field(None, max_length=500)
    subtitle: str | None = Field(None, max_length=500)
    author_name: str | None = Field(None, max_length=255)
    blurb: str | None = None
    short_description: str | None = Field(None, max_length=1000)
    keywords: list[str] | None = None
    categories: list[str] | None = None
    language: str | None = Field(None, max_length=10)
    isbn: str | None = Field(None, max_length=20)
    publication_date: date | None = None
    imprint: str | None = Field(None, max_length=255)
    copyright_notice: str | None = None
    dedication: str | None = None
    front_matter: str | None = None
    acknowledgements: str | None = None
    author_bio: str | None = None
    back_matter: str | None = None
    include_imprint_page: bool | None = None

    @field_validator("isbn")
    @classmethod
    def _validate_isbn(cls, value: str | None) -> str | None:
        normalised, error = normalise_isbn(value)
        if error:
            raise ValueError(error)
        return normalised

    @field_validator("keywords", "categories")
    @classmethod
    def _clean_list(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        cleaned = []
        for item in value:
            text = (item or "").strip()
            if text and text not in cleaned:
                cleaned.append(text)
        return cleaned

    @field_validator("imprint")
    @classmethod
    def _default_imprint(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or ANEMA_HOUSE_NAME


class ReleaseRequest(BaseModel):
    """Record a release. Formats are what the author produced, not what a retailer received."""

    formats: list[Literal["epub", "pdf", "docx", "txt"]] = Field(default_factory=list)
    imprint: str | None = Field(None, max_length=255)
    isbn: str | None = Field(None, max_length=20)
    released_at: datetime | None = None

    @field_validator("formats")
    @classmethod
    def _dedupe_formats(cls, value: list[str]) -> list[str]:
        seen: list[str] = []
        for fmt in value:
            if fmt not in seen:
                seen.append(fmt)
        return seen

    @field_validator("isbn")
    @classmethod
    def _validate_isbn(cls, value: str | None) -> str | None:
        normalised, error = normalise_isbn(value)
        if error:
            raise ValueError(error)
        return normalised


class CoverInfo(BaseModel):
    id: UUID
    content_type: str | None = None
    width: int | None = None
    height: int | None = None
    size_bytes: int | None = None
    uploaded_at: datetime | None = None
    url: str


class ReleaseRecord(BaseModel):
    released_at: datetime
    formats: list[str] = Field(default_factory=list)
    imprint: str | None = None
    isbn: str | None = None


class PublicationResponse(BaseModel):
    """Publication metadata plus cover, release record and the required cover specs."""

    book_id: UUID
    book_title: str
    book_type: str
    exists: bool = False
    title: str | None = None
    subtitle: str | None = None
    author_name: str | None = None
    blurb: str | None = None
    short_description: str | None = None
    keywords: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    language: str = "en"
    isbn: str | None = None
    publication_date: date | None = None
    imprint: str = ANEMA_HOUSE_NAME
    copyright_notice: str | None = None
    dedication: str | None = None
    front_matter: str | None = None
    acknowledgements: str | None = None
    author_bio: str | None = None
    back_matter: str | None = None
    include_imprint_page: bool = True
    status: str = "draft"
    release: ReleaseRecord | None = None
    cover: CoverInfo | None = None
    cover_specs: dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime | None = None
