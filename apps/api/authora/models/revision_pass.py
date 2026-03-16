"""Revision pass system for structured manuscript revision."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

# Pass types: structural, clarity, pacing, emotional_depth, consistency, grammar_polish, custom
REVISION_PASS_TYPES = (
    "structural",
    "clarity",
    "pacing",
    "emotional_depth",
    "consistency",
    "grammar_polish",
    "custom",
)

if TYPE_CHECKING:
    from authora.models.book import Book, Chapter
    from authora.models.project import Project


class RevisionPass(Base):
    """Revision pass at project level (e.g. Structural pass, Clarity pass)."""

    __tablename__ = "revision_passes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    book_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True
    )
    pass_type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="revision_passes")
    book: Mapped["Book | None"] = relationship("Book", back_populates="revision_passes")
    chapter_progress: Mapped[list["RevisionPassChapter"]] = relationship(
        "RevisionPassChapter", back_populates="revision_pass", cascade="all, delete-orphan"
    )
    checklist_items: Mapped[list["RevisionChecklistItem"]] = relationship(
        "RevisionChecklistItem", back_populates="revision_pass", cascade="all, delete-orphan"
    )
    comments: Mapped[list["ContentComment"]] = relationship(
        "ContentComment", back_populates="revision_pass", foreign_keys="ContentComment.revision_pass_id"
    )


class RevisionPassChapter(Base):
    """Chapter-level progress for a revision pass."""

    __tablename__ = "revision_pass_chapters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_pass_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("revision_passes.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    revision_pass: Mapped["RevisionPass"] = relationship("RevisionPass", back_populates="chapter_progress")
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="revision_pass_progress")


class RevisionChecklistItem(Base):
    """Checklist item for a revision pass (generated or custom)."""

    __tablename__ = "revision_checklist_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    revision_pass_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("revision_passes.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    revision_pass: Mapped["RevisionPass"] = relationship("RevisionPass", back_populates="checklist_items")
