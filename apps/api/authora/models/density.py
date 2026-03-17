"""Story Density Engine models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book, Chapter
    from authora.models.project import Project
    from authora.models.user import User


DENSITY_ACTION_CATEGORIES = (
    "trim",
    "compress",
    "strengthen",
    "expand",
    "bridge",
    "clarify",
    "merge",
    "keep_as_intentional",
)

DENSITY_ISSUE_CATEGORIES = (
    "clutter",
    "filler",
    "repetition",
    "drag",
    "over_explanation",
    "thin_support",
    "rushed_moment",
    "weak_transition",
    "bloated_scene",
    "underweighted_payoff",
    "instructional_redundancy",
    "practical_support_gap",
)


class DensityScan(Base):
    """A manuscript density scan run."""

    __tablename__ = "density_scans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    scan_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chapter_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    issue_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manuscript_density_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    density_map_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    extra_data: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(50), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="density_scans")
    book: Mapped["Book"] = relationship("Book", back_populates="density_scans")
    issues: Mapped[list["DensityIssue"]] = relationship(
        "DensityIssue", back_populates="scan", cascade="all, delete-orphan"
    )


class DensityIssue(Base):
    """A detected density issue (clutter, filler, thin support, etc.)."""

    __tablename__ = "density_issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("density_scans.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    issue_type: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    action_category: Mapped[str] = mapped_column(String(30), nullable=False, default="trim")
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_hint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    related_chapter_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    fix_suggestions: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    marked_intentional_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scan: Mapped["DensityScan"] = relationship("DensityScan", back_populates="issues")
    project: Mapped["Project"] = relationship("Project", back_populates="density_issues")
    book: Mapped["Book"] = relationship("Book", back_populates="density_issues")
    chapter: Mapped["Chapter | None"] = relationship("Chapter", back_populates="density_issues")
