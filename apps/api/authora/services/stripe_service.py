"""Stripe service - checkout, customer portal, webhook handling.

Stripe-ready abstraction. When STRIPE_SECRET_KEY is not set, all operations
return None or raise with clear messages. Product/price IDs are stored on Plan.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models import Plan, Subscription, User


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

    import stripe
    from sqlalchemy import select

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

    import stripe
    from sqlalchemy import select

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


async def handle_webhook(payload: bytes, sig_header: str) -> dict | None:
    """
    Handle Stripe webhook. Verify signature and dispatch events.
    Returns {"handled": True} or error dict. Caller should return 200 on success.
    Uses STRIPE_WEBHOOK_SECRET, or STRIPE_WEBHOOK_SECRET_TEST/LIVE based on key prefix.
    """
    if not _stripe_available():
        return {"error": "Stripe not configured"}

    import stripe

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

    # Event type handling - implement in caller or extend here
    # customer.subscription.created, updated, deleted
    # invoice.paid, invoice.payment_failed
    # checkout.session.completed
    event_type = event.get("type", "")
    return {"handled": True, "type": event_type}
