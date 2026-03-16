"""Book and chapter models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.ai_revision import AIRevision
    from authora.models.book_settings import BookSettings
    from authora.models.content_annotation import ContentComment, ContentHighlight
    from authora.models.ghostwriter import ChapterBrief, GhostwriterWorkspace
    from authora.models.chapter_section import ChapterSection
    from authora.models.note import Note
    from authora.models.project import Project
    from authora.models.project_template import ProjectTemplate
    from authora.models.publishing_asset import PublishingAsset
    from authora.models.writing_framework import WritingFramework


class Book(Base):
    """Book (fiction or nonfiction)."""

    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    genre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default="fiction")  # fiction | nonfiction
    planner_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    template_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_templates.id", ondelete="SET NULL"), nullable=True
    )
    framework_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("writing_frameworks.id", ondelete="SET NULL"), nullable=True
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="books")
    template: Mapped["ProjectTemplate | None"] = relationship("ProjectTemplate", foreign_keys=[template_id])
    framework: Mapped["WritingFramework | None"] = relationship("WritingFramework", foreign_keys=[framework_id])
    chapters: Mapped[list["Chapter"]] = relationship("Chapter", back_populates="book", cascade="all, delete-orphan", order_by="Chapter.sort_order")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="book", cascade="all, delete-orphan")
    ghostwriter_workspace: Mapped["GhostwriterWorkspace | None"] = relationship(
        "GhostwriterWorkspace", back_populates="book", uselist=False, cascade="all, delete-orphan"
    )
    book_settings: Mapped["BookSettings | None"] = relationship(
        "BookSettings", back_populates="book", uselist=False, cascade="all, delete-orphan"
    )
    publishing_assets: Mapped[list["PublishingAsset"]] = relationship(
        "PublishingAsset", back_populates="book", cascade="all, delete-orphan"
    )


class Chapter(Base):
    """Book chapter."""

    __tablename__ = "chapters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    section_status: Mapped[str | None] = mapped_column(String(50), nullable=True, default="draft")
    gamification_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    book: Mapped["Book"] = relationship("Book", back_populates="chapters")
    notes: Mapped[list["Note"]] = relationship("Note", back_populates="chapter")
    content_source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # user_written | ai_assisted | ai_generated
    chapter_brief: Mapped["ChapterBrief | None"] = relationship(
        "ChapterBrief", back_populates="chapter", uselist=False, cascade="all, delete-orphan"
    )
    versions: Mapped[list["ChapterVersion"]] = relationship(
        "ChapterVersion", back_populates="chapter", cascade="all, delete-orphan", order_by="ChapterVersion.created_at.desc()"
    )
    sections: Mapped[list["ChapterSection"]] = relationship(
        "ChapterSection", back_populates="chapter", cascade="all, delete-orphan", foreign_keys="ChapterSection.chapter_id"
    )
    highlights: Mapped[list["ContentHighlight"]] = relationship(
        "ContentHighlight", back_populates="chapter", cascade="all, delete-orphan"
    )
    comments: Mapped[list["ContentComment"]] = relationship(
        "ContentComment", back_populates="chapter", cascade="all, delete-orphan"
    )
    ai_revisions: Mapped[list["AIRevision"]] = relationship(
        "AIRevision", back_populates="chapter", cascade="all, delete-orphan"
    )


class ChapterVersion(Base):
    """Chapter content version for history."""

    __tablename__ = "chapter_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content_source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # user_written | ai_assisted | ai_generated
    created_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="versions")
