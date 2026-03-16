"""Content highlight and comment schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ContentHighlightCreate(BaseModel):
    """Create highlight."""

    start_offset: int = Field(..., ge=0)
    end_offset: int = Field(..., ge=0)
    color: str | None = Field(None, max_length=20)


class ContentHighlightResponse(BaseModel):
    """Highlight in API response."""

    id: UUID
    chapter_id: UUID | None
    note_id: UUID | None
    start_offset: int
    end_offset: int
    color: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentCommentCreate(BaseModel):
    """Create comment."""

    start_offset: int | None = Field(None, ge=0)
    end_offset: int | None = Field(None, ge=0)
    body: str = Field(..., min_length=1)
    parent_id: UUID | None = None
    revision_pass_id: UUID | None = None
    comment_type: str | None = Field(
        None,
        pattern="^(clarity|rewrite|pacing|continuity|tone|emotion|grammar|proofing|fact_check|question|approval|change_request|idea|client_request|beta_feedback|general|rewrite_suggestion|clarity_issue|pacing_note|grammar_spelling|consistency|character_voice|plot_continuity|other)$",
    )
    collaboration_role: str | None = Field(
        None,
        pattern="^(owner|admin|editor|beta_reader|reviewer|client|co_writer|viewer|guest)$",
    )


class ContentCommentUpdate(BaseModel):
    """Update comment."""

    body: str | None = Field(None, min_length=1)
    resolved: bool | None = None
    status: str | None = Field(
        None,
        pattern="^(open|in_review|resolved|deferred|needs_decision)$",
    )
    comment_type: str | None = Field(
        None,
        pattern="^(clarity|rewrite|pacing|continuity|tone|emotion|grammar|proofing|fact_check|question|approval|change_request|idea|client_request|beta_feedback|general|rewrite_suggestion|clarity_issue|pacing_note|grammar_spelling|consistency|character_voice|plot_continuity|other)$",
    )


class ContentCommentResponse(BaseModel):
    """Comment in API response."""

    id: UUID
    user_id: UUID | None = None
    chapter_id: UUID | None
    note_id: UUID | None
    parent_id: UUID | None
    revision_pass_id: UUID | None = None
    start_offset: int | None
    end_offset: int | None
    body: str
    comment_type: str | None = None
    collaboration_role: str | None = None
    status: str = "open"
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime
    replies: list["ContentCommentResponse"] = []
    user_email: str | None = None
    user_display_name: str | None = None

    model_config = {"from_attributes": True}


ContentCommentResponse.model_rebuild()
