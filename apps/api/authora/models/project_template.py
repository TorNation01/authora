"""Project template model."""

import uuid
from datetime import datetime
from typing import Any, TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.project_template import ProjectTemplate


class ProjectTemplate(Base):
    """Project/book template for guided creation."""

    __tablename__ = "project_templates"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_templates.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    who_it_is_for: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_outcome: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_workflow: Mapped[str | None] = mapped_column(Text, nullable=True)
    book_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    genre: Mapped[str | None] = mapped_column(String(255), nullable=True)
    structure_framework: Mapped[str | None] = mapped_column(String(100), nullable=True)
    default_structure: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    default_milestones: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    default_planning_prompts: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    default_accountability: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    ai_prompts: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    export_recommendations: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    setup_questions: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    chapter_skeletons: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_featured: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_disabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    # Marketplace future-ready: paid templates, creator attribution
    price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_paid: Mapped[bool] = mapped_column(default=False, nullable=False)
    creator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    parent: Mapped["ProjectTemplate | None"] = relationship(
        "ProjectTemplate",
        remote_side="ProjectTemplate.id",
        foreign_keys=[parent_id],
        back_populates="children",
    )
    children: Mapped[list["ProjectTemplate"]] = relationship(
        "ProjectTemplate",
        foreign_keys=[parent_id],
        back_populates="parent",
        overlaps="parent",
    )
