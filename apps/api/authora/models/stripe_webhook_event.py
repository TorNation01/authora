"""Stripe webhook event model - idempotency tracking."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class StripeWebhookEvent(Base):
    """Processed Stripe webhook events for idempotency."""

    __tablename__ = "stripe_webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stripe_event_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    event_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
