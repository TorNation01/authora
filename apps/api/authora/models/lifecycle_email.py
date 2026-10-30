"""Lifecycle email log — one row per (user, ladder step).

The seven-message ladder runs from signup to the first published book. Without
this table the sequence cannot exist: the sweep would re-send the same message
on every run, and there would be no record of which customers had been nudged.
The unique key is the idempotency guarantee; a `failed` row is retried by
updating it, not by inserting a second one.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base

if TYPE_CHECKING:
    pass


class LifecycleEmailLog(Base):
    """One row per user per lifecycle step: sent, skipped or failed."""

    __tablename__ = "lifecycle_email_log"
    __table_args__ = (UniqueConstraint("user_id", "step", name="uq_lifecycle_email_user_step"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)  # sent | skipped | failed
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
