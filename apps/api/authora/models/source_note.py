"""Source notes / annotations on vault sources."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.user import User
    from authora.models.vault import Source


class SourceNote(Base):
    """Note or annotation on a vault source (for literature review, annotated bib)."""

    __tablename__ = "source_notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_sources.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), nullable=False, default="annotation")
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    page_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    source: Mapped["Source"] = relationship("Source", back_populates="source_notes")
    user: Mapped["User"] = relationship("User")
