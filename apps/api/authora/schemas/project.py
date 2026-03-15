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

    model_config = {"from_attributes": True}
