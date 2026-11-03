"""Stripe webhook: signature is enforced and a replayed event runs once.

Stripe retries. A webhook that grants a month of access per delivery is a
subscription that never expires; a webhook that trusts unsigned payloads is an
open door to free subscriptions. Both are covered here with real signatures
computed the way Stripe computes them.
"""

import hashlib
import hmac
import json
import time

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.models.stripe_webhook_event import StripeWebhookEvent
from authora.services import stripe_service

SECRET = "whsec_test_only_secret"


def sign(payload: bytes, secret: str = SECRET) -> str:
    timestamp = int(time.time())
    signed = f"{timestamp}.".encode() + payload
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


@pytest.fixture
def stripe_configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test_dummy_for_webhook_test", raising=False)
    monkeypatch.setattr(settings, "stripe_webhook_secret", SECRET, raising=False)
    monkeypatch.setattr(settings, "stripe_webhook_secret_test", SECRET, raising=False)
    return settings


@pytest.mark.asyncio
async def test_unsigned_payload_is_refused(db: AsyncSession, stripe_configured):
    payload = json.dumps(
        {"id": "evt_forged_1", "type": "invoice.paid", "data": {"object": {}}}
    ).encode()

    result = await stripe_service.handle_webhook(db, payload, "t=1,v1=deadbeef")

    assert result and "error" in result
    assert result["error"] == "Invalid signature"


@pytest.mark.asyncio
async def test_replayed_event_is_recorded_once(db: AsyncSession, stripe_configured):
    payload = json.dumps(
        {
            "id": "evt_replay_1",
            "type": "customer.subscription.trial_will_end",
            "data": {"object": {}},
        }
    ).encode()

    first = await stripe_service.handle_webhook(db, payload, sign(payload))
    second = await stripe_service.handle_webhook(db, payload, sign(payload))

    assert first == {"handled": True, "type": "customer.subscription.trial_will_end"}
    assert second and second.get("idempotent") is True

    count = (
        await db.execute(
            select(func.count())
            .select_from(StripeWebhookEvent)
            .where(StripeWebhookEvent.stripe_event_id == "evt_replay_1")
        )
    ).scalar()
    assert count == 1
