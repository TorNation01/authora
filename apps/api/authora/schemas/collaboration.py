"""Collaboration schemas: invites, members, shares, approvals, activity."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectInviteCreate(BaseModel):
    """Create project invite."""

    email: str = Field(..., min_length=1, max_length=255)
    role: str = Field(
        ...,
        pattern="^(owner|admin|editor|beta_reader|reviewer|client|co_writer|viewer|guest)$",
    )


class ProjectInviteResponse(BaseModel):
    """Invite in API response."""

    id: UUID
    email: str
    project_id: UUID
    role: str
    status: str
    expires_at: datetime
    invited_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ProjectMemberResponse(BaseModel):
    """Project member in API response."""

    id: UUID
    user_id: UUID
    project_id: UUID
    role: str
    invited_by: UUID | None
    joined_at: datetime
    created_at: datetime
    email: str | None = None
    display_name: str | None = None

    model_config = {"from_attributes": True}


class ProjectShareCreate(BaseModel):
    """Create project share."""

    share_scope: str = Field(
        ...,
        pattern="^(full_project|manuscript|chapters|review_copy)$",
    )
    chapter_ids: list[UUID] | None = Field(None, description="Required for chapters scope")
    shared_with_user_id: UUID | None = None
    shared_with_email: str | None = Field(None, max_length=255)


class ProjectShareResponse(BaseModel):
    """Project share in API response."""

    id: UUID
    project_id: UUID
    share_scope: str
    chapter_ids: list | None = None
    shared_with_user_id: UUID | None = None
    shared_with_email: str | None = None
    created_by: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterApprovalResponse(BaseModel):
    """Chapter approval in API response."""

    id: UUID
    chapter_id: UUID
    status: str
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterApprovalUpdate(BaseModel):
    """Update chapter approval."""

    status: str = Field(
        ...,
        pattern="^(pending|approved|rejected|changes_requested)$",
    )
    notes: str | None = Field(None, max_length=2000)


class CollaborationActivityResponse(BaseModel):
    """Collaboration activity in API response."""

    id: UUID
    project_id: UUID
    user_id: UUID | None = None
    action: str
    entity_type: str | None = None
    entity_id: str | None = None
    extra_data: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
