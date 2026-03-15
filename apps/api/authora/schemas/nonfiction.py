"""Non-fiction workspace schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class NonfictionWorkspaceCreate(BaseModel):
    core_message: str | None = None
    reader_outcome: str | None = None
    reader_promise: str | None = None
    topic: str | None = None


class NonfictionWorkspaceUpdate(BaseModel):
    core_message: str | None = None
    reader_outcome: str | None = None
    reader_promise: str | None = None
    topic: str | None = None


class NonfictionWorkspaceResponse(BaseModel):
    id: UUID
    book_id: UUID
    core_message: str | None
    reader_outcome: str | None
    reader_promise: str | None
    topic: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TargetAudienceCreate(BaseModel):
    demographics: str | None = None
    pain_points: str | None = None
    goals: str | None = None
    objections: str | None = None


class TargetAudienceUpdate(BaseModel):
    demographics: str | None = None
    pain_points: str | None = None
    goals: str | None = None
    objections: str | None = None


class TargetAudienceResponse(BaseModel):
    id: UUID
    book_id: UUID
    demographics: str | None
    pain_points: str | None
    goals: str | None
    objections: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TransformationFrameworkCreate(BaseModel):
    before_state: str | None = None
    after_state: str | None = None
    steps: list[dict[str, Any]] | None = None


class TransformationFrameworkUpdate(BaseModel):
    before_state: str | None = None
    after_state: str | None = None
    steps: list[dict[str, Any]] | None = None


class TransformationFrameworkResponse(BaseModel):
    id: UUID
    book_id: UUID
    before_state: str | None
    after_state: str | None
    steps: list[dict[str, Any]] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NFChapterPlanCreate(BaseModel):
    chapter_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    summary: str | None = None
    key_points: list[str] | None = None


class NFChapterPlanUpdate(BaseModel):
    chapter_id: UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    summary: str | None = None
    key_points: list[str] | None = None
    sort_order: int | None = None


class NFChapterPlanResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    title: str
    summary: str | None
    key_points: list[str] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArgumentStructureCreate(BaseModel):
    chapter_id: UUID | None = None
    main_argument: str | None = None
    supporting_points: list[dict[str, Any]] | None = None


class ArgumentStructureUpdate(BaseModel):
    chapter_id: UUID | None = None
    main_argument: str | None = None
    supporting_points: list[dict[str, Any]] | None = None
    sort_order: int | None = None


class ArgumentStructureResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    main_argument: str | None
    supporting_points: list[dict[str, Any]] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SupportingExampleCreate(BaseModel):
    chapter_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    category: str | None = None


class SupportingExampleUpdate(BaseModel):
    chapter_id: UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    description: str | None = None
    category: str | None = None
    sort_order: int | None = None


class SupportingExampleResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    title: str
    description: str | None
    category: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseStudyCreate(BaseModel):
    chapter_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    scenario: str | None = None
    outcome: str | None = None
    lessons: str | None = None


class CaseStudyUpdate(BaseModel):
    chapter_id: UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    scenario: str | None = None
    outcome: str | None = None
    lessons: str | None = None
    sort_order: int | None = None


class CaseStudyResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    title: str
    scenario: str | None
    outcome: str | None
    lessons: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class StoryInsertionCreate(BaseModel):
    chapter_id: UUID | None = None
    story_content: str | None = None
    purpose: str | None = None
    placement_notes: str | None = None


class StoryInsertionUpdate(BaseModel):
    chapter_id: UUID | None = None
    story_content: str | None = None
    purpose: str | None = None
    placement_notes: str | None = None
    sort_order: int | None = None


class StoryInsertionResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    story_content: str | None
    purpose: str | None
    placement_notes: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NFWorksheetCreate(BaseModel):
    chapter_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    items: list[dict[str, Any]] | None = None


class NFWorksheetUpdate(BaseModel):
    chapter_id: UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    items: list[dict[str, Any]] | None = None
    sort_order: int | None = None


class NFWorksheetResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    title: str
    items: list[dict[str, Any]] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NFResearchNoteCreate(BaseModel):
    chapter_id: UUID | None = None
    title: str = Field(..., min_length=1, max_length=500)
    content: str | None = None
    source: str | None = None


class NFResearchNoteUpdate(BaseModel):
    chapter_id: UUID | None = None
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    source: str | None = None
    sort_order: int | None = None


class NFResearchNoteResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    title: str
    content: str | None
    source: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CitationPlaceholderCreate(BaseModel):
    chapter_id: UUID | None = None
    placeholder_text: str = Field(..., min_length=1, max_length=500)
    source_hint: str | None = None


class CitationPlaceholderUpdate(BaseModel):
    chapter_id: UUID | None = None
    placeholder_text: str | None = Field(None, min_length=1, max_length=500)
    source_hint: str | None = None
    status: str | None = Field(None, pattern="^(pending|resolved)$")
    sort_order: int | None = None


class CitationPlaceholderResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    placeholder_text: str
    source_hint: str | None
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AuthorityBuilderCreate(BaseModel):
    credentials: str | None = None
    experience: str | None = None
    testimonials: str | None = None


class AuthorityBuilderUpdate(BaseModel):
    credentials: str | None = None
    experience: str | None = None
    testimonials: str | None = None
    sort_order: int | None = None


class AuthorityBuilderResponse(BaseModel):
    id: UUID
    book_id: UUID
    credentials: str | None
    experience: str | None
    testimonials: str | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SummaryActionStepCreate(BaseModel):
    chapter_id: UUID | None = None
    summary: str | None = None
    action_steps: list[str] | None = None


class SummaryActionStepUpdate(BaseModel):
    chapter_id: UUID | None = None
    summary: str | None = None
    action_steps: list[str] | None = None
    sort_order: int | None = None


class SummaryActionStepResponse(BaseModel):
    id: UUID
    book_id: UUID
    chapter_id: UUID | None
    summary: str | None
    action_steps: list[str] | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
