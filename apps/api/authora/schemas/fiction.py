"""Fiction workspace schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class FictionWorkspaceCreate(BaseModel):
    premise: str | None = None
    genre: str | None = None
    tone: str | None = None
    themes: list[str] | None = None
    pacing_notes: str | None = None


class FictionWorkspaceUpdate(BaseModel):
    premise: str | None = None
    genre: str | None = None
    tone: str | None = None
    themes: list[str] | None = None
    pacing_notes: str | None = None
    protagonist_id: UUID | None = None
    antagonist_id: UUID | None = None


class FictionWorkspaceResponse(BaseModel):
    id: UUID
    book_id: UUID
    premise: str | None
    genre: str | None
    tone: str | None
    themes: list[str] | None
    pacing_notes: str | None
    protagonist_id: UUID | None
    antagonist_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FictionCharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: str = Field(default="supporting", pattern="^(protagonist|antagonist|supporting)$")
    description: str | None = None
    backstory: str | None = None
    goals: str | None = None
    flaws: str | None = None
    traits: dict[str, Any] | None = None


class FictionCharacterUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    role: str | None = Field(None, pattern="^(protagonist|antagonist|supporting)$")
    description: str | None = None
    backstory: str | None = None
    goals: str | None = None
    flaws: str | None = None
    traits: dict[str, Any] | None = None


class FictionCharacterResponse(BaseModel):
    id: UUID
    book_id: UUID
    name: str
    role: str
    description: str | None
    backstory: str | None
    goals: str | None
    flaws: str | None
    traits: dict[str, Any] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CharacterRelationshipCreate(BaseModel):
    character_a_id: UUID
    character_b_id: UUID
    relationship_type: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    arc_notes: str | None = None


class CharacterRelationshipUpdate(BaseModel):
    relationship_type: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    arc_notes: str | None = None


class CharacterRelationshipResponse(BaseModel):
    id: UUID
    book_id: UUID
    character_a_id: UUID
    character_b_id: UUID
    relationship_type: str
    description: str | None
    arc_notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorldElementCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    details: dict[str, Any] | None = None


class WorldElementUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    details: dict[str, Any] | None = None


class WorldElementResponse(BaseModel):
    id: UUID
    book_id: UUID
    name: str
    category: str
    description: str | None
    details: dict[str, Any] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlotArcCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    structure: str = Field(default="three_act", max_length=100)
    beats: list[dict[str, Any]] | None = None


class PlotArcUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    structure: str | None = Field(None, max_length=100)
    beats: list[dict[str, Any]] | None = None


class PlotArcResponse(BaseModel):
    id: UUID
    book_id: UUID
    name: str
    structure: str
    beats: list[dict[str, Any]] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SceneCreate(BaseModel):
    chapter_id: UUID | None = None
    pov_character_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    summary: str | None = None
    beat: str | None = None
    conflict_level: int | None = Field(None, ge=1, le=5)
    escalation_notes: str | None = None


class SceneUpdate(BaseModel):
    chapter_id: UUID | None = None
    pov_character_id: UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    summary: str | None = None
    beat: str | None = None
    conflict_level: int | None = Field(None, ge=1, le=5)
    escalation_notes: str | None = None
    sort_order: int | None = None


class SceneResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    pov_character_id: UUID | None
    title: str
    summary: str | None
    beat: str | None
    conflict_level: int | None
    escalation_notes: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FictionTrackerCreate(BaseModel):
    chapter_id: UUID | None = None
    type: str = Field(..., pattern="^(continuity|foreshadowing|unresolved)$")
    title: str = Field(..., min_length=1, max_length=500)
    content: str | None = None
    target_chapter_id: UUID | None = None


class FictionTrackerUpdate(BaseModel):
    chapter_id: UUID | None = None
    type: str | None = Field(None, pattern="^(continuity|foreshadowing|unresolved)$")
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    status: str | None = Field(None, pattern="^(pending|resolved)$")
    target_chapter_id: UUID | None = None


class FictionTrackerResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    type: str
    title: str
    content: str | None
    status: str
    target_chapter_id: UUID | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FictionChapterPlanCreate(BaseModel):
    chapter_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    summary: str | None = None
    goals: str | None = None
    conflicts: str | None = None
    scene_ids: list[str] | None = None


class FictionChapterPlanUpdate(BaseModel):
    chapter_id: UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    summary: str | None = None
    goals: str | None = None
    conflicts: str | None = None
    scene_ids: list[str] | None = None
    sort_order: int | None = None


class FictionChapterPlanResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    title: str
    summary: str | None
    goals: str | None
    conflicts: str | None
    scene_ids: list[str] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FictionAIPromptRequest(BaseModel):
    prompt_type: str = Field(
        ...,
        pattern="^(alternate_scenes|improve_dialogue|deepen_emotion|increase_tension|fix_pacing|rewrite_pov|suggest_twists|identify_weak|chapter_summary|scene_ideas|what_happens_next|dialogue_helper)$",
    )
    context: str | None = None
    chapter_id: UUID | None = None
    scene_id: UUID | None = None
    selection: str | None = None
