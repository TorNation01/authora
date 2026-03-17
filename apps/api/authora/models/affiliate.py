"""Affiliate system models: profiles, clicks, conversions, attributions, payouts."""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base

if TYPE_CHECKING:
    from authora.models.subscription import Subscription
    from authora.models.user import User


class AffiliateProfile(Base):
    """Affiliate account: apply, approve, commission rates."""

    __tablename__ = "affiliate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    commission_rate_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False, default=20)
    commission_recurring_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    application_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="affiliate_profile")
    clicks: Mapped[list["AffiliateClick"]] = relationship("AffiliateClick", back_populates="affiliate", cascade="all, delete-orphan")
    conversions: Mapped[list["AffiliateConversion"]] = relationship("AffiliateConversion", back_populates="affiliate", cascade="all, delete-orphan")
    attributions: Mapped[list["AffiliateAttribution"]] = relationship("AffiliateAttribution", back_populates="affiliate", cascade="all, delete-orphan")
    payouts: Mapped[list["AffiliatePayout"]] = relationship("AffiliatePayout", back_populates="affiliate", cascade="all, delete-orphan")


class AffiliateClick(Base):
    """Affiliate link click (tracking)."""

    __tablename__ = "affiliate_clicks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    affiliate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("affiliate_profiles.id", ondelete="CASCADE"), nullable=False)
    fingerprint_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    landing_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    referrer: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    affiliate: Mapped["AffiliateProfile"] = relationship("AffiliateProfile", back_populates="clicks")


class AffiliateAttribution(Base):
    """User signup attributed to affiliate (one per user)."""

    __tablename__ = "affiliate_attributions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    affiliate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("affiliate_profiles.id", ondelete="CASCADE"), nullable=False)
    attributed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    affiliate: Mapped["AffiliateProfile"] = relationship("AffiliateProfile", back_populates="attributions")


class AffiliateConversion(Base):
    """Revenue event attributed to affiliate (signup or payment)."""

    __tablename__ = "affiliate_conversions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    affiliate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("affiliate_profiles.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True)
    revenue_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    commission_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    commission_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    is_recurring: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fraud_flagged: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fraud_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    converted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    affiliate: Mapped["AffiliateProfile"] = relationship("AffiliateProfile", back_populates="conversions")
    subscription: Mapped["Subscription | None"] = relationship("Subscription", foreign_keys=[subscription_id])


class AffiliatePayout(Base):
    """Payout request and execution."""

    __tablename__ = "affiliate_payouts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    affiliate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("affiliate_profiles.id", ondelete="CASCADE"), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    stripe_payout_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payment_method: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    payment_details: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    affiliate: Mapped["AffiliateProfile"] = relationship("AffiliateProfile", back_populates="payouts")
