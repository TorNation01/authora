"""Story Integrity Engine schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IntegrityScanCreate(BaseModel):
    """Request to run a scan."""

    scan_type: str = Field(default="full_project", description="full_project, chapter, export_readiness, etc.")
    triggered_by: str | None = Field(None, description="manual, milestone, export, etc.")


class IntegrityScanResponse(BaseModel):
    """Scan result summary."""

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
    triggered_by: str | None

    model_config = {"from_attributes": True}


class IntegrityIssueResponse(BaseModel):
    """Issue in API response."""

    id: UUID
    scan_id: UUID
    project_id: UUID
    book_id: UUID
    chapter_id: UUID | None
    issue_type: str
    category: str
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


class IntegrityIssueUpdate(BaseModel):
    """Update issue status."""

    status: str | None = Field(None, description="open, resolved, ignored, intentional")


class IntegrityFixGuidance(BaseModel):
    """Guided fix guidance for an issue."""

    explanation: str
    why_it_matters: str
    suggestions: list[str]
    fix_suggestions: list[dict]


class StoryHealthSummary(BaseModel):
    """Story health summary for dashboard."""

    total_issues: int
    by_severity: dict[str, int]
    by_category: dict[str, int]
    open_count: int
    last_scan_at: datetime | None
    last_scan_issue_count: int | None


class ChapterHealthIssue(BaseModel):
    """Chapter-level issue from analyzer."""

    type: str
    severity: str
    title: str
    suggestion: str


class ChapterHealthFix(BaseModel):
    """Suggested fix for a chapter."""

    action: str
    label: str


class ChapterHealthResponse(BaseModel):
    """Per-chapter health analysis."""

    chapter_id: str
    chapter_index: int
    title: str
    word_count: int
    health: str
    health_reason: str
    purpose_clarity: float
    relationship_to_manuscript: float
    tension_level: float
    emotional_movement: float
    plot_movement: float
    information_density: float
    pacing: float
    transition_quality: float
    opening_strength: float
    closing_strength: float
    chapter_linkage: float
    repetition: float
    unresolved_internal: float
    what_this_chapter_is_doing: str
    why_feels_off: str | None
    suggested_fixes: list[ChapterHealthFix]
    issues: list[ChapterHealthIssue]


class ChapterHealthListResponse(BaseModel):
    """Chapter health data from latest scan."""

    chapters: list[ChapterHealthResponse]
    scan_id: str | None
    last_scan_at: datetime | None
