"""In-editor citation markers linking chapters to sources."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Chapter
    from authora.models.vault import Source


class ChapterCitation(Base):
    """Citation marker in a chapter, linked to a vault source."""

    __tablename__ = "chapter_citations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("vault_sources.id", ondelete="CASCADE"), nullable=False)
    citation_key: Mapped[str] = mapped_column(String(100), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer(), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped["Chapter"] = relationship("Chapter", back_populates="chapter_citations")
    source: Mapped["Source"] = relationship("Source", back_populates="chapter_citations")
