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
    knowledge_mode: str = Field(
        default="fiction",
        pattern="^(fiction|nonfiction|memoir|workbook|hybrid)$",
        description="Knowledge vault mode: fiction, nonfiction, memoir, workbook, hybrid",
    )
    knowledge_modules: list[str] | None = Field(
        default=None,
        description="Override enabled modules (null = use mode defaults)",
    )


class ProjectUpdate(BaseModel):
    """Update project."""

    name: str | None = Field(None, min_length=1, max_length=255)
    guidance_mode: str | None = Field(
        None,
        pattern="^(guided|flexible|freeform)$",
        description="Genre guidance: guided (full), flexible (lighter), freeform (none)",
    )
    knowledge_mode: str | None = Field(
        None,
        pattern="^(fiction|nonfiction|memoir|workbook|hybrid)$",
        description="Knowledge vault mode: fiction, nonfiction, memoir, workbook, hybrid",
    )
    knowledge_modules: list[str] | None = Field(
        default=None,
        description="Override enabled modules (null = use mode defaults, [] = clear override)",
    )


class ProjectResponse(BaseModel):
    """Project in API response."""

    id: UUID
    user_id: UUID
    name: str
    guidance_mode: str
    template_id: UUID | None = None
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
    knowledge_mode: str = Field(
        default="fiction",
        pattern="^(fiction|nonfiction|memoir|workbook|hybrid)$",
        description="Knowledge vault mode (defaults from book_type if not set)",
    )
    genre: str | None = None
    genre_tags: list[str] | None = Field(None, description="Genre blend, e.g. ['thriller','romance','fantasy']")
    themes: list[str] | None = Field(None, description="Thematic overlays, e.g. ['dystopian','post-apocalyptic']")
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
