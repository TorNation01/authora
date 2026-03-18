"""Originality, similarity, AI-assistance, and AI-origin risk schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ComparisonCorpusCreate(BaseModel):
    """Create comparison corpus."""

    corpus_type: str = Field(..., description="user_projects, uploaded, course, reference")
    name: str = Field(..., max_length=255)
    description: str | None = None
    project_id: UUID | None = None


class ComparisonCorpusResponse(BaseModel):
    """Comparison corpus in API response."""

    id: UUID
    project_id: UUID | None
    user_id: UUID
    corpus_type: str
    name: str
    description: str | None
    is_enabled: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class OriginalityScanCreate(BaseModel):
    """Request to run originality scan."""

    corpus_ids: list[UUID] | None = Field(None, description="Corpora to compare against; omit for defaults")
    excluded_ranges: list[dict] | None = Field(None, description="Excluded sections (bibliography, quotes, etc.)")
    min_similarity: float = Field(0.5, ge=0, le=1, description="Minimum similarity threshold")


class OriginalityScanResponse(BaseModel):
    """Originality scan result."""

    id: UUID
    project_id: UUID
    book_id: UUID
    status: str
    overall_similarity_pct: float | None
    excluded_ranges: list[dict] | None
    corpus_ids: list[str] | None
    started_at: datetime
    completed_at: datetime | None
    created_by: UUID | None

    model_config = {"from_attributes": True}


class MatchedPassageResponse(BaseModel):
    """Matched passage from similarity comparison."""

    id: UUID
    scan_id: UUID
    chapter_id: UUID | None
    source_type: str
    source_id: str | None
    source_label: str | None
    match_type: str
    similarity_pct: float | None
    query_text: str
    matched_text: str
    query_start: int | None
    query_end: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIAssistanceDisclosureCreate(BaseModel):
    """Create AI-assistance disclosure."""

    book_id: UUID | None = None
    chapter_id: UUID | None = None
    disclosure_type: str = Field(..., description="user_disclosed, system_tracked")
    content_source: str | None = Field(None, description="user_written, ai_assisted, ai_generated")
    ai_action_id: UUID | None = None
    section_hint: str | None = None
    notes: str | None = None


class AIAssistanceDisclosureResponse(BaseModel):
    """AI-assistance disclosure in API response."""

    id: UUID
    project_id: UUID
    book_id: UUID | None
    chapter_id: UUID | None
    user_id: UUID
    disclosure_type: str
    content_source: str | None
    section_hint: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIOriginRiskResponse(BaseModel):
    """AI-origin risk review (probabilistic, review-aid only)."""

    risk_band: str
    confidence_low: float
    confidence_high: float
    signals_summary: dict
    disclaimer: str


class IntegrityReviewReportCreate(BaseModel):
    """Create integrity review report."""

    originality_scan_id: UUID | None = None
    needs_human_review: bool = False
    reviewer_notes: str | None = None


class IntegrityReviewReportUpdate(BaseModel):
    """Update integrity review report (partial)."""

    originality_scan_id: UUID | None = None
    needs_human_review: bool | None = None
    reviewer_notes: str | None = None


class IntegrityReviewReportResponse(BaseModel):
    """Integrity review report."""

    id: UUID
    project_id: UUID
    book_id: UUID
    originality_scan_id: UUID | None
    reviewer_id: UUID | None
    status: str
    needs_human_review: bool
    reviewer_notes: str | None
    exported_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IntegrityReviewCommentCreate(BaseModel):
    """Create review comment."""

    matched_passage_id: UUID | None = None
    comment_type: str = Field(..., description="general, source, note")
    content: str


class IntegrityReviewCommentResponse(BaseModel):
    """Review comment."""

    id: UUID
    report_id: UUID
    matched_passage_id: UUID | None
    comment_type: str
    content: str
    author_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class OriginalityReportSummary(BaseModel):
    """Full originality report summary."""

    scan: OriginalityScanResponse
    matched_passages: list[MatchedPassageResponse]
    ai_assistance_disclosures: list[AIAssistanceDisclosureResponse]
    ai_origin_risk: AIOriginRiskResponse | None
    review_report: IntegrityReviewReportResponse | None


class OriginalityAdminConfigUpdate(BaseModel):
    """Update admin config."""

    value: dict | None = None
