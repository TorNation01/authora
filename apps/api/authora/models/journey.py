"""Journey and onboarding models."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.user import User

PHASES = [
    "idea",
    "concept",
    "outline",
    "chapter_planning",
    "drafting",
    "revision",
    "polish",
    "export_prep",
]


class UserJourney(Base):
    """User's writing journey - onboarding answers and current state."""

    __tablename__ = "user_journeys"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    book_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="SET NULL"), nullable=True)

    # Onboarding answers
    book_type: Mapped[str] = mapped_column(String(50), nullable=False)  # fiction | nonfiction
    writing_mode: Mapped[str] = mapped_column(String(50), nullable=False)  # solo | cowrite | ghostwriter
    writing_goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_timeline: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "3 months"
    writing_schedule: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g. "mornings"
    accountability_style: Mapped[str | None] = mapped_column(String(100), nullable=True)  # gentle | structured | buddy
    ai_comfort_level: Mapped[str | None] = mapped_column(String(50), nullable=True)  # minimal | moderate | full
    genre_topic: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Roadmap (generated)
    roadmap: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Current state
    current_phase: Mapped[str] = mapped_column(String(50), nullable=False, default="idea")
    phase_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class JourneyTask(Base):
    """Individual task within a phase."""

    __tablename__ = "journey_tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    journey_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("user_journeys.id", ondelete="CASCADE"), nullable=False)
    phase: Mapped[str] = mapped_column(String(50), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, default="checklist")  # checklist | action | milestone
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
