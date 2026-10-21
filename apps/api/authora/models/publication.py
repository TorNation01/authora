"""Book publication record: publishing metadata plus the release record."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book


DEFAULT_IMPRINT = "Anema House Publishing"


class BookPublication(Base):
    """Metadata used to turn a manuscript into a book, and its release record.

    One row per book. ``status`` is ``draft`` until the author records a
    release; ``released_at``/``release_*`` describe what the author declared,
    not what any retailer received.
    """

    __tablename__ = "book_publications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, unique=True
    )

    # Metadata
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    subtitle: Mapped[str | None] = mapped_column(String(500), nullable=True)
    author_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    blurb: Mapped[str | None] = mapped_column(Text, nullable=True)
    short_description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    keywords: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    categories: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    language: Mapped[str] = mapped_column(String(10), nullable=False, default="en")
    isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    imprint: Mapped[str] = mapped_column(String(255), nullable=False, default=DEFAULT_IMPRINT)

    # Front / back matter
    copyright_notice: Mapped[str | None] = mapped_column(Text, nullable=True)
    dedication: Mapped[str | None] = mapped_column(Text, nullable=True)
    front_matter: Mapped[str | None] = mapped_column(Text, nullable=True)
    acknowledgements: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    back_matter: Mapped[str | None] = mapped_column(Text, nullable=True)
    include_imprint_page: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Release record
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    released_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    release_formats: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    release_imprint: Mapped[str | None] = mapped_column(String(255), nullable=True)
    release_isbn: Mapped[str | None] = mapped_column(String(20), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    book: Mapped["Book"] = relationship("Book", back_populates="publication")

    @property
    def is_released(self) -> bool:
        return self.status == "released" and self.released_at is not None

    def release_record(self) -> dict[str, Any] | None:
        if not self.is_released:
            return None
        return {
            "released_at": self.released_at.isoformat() if self.released_at else None,
            "formats": list(self.release_formats or []),
            "imprint": self.release_imprint,
            "isbn": self.release_isbn,
        }
