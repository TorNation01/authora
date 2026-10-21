"""Fiction workspace models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book
    from authora.models.chapter import Chapter


class FictionWorkspace(Base):
    """Fiction workspace config - premise, genre, tone, pacing. One per book."""

    __tablename__ = "fiction_workspaces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, unique=True)

    premise: Mapped[str | None] = mapped_column(Text, nullable=True)
    logline: Mapped[str | None] = mapped_column(Text, nullable=True)  # one-sentence pitch
    genre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subgenre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    audience: Mapped[str | None] = mapped_column(String(255), nullable=True)  # who it is for
    pov: Mapped[str | None] = mapped_column(String(100), nullable=True)  # first / third limited / omniscient
    tense: Mapped[str | None] = mapped_column(String(50), nullable=True)  # past / present
    target_word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    comparable_titles: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)  # ["Book A", "Book B"]
    central_question: Mapped[str | None] = mapped_column(Text, nullable=True)  # dramatic question
    genre_tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)  # genre blend
    tone: Mapped[str | None] = mapped_column(String(255), nullable=True)  # dark, hopeful, humorous, etc.
    themes: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)  # ["identity", "redemption"]
    pacing_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    protagonist_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fiction_characters.id", ondelete="SET NULL"), nullable=True)
    antagonist_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fiction_characters.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FictionCharacter(Base):
    """Character in a fiction book."""

    __tablename__ = "fiction_characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="supporting")  # protagonist, antagonist, love_interest, mentor, foil, minor, supporting
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # one-line description
    age: Mapped[str | None] = mapped_column(String(100), nullable=True)
    appearance: Mapped[str | None] = mapped_column(Text, nullable=True)
    voice: Mapped[str | None] = mapped_column(Text, nullable=True)  # speech pattern, vocabulary, tells
    backstory: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)  # want: external goal
    need: Mapped[str | None] = mapped_column(Text, nullable=True)  # need: internal, often unadmitted
    wound: Mapped[str | None] = mapped_column(Text, nullable=True)  # the injury that explains the flaw
    flaws: Mapped[str | None] = mapped_column(Text, nullable=True)
    secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    arc_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_appearance: Mapped[str | None] = mapped_column(String(255), nullable=True)  # chapter / scene
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")  # active, background, cut
    traits: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)  # voice, appearance, etc.
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CharacterRelationship(Base):
    """Relationship between two characters."""

    __tablename__ = "character_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    character_a_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiction_characters.id", ondelete="CASCADE"), nullable=False)
    character_b_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiction_characters.id", ondelete="CASCADE"), nullable=False)

    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)  # ally, rival, parent, sibling, mentor, lover, enemy, colleague
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # one-line note: what binds them
    arc_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    intensity: Mapped[int] = mapped_column(Integer, nullable=False, default=3)  # 1 (faint) - 5 (defining)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class WorldElement(Base):
    """Worldbuilding element - location, culture, magic system, etc."""

    __tablename__ = "world_elements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # location, culture, magic, technology, etc.
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PlotArc(Base):
    """Plot arc or beat structure."""

    __tablename__ = "plot_arcs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    structure: Mapped[str] = mapped_column(String(100), nullable=False, default="three_act")  # three_act, hero_journey, etc.
    character_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fiction_characters.id", ondelete="SET NULL"), nullable=True)
    beats: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)  # [{label, change, chapter, emotional_turn}]
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Scene(Base):
    """Scene card - links to chapter, has summary, conflict, POV."""

    __tablename__ = "fiction_scenes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    pov_character_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fiction_characters.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    beat: Mapped[str | None] = mapped_column(String(255), nullable=True)  # inciting incident, midpoint, etc.
    conflict_level: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1-5
    escalation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FictionTracker(Base):
    """Continuity notes, foreshadowing, unresolved threads."""

    __tablename__ = "fiction_trackers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)

    type: Mapped[str] = mapped_column(String(50), nullable=False)  # continuity, foreshadowing, unresolved
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending, resolved
    target_chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FictionChapterPlan(Base):
    """Chapter-level planning - summary, goals, conflicts."""

    __tablename__ = "fiction_chapter_plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    conflicts: Mapped[str | None] = mapped_column(Text, nullable=True)
    scene_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)  # list of scene UUIDs
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
