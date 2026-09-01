"""Ghostwriter mode schemas."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class GhostwriterIntakeCreate(BaseModel):
    """Intake questionnaire submission — no field limits, be as thorough as you want."""

    mode: str = Field(default="heavy", pattern="^(light|heavy|full)$")
    intake_answers: dict[str, Any] = Field(default_factory=dict)
    voice_tone: str | None = None
    target_audience: str | None = None
    desired_outcome: str | None = None
    word_count_target: int | str | None = None
    deadline: str | None = None
    author_background: str | None = None
    sample_text: str | None = None
    content_warnings: str | None = None
    research_notes: str | None = None


class GhostwriterOutlineApprove(BaseModel):
    """Approve outline (with optional edits)."""

    outline: dict[str, Any] = Field(..., description="Outline structure: {chapters: [{title, summary}, ...]}")


class ChapterBriefCreate(BaseModel):
    """Create/update chapter brief."""

    brief_text: str = Field(..., min_length=1)


class ChapterBriefApprove(BaseModel):
    """Approve chapter brief."""

    approved: bool = True


class ApplyDraftRequest(BaseModel):
    """Apply generated draft to chapter."""

    chapter_id: UUID
    draft_text: str = Field(..., min_length=1)


class GenerateDraftRequest(BaseModel):
    """Request AI draft generation for a chapter."""

    chapter_id: UUID
    use_brief: bool = True


class RegenerateSectionRequest(BaseModel):
    """Regenerate a section with optional feedback."""

    selection: str = Field(..., min_length=1)
    feedback: str | None = None


class RewriteWithFeedbackRequest(BaseModel):
    """Rewrite content with user feedback."""

    selection: str = Field(..., min_length=1)
    feedback: str = Field(..., min_length=1)


class ChapterBriefResponse(BaseModel):
    """Chapter brief in API response."""

    id: UUID
    chapter_id: UUID
    brief_text: str
    approved_at: datetime | None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class GhostwriterWorkspaceResponse(BaseModel):
    """Ghostwriter workspace in API response."""

    id: UUID
    book_id: UUID
    mode: str
    workflow_step: str
    intake_answers: dict[str, Any] | None
    voice_tone: str | None
    target_audience: str | None
    desired_outcome: str | None
    word_count_target: int | str | None = None
    deadline: str | None = None
    author_background: str | None = None
    sample_text: str | None = None
    content_warnings: str | None = None
    research_notes: str | None = None
    outline: dict[str, Any] | None
    outline_approved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    chapter_briefs: list[ChapterBriefResponse] = []

    model_config = {"from_attributes": True}
