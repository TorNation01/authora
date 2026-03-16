"""AUTHORA research vault, idea capture, character bible, worldbuilding, timeline, themes, and source manager."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book, Chapter
    from authora.models.project import Project
    from authora.models.user import User


# --- Idea Capture ---

IDEA_TYPES = (
    "quick_note",
    "idea_card",
    "scene_idea",
    "chapter_idea",
    "title_idea",
    "plot_twist",
    "dialogue_snippet",
    "thematic_note",
    "save_for_later",
)

IDEA_STATUSES = ("raw_idea", "maybe_later", "planned", "used", "archived")


class Idea(Base):
    """Idea capture: quick notes, scene ideas, plot twists, dialogue snippets, etc."""

    __tablename__ = "vault_ideas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    character_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_characters.id", ondelete="SET NULL"), nullable=True)
    location_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_locations.id", ondelete="SET NULL"), nullable=True)
    timeline_event_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_timeline_events.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    idea_type: Mapped[str] = mapped_column(String(50), nullable=False, default="idea_card")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="raw_idea")
    pinned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    starred: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)  # voice_note, attachment refs
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="ideas")
    character: Mapped["VaultCharacter | None"] = relationship("VaultCharacter", back_populates="ideas", foreign_keys=[character_id])
    location: Mapped["VaultLocation | None"] = relationship("VaultLocation", back_populates="ideas", foreign_keys=[location_id])
    timeline_event: Mapped["TimelineEvent | None"] = relationship("TimelineEvent", back_populates="ideas", foreign_keys=[timeline_event_id])


# --- Research Vault ---

RESEARCH_ENTRY_TYPES = ("note", "clipped_snippet", "summary", "document", "topic_folder", "fact_check")


class ResearchEntry(Base):
    """Research vault entry: notes, clipped snippets, summaries, topic folders."""

    __tablename__ = "vault_research_entries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_research_entries.id", ondelete="CASCADE"), nullable=True)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_sources.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    entry_type: Mapped[str] = mapped_column(String(50), nullable=False, default="note")
    topic: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    needs_verification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    link_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="research_entries")
    parent: Mapped["ResearchEntry | None"] = relationship("ResearchEntry", remote_side=[id], back_populates="children")
    children: Mapped[list["ResearchEntry"]] = relationship("ResearchEntry", back_populates="parent", cascade="all, delete-orphan")
    source: Mapped["Source | None"] = relationship("Source", back_populates="research_entries")
    chapter_links: Mapped[list["ChapterResearchLink"]] = relationship(
        "ChapterResearchLink", back_populates="research_entry", cascade="all, delete-orphan"
    )


# --- Character Bible ---

CHARACTER_STATUSES = ("active", "background", "archived")


class VaultCharacter(Base):
    """Character bible: profiles for fiction and memoir-style people mapping."""

    __tablename__ = "vault_characters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    role_in_story: Mapped[str | None] = mapped_column(String(255), nullable=True)
    archetype: Mapped[str | None] = mapped_column(String(100), nullable=True)
    age: Mapped[str | None] = mapped_column(String(100), nullable=True)
    appearance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    voice_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    personality_traits: Mapped[str | None] = mapped_column(Text, nullable=True)
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    fears: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivations: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_conflict: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_conflict: Mapped[str | None] = mapped_column(Text, nullable=True)
    backstory: Mapped[str | None] = mapped_column(Text, nullable=True)
    timeline_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    secrets: Mapped[str | None] = mapped_column(Text, nullable=True)
    quirks: Mapped[str | None] = mapped_column(Text, nullable=True)
    dialogue_patterns: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotional_arc: Mapped[str | None] = mapped_column(Text, nullable=True)
    private_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="vault_characters")
    ideas: Mapped[list["Idea"]] = relationship("Idea", back_populates="character", foreign_keys="Idea.character_id")
    chapter_links: Mapped[list["ChapterCharacterLink"]] = relationship(
        "ChapterCharacterLink", back_populates="character", cascade="all, delete-orphan"
    )


# --- Worldbuilding / Setting ---

LOCATION_CATEGORIES = (
    "world",
    "location",
    "organisation",
    "faction",
    "culture",
    "rule_system",
    "technology",
    "magic",
    "geography",
    "environment",
    "glossary",
    "terminology",
    "domain",
    "framework",
    "method",
    "concept",
)


class VaultLocation(Base):
    """Worldbuilding / setting / location / organisation / concept map."""

    __tablename__ = "vault_locations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_locations.id", ondelete="CASCADE"), nullable=True)

    name: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="location")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    geography: Mapped[str | None] = mapped_column(Text, nullable=True)
    environment: Mapped[str | None] = mapped_column(Text, nullable=True)
    atmosphere: Mapped[str | None] = mapped_column(Text, nullable=True)
    history: Mapped[str | None] = mapped_column(Text, nullable=True)
    constraints: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="vault_locations")
    parent: Mapped["VaultLocation | None"] = relationship("VaultLocation", remote_side=[id], back_populates="children")
    children: Mapped[list["VaultLocation"]] = relationship("VaultLocation", back_populates="parent", cascade="all, delete-orphan")
    ideas: Mapped[list["Idea"]] = relationship("Idea", back_populates="location", foreign_keys="Idea.location_id")
    chapter_links: Mapped[list["ChapterLocationLink"]] = relationship(
        "ChapterLocationLink", back_populates="location", cascade="all, delete-orphan"
    )


# --- Timeline / Event Tracker ---

EVENT_TYPES = (
    "story_event",
    "chapter_event",
    "backstory",
    "life_event",
    "memoir_stage",
    "historical_reference",
)


class TimelineEvent(Base):
    """Timeline event: story chronology, backstory, memoir life-stage, etc."""

    __tablename__ = "vault_timeline_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, default="story_event")
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    date_label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    storyline: Mapped[str | None] = mapped_column(String(255), nullable=True)
    time_period: Mapped[str | None] = mapped_column(String(255), nullable=True)
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="timeline_events")
    ideas: Mapped[list["Idea"]] = relationship("Idea", back_populates="timeline_event", foreign_keys="Idea.timeline_event_id")
    chapter_links: Mapped[list["ChapterEventLink"]] = relationship(
        "ChapterEventLink", back_populates="event", cascade="all, delete-orphan"
    )


# --- Relationship Mapping ---

RELATIONSHIP_TYPES = (
    "family",
    "romantic",
    "rivalry",
    "alliance",
    "mentor_student",
    "business",
    "professional",
    "friendship",
    "other",
)


class VaultRelationship(Base):
    """Character-to-character relationship (or people map for non-fiction)."""

    __tablename__ = "vault_relationships"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    character_a_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_characters.id", ondelete="CASCADE"), nullable=False)
    character_b_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_characters.id", ondelete="CASCADE"), nullable=False)

    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str | None] = mapped_column(String(100), nullable=True)
    history: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="vault_relationships")
    character_a: Mapped["VaultCharacter"] = relationship("VaultCharacter", foreign_keys=[character_a_id])
    character_b: Mapped["VaultCharacter"] = relationship("VaultCharacter", foreign_keys=[character_b_id])


# --- Themes / Motifs / Symbols ---

THEME_TYPES = ("theme", "motif", "symbol", "emotional_thread", "recurring_idea")


class Theme(Base):
    """Theme, motif, symbol, or emotional thread tracker."""

    __tablename__ = "vault_themes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    theme_type: Mapped[str] = mapped_column(String(50), nullable=False, default="theme")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_central: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="vault_themes")
    chapter_links: Mapped[list["ChapterThemeLink"]] = relationship(
        "ChapterThemeLink", back_populates="theme", cascade="all, delete-orphan"
    )


# --- Source / Reference Manager ---

SOURCE_TYPES = ("book", "article", "website", "interview", "document", "video", "podcast", "other")
SOURCE_STATUSES = ("verified", "unverified", "needs_review")


class Source(Base):
    """Source / reference for non-fiction, memoir, research-heavy fiction, ghostwriting."""

    __tablename__ = "vault_sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, default="book")
    publication_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    link_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    usage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    topic_tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    quote_extracts: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    citation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reliability_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="needs_review")
    extra: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="vault_sources")
    research_entries: Mapped[list["ResearchEntry"]] = relationship("ResearchEntry", back_populates="source")
    chapter_links: Mapped[list["ChapterSourceLink"]] = relationship(
        "ChapterSourceLink", back_populates="source", cascade="all, delete-orphan"
    )


# --- Chapter Link Tables ---


class ChapterCharacterLink(Base):
    """Link chapter to character (for knowledge panel)."""

    __tablename__ = "chapter_character_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    character_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_characters.id", ondelete="CASCADE"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="character_links")
    character: Mapped["VaultCharacter"] = relationship("VaultCharacter", back_populates="chapter_links")


class ChapterLocationLink(Base):
    """Link chapter to location/setting."""

    __tablename__ = "chapter_location_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    location_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_locations.id", ondelete="CASCADE"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="location_links")
    location: Mapped["VaultLocation"] = relationship("VaultLocation", back_populates="chapter_links")


class ChapterEventLink(Base):
    """Link chapter to timeline event."""

    __tablename__ = "chapter_event_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_timeline_events.id", ondelete="CASCADE"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="event_links")
    event: Mapped["TimelineEvent"] = relationship("TimelineEvent", back_populates="chapter_links")


class ChapterThemeLink(Base):
    """Link chapter to theme/motif."""

    __tablename__ = "chapter_theme_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    theme_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_themes.id", ondelete="CASCADE"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="theme_links")
    theme: Mapped["Theme"] = relationship("Theme", back_populates="chapter_links")


class ChapterSourceLink(Base):
    """Link chapter to source (used-in-chapter marker)."""

    __tablename__ = "chapter_source_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_sources.id", ondelete="CASCADE"), nullable=False)
    usage_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ChapterResearchLink(Base):
    """Link chapter to research entry."""

    __tablename__ = "chapter_research_links"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    research_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_research_entries.id", ondelete="CASCADE"), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="research_links")
    research_entry: Mapped["ResearchEntry"] = relationship("ResearchEntry", back_populates="chapter_links")
