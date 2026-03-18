"""Project template schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TemplateResponse(BaseModel):
    """Template in API response."""

    id: UUID
    slug: str
    category: str
    parent_id: UUID | None
    name: str
    description: str | None
    who_it_is_for: str | None
    expected_outcome: str | None
    suggested_workflow: str | None
    book_type: str | None
    genre: str | None
    structure_framework: str | None
    default_structure: dict | None
    default_milestones: list | None
    default_planning_prompts: dict | None
    default_accountability: dict | None
    ai_prompts: dict | None
    export_recommendations: list | None
    setup_questions: list | None
    chapter_skeletons: list | None
    sort_order: int
    is_featured: bool
    is_disabled: bool
    access_level: str = "free"
    premium_pack_slug: str | None = None
    can_use: bool = True
    required_action: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TemplateSummary(BaseModel):
    """Lightweight template summary for lists."""

    id: UUID
    slug: str
    category: str
    parent_id: UUID | None
    name: str
    description: str | None
    book_type: str | None
    genre: str | None
    sort_order: int
    is_featured: bool
    access_level: str = "free"
    premium_pack_slug: str | None = None
    can_use: bool = True
    required_action: str | None = None  # "upgrade" | "purchase:{pack_slug}"

    model_config = {"from_attributes": True}


class TemplateCategory(BaseModel):
    """Template category with children."""

    category: str
    name: str
    templates: list[TemplateSummary]
    children: list[TemplateSummary] = Field(default_factory=list)
