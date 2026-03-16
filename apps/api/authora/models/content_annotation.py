"""Content highlights and comments."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Chapter
    from authora.models.note import Note
    from authora.models.user import User


class ContentHighlight(Base):
    """Highlight within chapter or note content."""

    __tablename__ = "content_highlights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True)
    note_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True)
    start_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    end_offset: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter | None"] = relationship("Chapter", back_populates="highlights")
    note: Mapped["Note | None"] = relationship("Note", back_populates="highlights")


class ContentComment(Base):
    """Comment on chapter or note content."""

    __tablename__ = "content_comments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    chapter_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=True)
    note_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("notes.id", ondelete="CASCADE"), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("content_comments.id", ondelete="CASCADE"), nullable=True)
    revision_pass_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("revision_passes.id", ondelete="SET NULL"), nullable=True
    )
    start_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    chapter: Mapped["Chapter | None"] = relationship("Chapter", back_populates="comments")
    note: Mapped["Note | None"] = relationship("Note", back_populates="comments")
    revision_pass: Mapped["RevisionPass | None"] = relationship(
        "RevisionPass", back_populates="comments", foreign_keys="ContentComment.revision_pass_id"
    )
    parent: Mapped["ContentComment | None"] = relationship(
        "ContentComment",
        foreign_keys="ContentComment.parent_id",
        remote_side="ContentComment.id",
        back_populates="replies",
    )
    replies: Mapped[list["ContentComment"]] = relationship(
        "ContentComment",
        back_populates="parent",
        foreign_keys="ContentComment.parent_id",
    )
