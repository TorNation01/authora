"""Funnel instrumentation: visit -> signup -> first book -> first chapter -> paid.

The top of the funnel was never recorded — analytics_events held only
authenticated product events — so the drop between a stranger arriving and an
account existing was invisible. These tests pin the two new ends of the
funnel: the anonymous page-view beacon and the single ladder endpoint.
"""

import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from authora.models import AnalyticsEvent


def fresh_ip() -> dict[str, str]:
    """A client identity with its own rate-limit bucket.

    The rest of the suite shares 127.0.0.1, and the per-IP limiter is real:
    spending its budget here makes unrelated tests fail with 429. Every request
    in this module gets its own bucket instead.
    """
    return {"cf-connecting-ip": f"198.51.100.{uuid.uuid4().int % 200 + 10}"}


@pytest.mark.asyncio
async def test_visit_beacon_records_anonymous_page_view(anon_client: AsyncClient, db):
    visitor = f"t{uuid.uuid4().hex[:12]}"
    res = await anon_client.post(
        "/api/v1/analytics/visit",
        json={
            "path": "/pricing",
            "referrer": "https://www.google.com/",
            "visitor_id": visitor,
            "utm_source": "google",
            "utm_campaign": "launch",
        },
        headers={
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/131.0",
            **fresh_ip(),
        },
    )
    assert res.status_code in (200, 202), res.text

    row = (
        await db.execute(
            select(AnalyticsEvent).where(
                AnalyticsEvent.event_type == "page_view",
                AnalyticsEvent.properties["visitor_id"].astext == visitor,
            )
        )
    ).scalars().first()
    assert row is not None, "page_view event was not written"
    assert row.user_id is None, "an anonymous visit must not be attached to a user"
    assert row.properties["path"] == "/pricing"
    assert row.properties["utm_source"] == "google"


@pytest.mark.asyncio
async def test_visit_beacon_drops_crawlers(anon_client: AsyncClient, db):
    visitor = f"bot{uuid.uuid4().hex[:12]}"
    res = await anon_client.post(
        "/api/v1/analytics/visit",
        json={"path": "/", "visitor_id": visitor},
        headers={
            "user-agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            **fresh_ip(),
        },
    )
    assert res.status_code in (200, 202, 204), res.text

    row = (
        await db.execute(
            select(AnalyticsEvent.id).where(
                AnalyticsEvent.event_type == "page_view",
                AnalyticsEvent.properties["visitor_id"].astext == visitor,
            )
        )
    ).scalars().first()
    assert row is None, "a crawler must not be counted as a visitor"


@pytest.mark.asyncio
async def test_visit_beacon_rejects_oversized_path(anon_client: AsyncClient):
    res = await anon_client.post(
        "/api/v1/analytics/visit",
        json={"path": "/" + "a" * 2000, "visitor_id": "x" * 10},
        headers=fresh_ip(),
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_funnel_ladder_reports_every_stage(admin_client: AsyncClient):
    res = await admin_client.get("/api/v1/admin/funnel/ladder", params={"days": 30}, headers=fresh_ip())
    assert res.status_code == 200, res.text
    body = res.json()
    stages = {s["key"]: s for s in body["stages"]}
    assert list(stages) == ["visit", "signup", "first_book", "first_chapter", "paid"]
    for stage in body["stages"]:
        assert isinstance(stage["count"], int)
    # Visits are cookie-scoped and only exist from the day the beacon shipped,
    # so they are not yet >= signups inside a 30-day window. What must hold is
    # that a visit recorded above is counted here, and that the ladder is a
    # complete ladder: stage 1 has no inbound conversion, every other stage does.
    assert stages["visit"]["count"] >= 1, "the beacon write in the previous test must show up"
    assert stages["visit"]["conversion_pct"] is None
    for stage in body["stages"][1:]:
        # None means the stage above it had nobody in the window — an honest
        # blank, not a fabricated 0%.
        assert stage["conversion_pct"] is None or stage["conversion_pct"] >= 0
    assert body["page_views"] >= stages["visit"]["count"]


@pytest.mark.asyncio
async def test_funnel_ladder_is_admin_only(client: AsyncClient):
    res = await client.get("/api/v1/admin/funnel/ladder", headers=fresh_ip())
    assert res.status_code in (401, 403)


@pytest.mark.asyncio
async def test_signup_records_attributed_signup_event(anon_client: AsyncClient, db, monkeypatch):
    # Registration is gated by Turnstile and invite codes in production. This
    # test is about the event the handler writes, so the gates are switched off
    # rather than fought with — a 503 from an unreachable Cloudflare says
    # nothing about funnel instrumentation.
    from authora.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("TURNSTILE_SECRET_KEY", "")
    monkeypatch.setenv("SIGNUP_INVITE_CODES", "")
    get_settings.cache_clear()

    # The rest of the suite hammers /auth/register from 127.0.0.1, so that IP's
    # bucket is spent. Give this one request its own client identity instead of
    # clearing a limiter that is doing its job.
    unique_ip = fresh_ip()["cf-connecting-ip"]

    visitor = f"s{uuid.uuid4().hex[:12]}"
    email = f"funnel-{uuid.uuid4().hex[:8]}@example.com"
    res = await anon_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", "visitor_id": visitor},
        headers={"cf-connecting-ip": unique_ip},
    )
    assert res.status_code == 200, res.text

    row = (
        await db.execute(
            select(AnalyticsEvent).where(
                AnalyticsEvent.event_type == "signup_completed",
                AnalyticsEvent.properties["visitor_id"].astext == visitor,
            )
        )
    ).scalars().first()
    assert row is not None, "signup_completed event did not carry the visit id"

    await anon_client.post("/api/v1/auth/logout")
    from authora.models import User

    created = (await db.execute(select(User).where(User.email == email))).scalars().first()
    if created is not None:
        await db.delete(created)
        await db.flush()
    get_settings.cache_clear()
