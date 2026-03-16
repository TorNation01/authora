"""Writing framework model."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class WritingFramework(Base):
    """Writing framework (Three-Act, Hero's Journey, Problem-Solution, etc.)."""

    __tablename__ = "writing_frameworks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    book_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    ideal_use_cases: Mapped[str | None] = mapped_column(Text, nullable=True)
    ideal_genres: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    planning_stages: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    beat_stages: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    chapter_structure: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    manuscript_scaffolding: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    chapter_skeletons: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    milestone_logic: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    accountability_mapping: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    revision_checklist: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    ai_prompt_presets: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    recommendation_rules: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    scene_prompts: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_featured: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_disabled: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
