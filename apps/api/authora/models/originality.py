"""Originality, similarity, AI-assistance, and AI-origin risk review models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book, Chapter
    from authora.models.project import Project
    from authora.models.user import User


class ComparisonCorpus(Base):
    """Corpus for similarity comparison (user projects, uploaded, course, reference)."""

    __tablename__ = "comparison_corpora"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    corpus_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class OriginalityScan(Base):
    """Originality/similarity scan run."""

    __tablename__ = "originality_scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    overall_similarity_pct: Mapped[float | None] = mapped_column(Float(), nullable=True)
    excluded_ranges: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB(), nullable=True)
    corpus_ids: Mapped[list[str] | None] = mapped_column(JSONB(), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    project: Mapped["Project"] = relationship("Project")
    book: Mapped["Book"] = relationship("Book")
    matched_passages: Mapped[list["MatchedPassage"]] = relationship(
        "MatchedPassage", back_populates="scan", cascade="all, delete-orphan"
    )


class MatchedPassage(Base):
    """Matched passage from similarity comparison."""

    __tablename__ = "matched_passages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("originality_scans.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_label: Mapped[str | None] = mapped_column(String(500), nullable=True)
    match_type: Mapped[str] = mapped_column(String(50), nullable=False)
    similarity_pct: Mapped[float | None] = mapped_column(Float(), nullable=True)
    query_text: Mapped[str] = mapped_column(Text(), nullable=False)
    matched_text: Mapped[str] = mapped_column(Text(), nullable=False)
    query_start: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    query_end: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    scan: Mapped["OriginalityScan"] = relationship("OriginalityScan", back_populates="matched_passages")
    chapter: Mapped["Chapter | None"] = relationship("Chapter")


class AIAssistanceDisclosure(Base):
    """AI-assistance disclosure (user-disclosed or system-tracked)."""

    __tablename__ = "ai_assistance_disclosures"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    disclosure_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content_source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_action_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_action_log.id", ondelete="SET NULL"), nullable=True)
    section_hint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AIOriginRiskReview(Base):
    """AI-origin risk review (probabilistic, review-aid only)."""

    __tablename__ = "ai_origin_risk_reviews"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    risk_band: Mapped[str] = mapped_column(String(50), nullable=False)
    confidence_low: Mapped[float | None] = mapped_column(Float(), nullable=True)
    confidence_high: Mapped[float | None] = mapped_column(Float(), nullable=True)
    signals_summary: Mapped[dict[str, Any] | None] = mapped_column(JSONB(), nullable=True)
    disclaimer_ack: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IntegrityReviewReport(Base):
    """Integrity review report (educator/reviewer workflow)."""

    __tablename__ = "integrity_review_reports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    originality_scan_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("originality_scans.id", ondelete="SET NULL"), nullable=True)
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    needs_human_review: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=False)
    reviewer_notes: Mapped[str | None] = mapped_column(Text(), nullable=True)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class IntegrityReviewComment(Base):
    """Review comment on matched passage or report."""

    __tablename__ = "integrity_review_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("integrity_review_reports.id", ondelete="CASCADE"), nullable=False)
    matched_passage_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("matched_passages.id", ondelete="SET NULL"), nullable=True)
    comment_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class OriginalityAdminConfig(Base):
    """Admin config for originality/similarity features."""

    __tablename__ = "originality_admin_config"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    value: Mapped[dict[str, Any] | None] = mapped_column(JSONB(), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
