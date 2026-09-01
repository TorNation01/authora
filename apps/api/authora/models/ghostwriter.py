"""Ghostwriter mode models - intake, approval workflow, content provenance."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book, Chapter
    from authora.models.ghostwriter_session import GhostwriterSession


# Content provenance: who/what created the content
CONTENT_SOURCE_USER = "user_written"
CONTENT_SOURCE_AI_ASSISTED = "ai_assisted"
CONTENT_SOURCE_AI_GENERATED = "ai_generated"

GHOSTWRITER_MODES = ("light", "heavy", "full")
WORKFLOW_STEPS = (
    "intake",           # Questionnaire
    "outline",          # Outline generation & approval
    "briefs",           # Chapter brief generation
    "drafting",         # AI draft generation
    "review",           # Review/edit/approve
)


class GhostwriterWorkspace(Base):
    """Ghostwriter workspace - intake, mode, outline, approval state. One per book."""

    __tablename__ = "ghostwriter_workspaces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    mode: Mapped[str] = mapped_column(String(50), nullable=False, default="heavy")  # light | heavy | full
    workflow_step: Mapped[str] = mapped_column(String(50), nullable=False, default="intake")

    # Intake questionnaire
    intake_answers: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    genre_tags: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)  # genre blend from intake
    themes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)  # thematic overlays
    voice_tone: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    desired_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count_target: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_background: Mapped[str | None] = mapped_column(Text, nullable=True)
    sample_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_warnings: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Outline
    outline: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)  # {chapters: [{title, summary}, ...]}
    outline_approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    book: Mapped["Book"] = relationship("Book", back_populates="ghostwriter_workspace")
    chapter_briefs: Mapped[list["ChapterBrief"]] = relationship(
        "ChapterBrief", back_populates="ghostwriter_workspace", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["GhostwriterSession"]] = relationship(
        "GhostwriterSession", back_populates="ghostwriter_workspace", cascade="all, delete-orphan"
    )


class ChapterBrief(Base):
    """Chapter brief for ghostwriter - AI-generated brief before draft."""

    __tablename__ = "chapter_briefs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ghostwriter_workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("ghostwriter_workspaces.id", ondelete="CASCADE"), nullable=False
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False
    )

    brief_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    ghostwriter_workspace: Mapped["GhostwriterWorkspace"] = relationship(
        "GhostwriterWorkspace", back_populates="chapter_briefs"
    )
    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="chapter_brief")
