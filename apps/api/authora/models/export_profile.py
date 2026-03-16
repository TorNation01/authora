"""Export profile model - saved export presets."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.user import User


class ExportProfile(Base):
    """Saved export preset - format, options, naming, project-type handling."""

    __tablename__ = "export_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Preset type: system presets are built-in; custom are user-created
    is_system: Mapped[bool] = mapped_column(default=False, nullable=False)
    system_key: Mapped[str | None] = mapped_column(String(50), nullable=True)  # clean_manuscript, beta_reader, etc.

    # Format and compile
    format: Mapped[str] = mapped_column(String(20), nullable=False, default="docx")
    compile_type: Mapped[str] = mapped_column(String(50), nullable=False, default="full")
    format_style: Mapped[str] = mapped_column(String(20), nullable=False, default="manuscript")

    # Options (JSON)
    options: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    front_matter_blocks: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)
    back_matter_blocks: Mapped[list[dict] | None] = mapped_column(JSONB, nullable=True)

    # Naming pattern: {project_title}, {profile}, {date}, {version}, {author}
    naming_pattern: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Project type hint (fiction, nonfiction, memoir, workbook, journal, ghostwritten)
    project_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="export_profiles")
