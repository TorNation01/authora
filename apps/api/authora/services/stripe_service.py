"""Stripe service - checkout, customer portal, webhook handling.

Stripe-ready abstraction. When STRIPE_SECRET_KEY is not set, all operations
return None or raise with clear messages. Product/price IDs are stored on Plan.
"""

import uuid as uuid_module
from datetime import datetime, timedelta, timezone
from uuid import UUID

import stripe
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models import Plan, StripeWebhookEvent, Subscription, User


def _stripe_available() -> bool:
    s = get_settings()
    return bool(getattr(s, "stripe_secret_key", None))


def get_stripe_publishable_key() -> str | None:
    """Return publishable key for frontend, or None if Stripe not configured."""
    s = get_settings()
    return getattr(s, "stripe_publishable_key", None)


async def create_checkout_session(
    db: AsyncSession,
    user_id: UUID,
    plan_slug: str,
    billing_interval: str,
    *,
    success_url: str | None = None,
    cancel_url: str | None = None,
    promo_code: str | None = None,
) -> dict | None:
    """
    Create Stripe Checkout Session for subscription or one-time.
    billing_interval: monthly | yearly | lifetime
    Returns { "url": "...", "session_id": "..." } or None if Stripe not configured.
    """
    if not _stripe_available():
        return None

    stripe.api_key = get_settings().stripe_secret_key
    s = get_settings()

    r = await db.execute(
        select(Plan).where(Plan.slug == plan_slug)
    )
    plan = r.scalar_one_or_none()
    if not plan:
        return None

    price_id = None
    if billing_interval == "monthly":
        price_id = getattr(plan, "stripe_price_id_monthly", None) or getattr(plan, "stripe_price_id", None)
    elif billing_interval == "yearly":
        price_id = getattr(plan, "stripe_price_id_yearly", None)
    elif billing_interval == "lifetime":
        price_id = getattr(plan, "stripe_price_id_lifetime", None)

    if not price_id:
        return None

    r2 = await db.execute(select(User).where(User.id == user_id))
    user = r2.scalar_one_or_none()
    if not user:
        return None

    customer_id = None
    # Look up existing Stripe customer from subscription
    r3 = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id)
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    sub = r3.scalar_one_or_none()
    if sub and sub.stripe_customer_id:
        customer_id = sub.stripe_customer_id

    success = success_url or s.stripe_success_url
    cancel = cancel_url or s.stripe_cancel_url

    mode = "subscription" if billing_interval in ("monthly", "yearly") else "payment"
    params = {
        "mode": mode,
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": success,
        "cancel_url": cancel,
        "metadata": {
            "user_id": str(user_id),
            "plan_slug": plan_slug,
            "billing_interval": billing_interval,
        },
    }
    if customer_id:
        params["customer"] = customer_id
    else:
        params["customer_email"] = user.email

    if promo_code and mode == "subscription":
        params["discounts"] = [{"promotion_code": promo_code}]

    session = stripe.checkout.Session.create(**params)
    return {"url": session.url, "session_id": session.id}


async def create_customer_portal_session(
    db: AsyncSession,
    user_id: UUID,
    *,
    return_url: str | None = None,
) -> dict | None:
    """
    Create Stripe Customer Portal session for managing subscription.
    Returns { "url": "..." } or None.
    """
    if not _stripe_available():
        return None

    stripe.api_key = get_settings().stripe_secret_key
    s = get_settings()

    r = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == user_id, Subscription.stripe_customer_id.isnot(None))
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    sub = r.scalar_one_or_none()
    if not sub or not sub.stripe_customer_id:
        return None

    session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=return_url or s.stripe_success_url,
    )
    return {"url": session.url}


def _get_webhook_secret() -> str | None:
    """Resolve webhook secret: STRIPE_WEBHOOK_SECRET, or test/live variant based on key prefix."""
    s = get_settings()
    if s.stripe_webhook_secret:
        return s.stripe_webhook_secret
    # Infer live vs test from secret key prefix
    key = s.stripe_secret_key or ""
    if key.startswith("sk_live_"):
        return s.stripe_webhook_secret_live
    if key.startswith("sk_test_"):
        return s.stripe_webhook_secret_test
    return s.stripe_webhook_secret_live or s.stripe_webhook_secret_test


def is_stripe_live_mode() -> bool:
    """True if using live Stripe keys (sk_live_, pk_live_)."""
    s = get_settings()
    if s.stripe_live_mode is not None:
        return s.stripe_live_mode
    key = s.stripe_secret_key or ""
    return key.startswith("sk_live_")


async def handle_webhook(db: AsyncSession, payload: bytes, sig_header: str) -> dict | None:
    """
    Handle Stripe webhook. Verify signature, ensure idempotency, and process events.
    Returns {"handled": True} or error dict. Caller should return 200 on success.
    """
    if not _stripe_available():
        return {"error": "Stripe not configured"}

    stripe.api_key = get_settings().stripe_secret_key
    webhook_secret = _get_webhook_secret()
    if not webhook_secret:
        return {"error": "STRIPE_WEBHOOK_SECRET not set (or STRIPE_WEBHOOK_SECRET_TEST/LIVE for test/live keys)"}

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return {"error": "Invalid payload"}
    except stripe.SignatureVerificationError:
        return {"error": "Invalid signature"}

    event_id = event.get("id", "")
    event_type = event.get("type", "")

    # Idempotency: skip if already processed
    r = await db.execute(
        select(StripeWebhookEvent).where(StripeWebhookEvent.stripe_event_id == event_id)
    )
    if r.scalar_one_or_none():
        return {"handled": True, "type": event_type, "idempotent": True}

    # Process event
    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(db, event)
        elif event_type in ("customer.subscription.created", "customer.subscription.updated"):
            await _handle_subscription_created_or_updated(db, event)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(db, event)
        elif event_type == "invoice.payment_failed":
            await _handle_invoice_payment_failed(db, event)
        elif event_type == "invoice.paid":
            await _handle_invoice_paid(db, event)
    except Exception:
        await db.rollback()
        raise

    # Record processed event
    db.add(
        StripeWebhookEvent(
            id=uuid_module.uuid4(),
            stripe_event_id=event_id,
            event_type=event_type,
        )
    )
    await db.flush()
    return {"handled": True, "type": event_type}


async def _handle_checkout_completed(db: AsyncSession, event: dict) -> None:
    """Create or update subscription from checkout.session.completed."""
    session = event.get("data", {}).get("object", {})
    metadata = session.get("metadata", {}) or {}
    user_id_str = metadata.get("user_id")
    plan_slug = metadata.get("plan_slug")
    billing_interval = metadata.get("billing_interval", "monthly")

    if not user_id_str or not plan_slug:
        return

    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        return

    r = await db.execute(select(Plan).where(Plan.slug == plan_slug))
    plan = r.scalar_one_or_none()
    if not plan:
        return

    customer_id = session.get("customer") or session.get("customer_email")
    if isinstance(customer_id, str) and not customer_id.startswith("cus_"):
        customer_id = None  # customer_email is not a customer id

    mode = session.get("mode", "subscription")
    subscription_id = session.get("subscription")

    if mode == "subscription" and subscription_id:
        # Fetch full subscription from Stripe for period dates
        try:
            sub_obj = stripe.Subscription.retrieve(subscription_id)
            period_start = datetime.fromtimestamp(sub_obj["current_period_start"], tz=timezone.utc)
            period_end = datetime.fromtimestamp(sub_obj["current_period_end"], tz=timezone.utc)
            cancel_at_period_end = sub_obj.get("cancel_at_period_end", False)
            status = sub_obj.get("status", "active")
        except Exception:
            period_start = datetime.now(timezone.utc)
            period_end = period_start + timedelta(days=30 if billing_interval == "monthly" else 365)
            cancel_at_period_end = False
            status = "active"

        # Upsert by stripe_subscription_id
        r2 = await db.execute(
            select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
        )
        sub = r2.scalar_one_or_none()
        if sub:
            sub.period_start = period_start
            sub.period_end = period_end
            sub.cancel_at_period_end = cancel_at_period_end
            sub.status = status
            sub.billing_interval = billing_interval
            if sub.stripe_customer_id is None and customer_id:
                sub.stripe_customer_id = customer_id
        else:
            sub = Subscription(
                user_id=user_id,
                plan_id=plan.id,
                status=status,
                stripe_customer_id=customer_id,
                stripe_subscription_id=subscription_id,
                period_start=period_start,
                period_end=period_end,
                cancel_at_period_end=cancel_at_period_end,
                billing_interval=billing_interval,
                is_lifetime=False,
            )
            db.add(sub)
    else:
        # One-time payment (lifetime)
        r2 = await db.execute(
            select(Subscription)
            .where(Subscription.user_id == user_id, Subscription.plan_id == plan.id)
            .order_by(Subscription.created_at.desc())
            .limit(1)
        )
        existing = r2.scalar_one_or_none()
        if existing and existing.is_lifetime:
            return  # Already have lifetime
        sub = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status="active",
            stripe_customer_id=customer_id if isinstance(customer_id, str) and customer_id.startswith("cus_") else None,
            stripe_subscription_id=None,
            period_start=datetime.now(timezone.utc),
            period_end=None,
            billing_interval="lifetime",
            is_lifetime=True,
        )
        db.add(sub)
        await db.flush()
        if get_settings().feature_affiliate:
            from authora.services.affiliate_service import record_conversion_on_payment
            revenue_cents = plan.price_lifetime_cents or 0
            if revenue_cents > 0:
                await record_conversion_on_payment(
                    db, user_id, sub.id, revenue_cents, is_recurring=False
                )


async def _handle_subscription_created_or_updated(db: AsyncSession, event: dict) -> None:
    """Sync subscription from Stripe customer.subscription.*."""
    sub_obj = event.get("data", {}).get("object", {})
    subscription_id = sub_obj.get("id")
    if not subscription_id:
        return

    customer_id = sub_obj.get("customer")
    if isinstance(customer_id, dict):
        customer_id = customer_id.get("id")
    status = sub_obj.get("status", "active")
    cancel_at_period_end = sub_obj.get("cancel_at_period_end", False)
    period_start = datetime.fromtimestamp(sub_obj["current_period_start"], tz=timezone.utc)
    period_end = datetime.fromtimestamp(sub_obj["current_period_end"], tz=timezone.utc)

    # Resolve plan from price
    items = sub_obj.get("items", {}).get("data", [])
    price_id = items[0].get("price", {}).get("id") if items else None
    if not price_id:
        return

    r = await db.execute(
        select(Plan).where(
            (Plan.stripe_price_id_monthly == price_id)
            | (Plan.stripe_price_id_yearly == price_id)
            | (Plan.stripe_price_id == price_id)
        )
    )
    plan = r.scalar_one_or_none()
    if not plan:
        return

    # Resolve user from customer
    r2 = await db.execute(
        select(Subscription).where(Subscription.stripe_customer_id == customer_id).limit(1)
    )
    existing_sub = r2.scalar_one_or_none()
    if existing_sub:
        user_id = existing_sub.user_id
    else:
        return  # No user linked to this customer yet; checkout.session.completed will create

    r3 = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    sub = r3.scalar_one_or_none()
    recurring = items[0].get("price", {}).get("recurring", {}) if items else {}
    interval = recurring.get("interval", "month")
    billing_interval = "yearly" if interval == "year" else "monthly"

    if sub:
        sub.plan_id = plan.id
        sub.status = status
        sub.period_start = period_start
        sub.period_end = period_end
        sub.cancel_at_period_end = cancel_at_period_end
        sub.billing_interval = billing_interval
    else:
        sub = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            status=status,
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            period_start=period_start,
            period_end=period_end,
            cancel_at_period_end=cancel_at_period_end,
            billing_interval=billing_interval,
            is_lifetime=False,
        )
        db.add(sub)


async def _handle_subscription_deleted(db: AsyncSession, event: dict) -> None:
    """Mark subscription as canceled."""
    sub_obj = event.get("data", {}).get("object", {})
    subscription_id = sub_obj.get("id")
    if not subscription_id:
        return

    r = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    sub = r.scalar_one_or_none()
    if sub:
        sub.status = "canceled"
        # Keep period_end so user retains access until end of period
        if not sub.period_end and sub_obj.get("current_period_end"):
            sub.period_end = datetime.fromtimestamp(sub_obj["current_period_end"], tz=timezone.utc)


def _get_subscription_id(invoice: dict) -> str | None:
    """Extract subscription ID from invoice (may be string or expanded object)."""
    sub = invoice.get("subscription")
    if isinstance(sub, str):
        return sub
    if isinstance(sub, dict):
        return sub.get("id")
    return None


async def _handle_invoice_payment_failed(db: AsyncSession, event: dict) -> None:
    """Set grace period on subscription when payment fails."""
    invoice = event.get("data", {}).get("object", {})
    subscription_id = _get_subscription_id(invoice)
    if not subscription_id:
        return

    r = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    sub = r.scalar_one_or_none()
    if not sub:
        return

    # Grace period: 7 days from period_end (or now if period_end in past)
    now = datetime.now(timezone.utc)
    period_end = sub.period_end or now
    if period_end < now:
        period_end = now
    grace_end = period_end + timedelta(days=7)
    sub.grace_period_end = grace_end
    sub.status = "past_due"  # Retain access during grace period


async def _handle_invoice_paid(db: AsyncSession, event: dict) -> None:
    """Clear grace period when payment succeeds. Record affiliate conversion."""
    invoice = event.get("data", {}).get("object", {})
    subscription_id = _get_subscription_id(invoice)
    if not subscription_id:
        return

    r = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == subscription_id)
    )
    sub = r.scalar_one_or_none()
    if sub:
        sub.grace_period_end = None
        sub.status = "active"

        if get_settings().feature_affiliate:
            from authora.services.affiliate_service import record_conversion_on_payment
            amount_paid = invoice.get("amount_paid", 0) or 0
            if amount_paid > 0:
                await record_conversion_on_payment(
                    db, sub.user_id, sub.id, amount_paid, is_recurring=True
                )
