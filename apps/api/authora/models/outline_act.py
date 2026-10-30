"""Per-book act sheets - what the beginning, middle and ending must establish."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class OutlineActSheet(Base):
    __tablename__ = "outline_act_sheets"
    __table_args__ = (UniqueConstraint("book_id", "act_key", name="uq_outline_act_sheets_book_act"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True
    )
    act_key: Mapped[str] = mapped_column(String(40), nullable=False)
    # Author-facing label and order. Null means "use the built-in default for this key",
    # which keeps Act 1-3 working without a data migration.
    title: Mapped[str | None] = mapped_column(String(120), nullable=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sections: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict, server_default="{}")
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
