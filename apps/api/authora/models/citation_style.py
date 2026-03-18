"""Citation style (CSL) models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.book import Book
    from authora.models.project import Project


class CitationStyle(Base):
    """CSL citation style (APA, MLA, Chicago, etc.)."""

    __tablename__ = "citation_styles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    csl_xml: Mapped[str | None] = mapped_column(Text(), nullable=True)
    is_builtin: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ProjectCitationStyle(Base):
    """Project or book-level citation style preference."""

    __tablename__ = "project_citation_styles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=True)
    citation_style_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("citation_styles.id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="citation_style_prefs")
    book: Mapped["Book | None"] = relationship("Book", back_populates="citation_style_pref")
    citation_style: Mapped["CitationStyle"] = relationship("CitationStyle")
