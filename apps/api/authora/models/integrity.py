"""Story Integrity Engine models."""

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


class IntegrityScan(Base):
    """A manuscript integrity scan run."""

    __tablename__ = "integrity_scans"

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
    story_map_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    extra_data: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    triggered_by: Mapped[str | None] = mapped_column(String(50), nullable=True)

    project: Mapped["Project"] = relationship("Project", back_populates="integrity_scans")
    book: Mapped["Book"] = relationship("Book", back_populates="integrity_scans")
    issues: Mapped[list["IntegrityIssue"]] = relationship(
        "IntegrityIssue", back_populates="scan", cascade="all, delete-orphan"
    )
    analytics: Mapped[list["IntegrityScanAnalytics"]] = relationship(
        "IntegrityScanAnalytics", back_populates="scan", cascade="all, delete-orphan"
    )


class IntegrityIssue(Base):
    """A detected integrity issue."""

    __tablename__ = "integrity_issues"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("integrity_scans.id", ondelete="CASCADE"), nullable=False)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="SET NULL"), nullable=True)
    issue_type: Mapped[str] = mapped_column(String(80), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_hint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    related_chapter_ids: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    related_entity_ids: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    fix_suggestions: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")
    marked_intentional_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scan: Mapped["IntegrityScan"] = relationship("IntegrityScan", back_populates="issues")
    project: Mapped["Project"] = relationship("Project", back_populates="integrity_issues")
    book: Mapped["Book"] = relationship("Book", back_populates="integrity_issues")
    chapter: Mapped["Chapter | None"] = relationship("Chapter", back_populates="integrity_issues")


class IntegrityScanAnalytics(Base):
    """Analytics events for integrity scans."""

    __tablename__ = "integrity_scan_analytics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("integrity_scans.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    event_data: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    scan: Mapped["IntegrityScan"] = relationship("IntegrityScan", back_populates="analytics")
