"""AUTHORA vault schemas: ideas, research, characters, locations, timeline, themes, sources."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


# --- Idea ---

class IdeaCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = ""
    idea_type: str = Field(default="idea_card", max_length=50)
    status: str = Field(default="raw_idea", max_length=50)
    pinned: bool = False
    starred: bool = False
    category: str | None = Field(None, max_length=100)
    tags: list[str] = Field(default_factory=list)
    book_id: UUID | None = None
    chapter_id: UUID | None = None
    character_id: UUID | None = None
    location_id: UUID | None = None
    timeline_event_id: UUID | None = None
    metadata: dict[str, Any] | None = None


class IdeaUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    idea_type: str | None = Field(None, max_length=50)
    status: str | None = Field(None, max_length=50)
    pinned: bool | None = None
    starred: bool | None = None
    category: str | None = Field(None, max_length=100)
    tags: list[str] | None = None
    book_id: UUID | None = None
    chapter_id: UUID | None = None
    character_id: UUID | None = None
    location_id: UUID | None = None
    timeline_event_id: UUID | None = None
    metadata: dict[str, Any] | None = None


class IdeaResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    book_id: UUID | None
    chapter_id: UUID | None
    character_id: UUID | None
    location_id: UUID | None
    timeline_event_id: UUID | None
    title: str
    content: str
    idea_type: str
    status: str
    pinned: bool
    starred: bool
    category: str | None
    tags: list[str]
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Research Entry ---

class ResearchEntryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = ""
    entry_type: str = Field(default="note", max_length=50)
    topic: str | None = Field(None, max_length=255)
    tags: list[str] = Field(default_factory=list)
    needs_verification: bool = False
    parent_id: UUID | None = None
    source_id: UUID | None = None
    link_metadata: dict[str, Any] | None = None


class ResearchEntryUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    entry_type: str | None = Field(None, max_length=50)
    topic: str | None = Field(None, max_length=255)
    tags: list[str] | None = None
    needs_verification: bool | None = None
    parent_id: UUID | None = None
    source_id: UUID | None = None
    link_metadata: dict[str, Any] | None = None


class ResearchEntryResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    parent_id: UUID | None
    source_id: UUID | None
    title: str
    content: str
    entry_type: str
    topic: str | None
    tags: list[str]
    needs_verification: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Vault Character ---

class VaultCharacterCreate(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    aliases: list[str] = Field(default_factory=list)
    role_in_story: str | None = Field(None, max_length=255)
    archetype: str | None = Field(None, max_length=100)
    age: str | None = Field(None, max_length=100)
    appearance_notes: str | None = None
    voice_notes: str | None = None
    personality_traits: str | None = None
    goals: str | None = None
    fears: str | None = None
    motivations: str | None = None
    internal_conflict: str | None = None
    external_conflict: str | None = None
    backstory: str | None = None
    timeline_notes: str | None = None
    secrets: str | None = None
    quirks: str | None = None
    dialogue_patterns: str | None = None
    emotional_arc: str | None = None
    private_notes: str | None = None
    status: str = Field(default="active", max_length=50)
    book_id: UUID | None = None


class VaultCharacterUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    aliases: list[str] | None = None
    role_in_story: str | None = Field(None, max_length=255)
    archetype: str | None = Field(None, max_length=100)
    age: str | None = Field(None, max_length=100)
    appearance_notes: str | None = None
    voice_notes: str | None = None
    personality_traits: str | None = None
    goals: str | None = None
    fears: str | None = None
    motivations: str | None = None
    internal_conflict: str | None = None
    external_conflict: str | None = None
    backstory: str | None = None
    timeline_notes: str | None = None
    secrets: str | None = None
    quirks: str | None = None
    dialogue_patterns: str | None = None
    emotional_arc: str | None = None
    private_notes: str | None = None
    status: str | None = Field(None, max_length=50)
    book_id: UUID | None = None


class VaultCharacterResponse(BaseModel):
    id: UUID
    project_id: UUID
    book_id: UUID | None
    full_name: str
    aliases: list[str]
    role_in_story: str | None
    archetype: str | None
    age: str | None
    appearance_notes: str | None
    voice_notes: str | None
    personality_traits: str | None
    goals: str | None
    fears: str | None
    motivations: str | None
    internal_conflict: str | None
    external_conflict: str | None
    backstory: str | None
    timeline_notes: str | None
    secrets: str | None
    quirks: str | None
    dialogue_patterns: str | None
    emotional_arc: str | None
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Vault Location ---

class VaultLocationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    category: str = Field(default="location", max_length=100)
    description: str | None = None
    rules: str | None = None
    geography: str | None = None
    environment: str | None = None
    atmosphere: str | None = None
    history: str | None = None
    constraints: str | None = None
    book_id: UUID | None = None
    parent_id: UUID | None = None


class VaultLocationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=500)
    category: str | None = Field(None, max_length=100)
    description: str | None = None
    rules: str | None = None
    geography: str | None = None
    environment: str | None = None
    atmosphere: str | None = None
    history: str | None = None
    constraints: str | None = None
    book_id: UUID | None = None
    parent_id: UUID | None = None


class VaultLocationResponse(BaseModel):
    id: UUID
    project_id: UUID
    book_id: UUID | None
    parent_id: UUID | None
    name: str
    category: str
    description: str | None
    rules: str | None
    geography: str | None
    environment: str | None
    atmosphere: str | None
    history: str | None
    constraints: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Timeline Event ---

class TimelineEventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    event_type: str = Field(default="story_event", max_length=50)
    event_date: date | None = None
    date_label: str | None = Field(None, max_length=255)
    sequence_order: int = 0
    storyline: str | None = Field(None, max_length=255)
    time_period: str | None = Field(None, max_length=255)
    book_id: UUID | None = None


class TimelineEventUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    event_type: str | None = Field(None, max_length=50)
    event_date: date | None = None
    date_label: str | None = Field(None, max_length=255)
    sequence_order: int | None = None
    storyline: str | None = Field(None, max_length=255)
    time_period: str | None = Field(None, max_length=255)
    book_id: UUID | None = None


class TimelineEventResponse(BaseModel):
    id: UUID
    project_id: UUID
    book_id: UUID | None
    title: str
    description: str | None
    event_type: str
    event_date: date | None
    date_label: str | None
    sequence_order: int
    storyline: str | None
    time_period: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Vault Relationship ---

class VaultRelationshipCreate(BaseModel):
    character_a_id: UUID
    character_b_id: UUID
    relationship_type: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    status: str | None = Field(None, max_length=100)
    history: str | None = None


class VaultRelationshipUpdate(BaseModel):
    relationship_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    status: str | None = Field(None, max_length=100)
    history: str | None = None


class VaultRelationshipResponse(BaseModel):
    id: UUID
    project_id: UUID
    character_a_id: UUID
    character_b_id: UUID
    relationship_type: str
    description: str | None
    status: str | None
    history: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Theme ---

class ThemeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    theme_type: str = Field(default="theme", max_length=50)
    description: str | None = None
    notes: str | None = None
    is_central: bool = False
    book_id: UUID | None = None


class ThemeUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    theme_type: str | None = Field(None, max_length=50)
    description: str | None = None
    notes: str | None = None
    is_central: bool | None = None
    book_id: UUID | None = None


class ThemeResponse(BaseModel):
    id: UUID
    project_id: UUID
    book_id: UUID | None
    name: str
    theme_type: str
    description: str | None
    notes: str | None
    is_central: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Source ---

class SourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    author: str | None = Field(None, max_length=500)
    source_type: str = Field(default="book", max_length=50)
    publication_date: str | None = Field(None, max_length=100)
    url: str | None = Field(None, max_length=2000)
    usage_notes: str | None = None
    topic_tags: list[str] = Field(default_factory=list)
    quote_extracts: list[str] = Field(default_factory=list)
    citation_notes: str | None = None
    reliability_note: str | None = None
    status: str = Field(default="needs_review", max_length=50)


class SourceUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    author: str | None = Field(None, max_length=500)
    source_type: str | None = Field(None, max_length=50)
    publication_date: str | None = Field(None, max_length=100)
    url: str | None = Field(None, max_length=2000)
    usage_notes: str | None = None
    topic_tags: list[str] | None = None
    quote_extracts: list[str] | None = None
    citation_notes: str | None = None
    reliability_note: str | None = None
    status: str | None = Field(None, max_length=50)
    used_in_manuscript: bool | None = None


class SourceResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    author: str | None
    source_type: str
    publication_date: str | None
    url: str | None
    usage_notes: str | None
    topic_tags: list[str]
    quote_extracts: list[str]
    citation_notes: str | None
    reliability_note: str | None
    status: str
    used_in_manuscript: bool = False
    zotero_item_key: str | None = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Chapter Links ---

class ChapterCharacterLinkCreate(BaseModel):
    character_id: UUID
    notes: str | None = None


class ChapterCharacterLinkResponse(BaseModel):
    id: UUID
    chapter_id: UUID
    character_id: UUID
    notes: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterLocationLinkCreate(BaseModel):
    location_id: UUID
    notes: str | None = None


class ChapterLocationLinkResponse(BaseModel):
    id: UUID
    chapter_id: UUID
    location_id: UUID
    notes: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterEventLinkCreate(BaseModel):
    event_id: UUID
    notes: str | None = None


class ChapterEventLinkResponse(BaseModel):
    id: UUID
    chapter_id: UUID
    event_id: UUID
    notes: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterThemeLinkCreate(BaseModel):
    theme_id: UUID
    notes: str | None = None


class ChapterThemeLinkResponse(BaseModel):
    id: UUID
    chapter_id: UUID
    theme_id: UUID
    notes: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterSourceLinkCreate(BaseModel):
    source_id: UUID
    usage_notes: str | None = None


class ChapterSourceLinkResponse(BaseModel):
    id: UUID
    chapter_id: UUID
    source_id: UUID
    usage_notes: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterResearchLinkCreate(BaseModel):
    research_id: UUID
    notes: str | None = None


class ChapterResearchLinkResponse(BaseModel):
    id: UUID
    chapter_id: UUID
    research_id: UUID
    notes: str | None
    sort_order: int
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Chapter Knowledge Panel ---

class ChapterKnowledgePanel(BaseModel):
    """Aggregated knowledge for a chapter: linked characters, locations, events, themes, sources, research."""

    chapter_id: UUID
    characters: list[VaultCharacterResponse] = Field(default_factory=list)
    locations: list[VaultLocationResponse] = Field(default_factory=list)
    events: list[TimelineEventResponse] = Field(default_factory=list)
    themes: list[ThemeResponse] = Field(default_factory=list)
    sources: list[SourceResponse] = Field(default_factory=list)
    research_entries: list[ResearchEntryResponse] = Field(default_factory=list)
