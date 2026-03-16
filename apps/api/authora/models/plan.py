"""Billing plan model."""

import uuid
from typing import Any

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from authora.database import Base


class Plan(Base):
    """Billing plan tier (free, starter, pro, studio, founder_lifetime)."""

    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    limits: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    features: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    price_monthly_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_yearly_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_lifetime_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stripe_price_id_monthly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_price_id_yearly: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_price_id_lifetime: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now())

    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="plan", foreign_keys="Subscription.plan_id"
    )
    entitlement_grants: Mapped[list["EntitlementGrant"]] = relationship(
        "EntitlementGrant", back_populates="plan"
    )
    promo_codes: Mapped[list["PromoCode"]] = relationship(
        "PromoCode", back_populates="plan"
    )
