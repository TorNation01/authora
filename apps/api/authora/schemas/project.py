"""Project schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Create project."""

    name: str = Field(..., min_length=1, max_length=255)
    guidance_mode: str = Field(
        default="guided",
        pattern="^(guided|flexible|freeform)$",
        description="Genre guidance: guided (full), flexible (lighter), freeform (none)",
    )


class ProjectUpdate(BaseModel):
    """Update project."""

    name: str | None = Field(None, min_length=1, max_length=255)
    guidance_mode: str | None = Field(
        None,
        pattern="^(guided|flexible|freeform)$",
        description="Genre guidance: guided (full), flexible (lighter), freeform (none)",
    )


class ProjectResponse(BaseModel):
    """Project in API response."""

    id: UUID
    user_id: UUID
    name: str
    guidance_mode: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    last_accessed_at: datetime | None = None

    model_config = {"from_attributes": True}


class DeleteProjectConfirm(BaseModel):
    """Confirmation for project deletion."""

    confirm: bool = Field(..., description="Must be true to delete")


class ProjectWizardRequest(BaseModel):
    """Project creation wizard request."""

    template_id: UUID | None = Field(None, description="Template ID (omit for custom/blank)")
    project_name: str = Field(..., min_length=1, max_length=255)
    book_title: str | None = Field(None, min_length=1, max_length=500)
    book_type: str = Field(default="fiction", pattern="^(fiction|nonfiction)$")
    genre: str | None = None
    core_idea: str | None = Field(None, max_length=2000)
    wizard_answers: dict[str, str | int | list] | None = None
    structure_framework: str | None = None
    framework_id: UUID | None = Field(None, description="Writing framework ID (overrides template)")
    target_words: int | None = Field(None, ge=0)
    target_date: str | None = Field(None, max_length=50)
    guidance_mode: str = Field(
        default="guided",
        pattern="^(guided|flexible|freeform)$",
        description="Genre guidance: guided (full), flexible (lighter), freeform (none)",
    )
