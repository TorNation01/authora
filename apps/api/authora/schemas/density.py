"""Story Density Engine schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class DensityScanCreate(BaseModel):
    """Request to run a density scan."""

    scan_type: str = Field(
        default="full_project",
        description="full_project, chapter, section, revision_pass, pre_export, trim_chapter, strengthen_targeted",
    )
    triggered_by: str | None = Field(None, description="manual, chapter_complete, revision, export, scheduled")


class DensityScanResponse(BaseModel):
    """Density scan result summary."""

    id: UUID
    project_id: UUID
    book_id: UUID
    scan_type: str
    status: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    chapter_count: int | None
    issue_count: int | None
    manuscript_density_score: float | None
    triggered_by: str | None

    model_config = {"from_attributes": True}


class DensityIssueResponse(BaseModel):
    """Density issue in API response."""

    id: UUID
    scan_id: UUID
    project_id: UUID
    book_id: UUID
    chapter_id: UUID | None
    issue_type: str
    category: str
    action_category: str
    severity: str
    confidence: float
    title: str
    description: str | None
    location_hint: str | None
    related_chapter_ids: list[str] | None
    fix_suggestions: list[dict] | None
    status: str
    marked_intentional_at: datetime | None
    resolved_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DensityIssueUpdate(BaseModel):
    """Update density issue status."""

    status: str | None = Field(None, description="open, resolved, ignored, intentional")


class DensityFixGuidance(BaseModel):
    """Guided fix guidance for a density issue."""

    explanation: str
    why_it_matters: str
    suggestions: list[str]
    fix_suggestions: list[dict]
    recommended_action: str | None = None
    confidence: float | None = None
    alternatives: list[dict] | None = None
    revision_task_suggestion: str | None = None


class DensityDecisionResponse(BaseModel):
    """Trim-vs-strengthen decision for an issue."""

    recommended_action: str
    confidence: float
    explanation: str
    alternatives: list[dict]
    revision_task_suggestion: str | None = None


class DensityAlternativesComparison(BaseModel):
    """Comparison of alternative repair paths."""

    alternatives: list[dict]


class DensityHealthSummary(BaseModel):
    """Manuscript density health summary for dashboard."""

    total_issues: int
    by_severity: dict[str, int]
    by_category: dict[str, int]
    by_action: dict[str, int]
    open_count: int
    manuscript_density_score: float | None
    last_scan_at: datetime | None
    last_scan_issue_count: int | None
