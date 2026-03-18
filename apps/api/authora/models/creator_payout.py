"""Creator payout models: earnings, payouts, balance adjustments."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.template_purchase import TemplatePurchase


class CreatorEarning(Base):
    """Creator earnings from a template sale. One per purchase of creator's template."""

    __tablename__ = "creator_earnings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    template_purchase_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("template_purchases.id", ondelete="CASCADE"), nullable=False
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    payout_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("creator_payouts.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    template_purchase: Mapped["TemplatePurchase"] = relationship("TemplatePurchase")
    payout: Mapped["CreatorPayout | None"] = relationship(
        "CreatorPayout",
        back_populates="earnings",
        foreign_keys=[payout_id],
    )


class CreatorPayout(Base):
    """Creator payout request and execution."""

    __tablename__ = "creator_payouts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    stripe_payout_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    earnings: Mapped[list["CreatorEarning"]] = relationship(
        "CreatorEarning",
        back_populates="payout",
        foreign_keys="CreatorEarning.payout_id",
    )


class CreatorBalanceAdjustment(Base):
    """Admin balance adjustment for a creator (credit or debit)."""

    __tablename__ = "creator_balance_adjustments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)  # positive=credit, negative=debit
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
