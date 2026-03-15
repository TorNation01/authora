"""Project schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Create project."""

    name: str = Field(..., min_length=1, max_length=255)


class ProjectUpdate(BaseModel):
    """Update project."""

    name: str | None = Field(None, min_length=1, max_length=255)


class ProjectResponse(BaseModel):
    """Project in API response."""

    id: UUID
    user_id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    last_accessed_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeleteProjectConfirm(BaseModel):
    """Confirmation for project deletion."""

    confirm: bool = Field(..., description="Must be true to delete")
