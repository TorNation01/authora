"""Book Bible, character library and act models.

These are additive tables. Nothing here alters the existing fiction_* tables or
the books/chapters schema beyond one nullable chapters.act_id column.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class BookBible(Base):
    """One structured bible per book - the 15-section document."""

    __tablename__ = "book_bibles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # {"story_foundation": {"premise": "...", ...}, ...}
    sections: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    # {"story_foundation": "working" | "locked" | "undecided"}
    section_status: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Character(Base):
    """Project-level character library entry.

    A character lives with the project (the series), not with a single book, so
    the same person can be pulled into book two and edited without duplication.
    `continuation_of` links a later-book version back to its canonical entry.
    """

    __tablename__ = "characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    origin_book_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="SET NULL"), nullable=True
    )
    continuation_of: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="SET NULL"), nullable=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    aliases: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="supporting")
    archetype: Mapped[str | None] = mapped_column(String(120), nullable=True)
    one_line: Mapped[str | None] = mapped_column(Text, nullable=True)

    age: Mapped[str | None] = mapped_column(String(80), nullable=True)
    pronouns: Mapped[str | None] = mapped_column(String(40), nullable=True)
    gender: Mapped[str | None] = mapped_column(String(60), nullable=True)
    profession: Mapped[str | None] = mapped_column(String(200), nullable=True)
    appearance: Mapped[str | None] = mapped_column(Text, nullable=True)
    voice: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality: Mapped[str | None] = mapped_column(Text, nullable=True)

    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    fears: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivations: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_conflict: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_conflict: Mapped[str | None] = mapped_column(Text, nullable=True)

    backstory: Mapped[str | None] = mapped_column(Text, nullable=True)
    wound: Mapped[str | None] = mapped_column(Text, nullable=True)
    secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    arc_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    quirks: Mapped[str | None] = mapped_column(Text, nullable=True)
    need: Mapped[str | None] = mapped_column(Text, nullable=True)
    flaws: Mapped[str | None] = mapped_column(Text, nullable=True)
    skills_limitations: Mapped[str | None] = mapped_column(Text, nullable=True)
    values_boundaries: Mapped[str | None] = mapped_column(Text, nullable=True)
    distinctive_behaviour: Mapped[str | None] = mapped_column(Text, nullable=True)
    portrait_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    portrait_source: Mapped[str | None] = mapped_column(String(20), nullable=True)
    portrait_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dialogue_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    relationships_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    private_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    canon_status: Mapped[str] = mapped_column(String(20), nullable=False, default="working")  # working|locked|undecided
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")  # active|retired
    extras: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class CharacterBond(Base):
    """How one character sees another, in one book - deliberately one-way.

    Distinct from the older fiction_* `character_relationships` table, which is
    two-way and keyed to per-book fiction_characters.
    """

    __tablename__ = "character_bonds"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    from_character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    to_character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    from_chapter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Act(Base):
    """An act in a book. Unlimited, ordered by the author."""

    __tablename__ = "acts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    target_words: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class BookCharacter(Base):
    """Links a library character to a book, so one person can appear in many books."""

    __tablename__ = "book_characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role_in_book: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SeriesBible(Base):
    """One structured bible per project - the canon that sits above any single book."""

    __tablename__ = "series_bibles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    sections: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    section_status: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
