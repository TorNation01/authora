"""Chapter brief sheet - the structured, 13-section brief for one chapter.

Additive table. It does not replace the ghostwriter's free-text `chapter_briefs`
table; it sits beside it as the author-facing planning document that a draft
can be generated from.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class ChapterBriefSheet(Base):
    """One structured brief per chapter."""

    __tablename__ = "chapter_brief_sheets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chapter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # {"purpose": {"what_must_accomplish": "...", ...}, ...}
    sections: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    # {"purpose": "working" | "locked" | "undecided"}
    section_status: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
