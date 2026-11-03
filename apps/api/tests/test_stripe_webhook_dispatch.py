"""Stripe webhook dispatch: event names and route aliases.

The live endpoint (we_1UQTbK..., added by Astra) subscribes to
``invoice.payment_succeeded``, the legacy name Stripe still emits. The handler
matched only ``invoice.paid``, so every renewal verified, returned 200, was
recorded in stripe_webhook_events as processed - and extended nothing. These
tests pin both spellings to the same handler, pin the singular ``/webhook``
path so a dashboard URL without the trailing "s" cannot 404, and keep signature
verification honest.
"""

import hashlib
import hmac
import json
import time

import pytest
from sqlalchemy import select

SECRET = "whsec_test_dispatch"


def _sign(payload: bytes, secret: str = SECRET) -> str:
    timestamp = int(time.time())
    signed = f"{timestamp}.".encode() + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def _payload(event_id: str, event_type: str) -> bytes:
    return json.dumps(
        {
            "id": event_id,
            "type": event_type,
            "data": {"object": {"subscription": "sub_test_1", "customer": "cus_test_1"}},
        }
    ).encode()


@pytest.fixture
def stripe_configured(monkeypatch):
    """Point the service at a known secret without touching the real .env."""
    from authora.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_dispatch", raising=False)
    monkeypatch.setattr(settings, "stripe_webhook_secret", SECRET, raising=False)
    return settings


@pytest.fixture
def invoice_paid_calls(monkeypatch):
    """Record which events reach the invoice-paid handler."""
    calls: list[str] = []

    async def spy(db, event):
        calls.append(event["id"])

    monkeypatch.setattr(
        "authora.services.stripe_service._handle_invoice_paid", spy, raising=True
    )
    return calls


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_type",
    ["invoice.paid", "invoice.payment_succeeded"],
)
async def test_invoice_events_extend_the_subscription(
    client, stripe_configured, invoice_paid_calls, event_type
):
    """Both invoice-paid spellings must reach the handler."""
    payload = _payload(f"evt_{event_type.replace('.', '_')}", event_type)
    resp = await client.post(
        "/api/v1/billing/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": _sign(payload)},
    )
    assert resp.status_code == 200, resp.text
    assert invoice_paid_calls == [f"evt_{event_type.replace('.', '_')}"]


@pytest.mark.asyncio
async def test_singular_webhook_path_is_routed(client, stripe_configured, invoice_paid_calls):
    """The path without the trailing "s" reaches the same verified handler."""
    payload = _payload("evt_singular_path", "invoice.payment_succeeded")
    resp = await client.post(
        "/api/v1/billing/webhook",
        content=payload,
        headers={"stripe-signature": _sign(payload)},
    )
    assert resp.status_code == 200, resp.text
    assert invoice_paid_calls == ["evt_singular_path"]


@pytest.mark.asyncio
async def test_bad_signature_is_still_rejected(client, stripe_configured):
    """Aliasing the path must not weaken signature verification."""
    payload = _payload("evt_bad_sig", "invoice.payment_succeeded")
    resp = await client.post(
        "/api/v1/billing/webhook",
        content=payload,
        headers={"stripe-signature": _sign(payload, secret="whsec_wrong")},
    )
    assert resp.status_code == 400
    assert "signature" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_event_is_recorded_once(client, db, stripe_configured, invoice_paid_calls):
    """A redelivered event is idempotent and does not re-run the handler."""
    from authora.models.stripe_webhook_event import StripeWebhookEvent

    payload = _payload("evt_idempotent", "invoice.payment_succeeded")
    headers = {"stripe-signature": _sign(payload)}

    first = await client.post(
        "/api/v1/billing/webhooks/stripe", content=payload, headers=headers
    )
    assert first.status_code == 200, first.text

    second = await client.post(
        "/api/v1/billing/webhooks/stripe", content=payload, headers=headers
    )
    assert second.status_code == 200
    assert second.json().get("idempotent") is True
    assert invoice_paid_calls == ["evt_idempotent"]

    rows = (
        await db.execute(
            select(StripeWebhookEvent).where(
                StripeWebhookEvent.stripe_event_id == "evt_idempotent"
            )
        )
    ).scalars().all()
    assert len(rows) == 1
