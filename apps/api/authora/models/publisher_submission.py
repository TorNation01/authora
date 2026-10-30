"""Publisher submission record.

One row per push of a book to a publishing house. The house is a real, external
system (Anema House's intake), so this table keeps what was sent, the reference
the house returned, and the last status we were told. Nothing here implies the
house accepted the book.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book


class PublisherSubmission(Base):
    """A manuscript pack sent to a publishing house for review."""

    __tablename__ = "publisher_submissions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    publisher_name: Mapped[str] = mapped_column(String(255), nullable=False)
    publisher_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # Reference issued by the house (e.g. AH-2026-0007). Unique per house.
    ref: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="received")
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Exactly what was sent, so the author can see it later without guessing.
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    files: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)

    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    book: Mapped["Book"] = relationship("Book")
