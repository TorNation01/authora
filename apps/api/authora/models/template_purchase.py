"""Template purchase model - individual creator template sales."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from authora.database import Base


class TemplatePurchase(Base):
    """User's purchase of a single creator template."""

    __tablename__ = "template_purchases"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_templates.id", ondelete="CASCADE"), nullable=False
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stripe_session_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    purchased_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
