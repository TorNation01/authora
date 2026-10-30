"""Open signup + Cloudflare Turnstile bot protection.

Covers the transition the beta gate makes when it lifts: with no invite codes
configured signup is open, and Turnstile is the thing standing between a bot
and an account.

Both branches are proved against Cloudflare's real siteverify endpoint using
its documented dummy keys (https://developers.cloudflare.com/turnstile/troubleshooting/testing/):

    1x0000000000000000000000000000000AA  -> always passes
    2x0000000000000000000000000000000AA  -> always blocks
"""

import uuid

import pytest
from sqlalchemy import select

from authora.config import get_settings
from authora.models import User

PASS_SECRET = "1x0000000000000000000000000000000AA"
BLOCK_SECRET = "2x0000000000000000000000000000000AA"
DUMMY_SITE_KEY = "1x00000000000000000000AA"


@pytest.fixture(autouse=True)
async def clear_auth_rate_limit():
    """The auth bucket is 5 attempts per window and shared across the suite.

    Several assertions here need more than five credential posts from the same
    client IP, so start every test with an empty bucket.
    """
    from authora.middleware import security as sec

    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url("redis://localhost:6379/1")
        async for key in client.scan_iter("ratelimit:*"):
            await client.delete(key)
        await client.aclose()
    except Exception:
        pass
    sec._rate_limit_store.clear()
    yield


@pytest.fixture
def signup_mode(monkeypatch):
    """Put the API in a chosen signup mode for one test."""

    def _apply(invite_codes: str = "", secret: str = ""):
        monkeypatch.setenv("SIGNUP_INVITE_CODES", invite_codes)
        monkeypatch.setenv("TURNSTILE_SECRET_KEY", secret)
        monkeypatch.setenv("TURNSTILE_SITE_KEY", DUMMY_SITE_KEY)
        get_settings.cache_clear()

    yield _apply
    get_settings.cache_clear()


def _email() -> str:
    return f"probe-turnstile-{uuid.uuid4().hex[:10]}@example.com"


async def _register(client, email: str, **extra):
    return await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "password123", **extra},
    )


@pytest.mark.asyncio
async def test_open_signup_without_bot_token_is_rejected(client, signup_mode):
    """Gate lifted, no Turnstile token: no account."""
    signup_mode(invite_codes="", secret=BLOCK_SECRET)
    res = await _register(client, _email())
    assert res.status_code == 403, res.text
    assert "verification" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_open_signup_with_forged_bot_token_is_rejected(client, signup_mode):
    """A made-up token fails at Cloudflare, not just in our client."""
    signup_mode(invite_codes="", secret=BLOCK_SECRET)
    res = await _register(client, _email(), turnstile_token="forged-token")
    assert res.status_code == 403, res.text


@pytest.mark.asyncio
async def test_open_signup_with_valid_bot_token_creates_account(client, signup_mode, db):
    """A solved challenge lets a stranger in."""
    signup_mode(invite_codes="", secret=PASS_SECRET)
    email = _email()
    res = await _register(client, email, turnstile_token="XXXX.DUMMY.TOKEN.XXXX")
    assert res.status_code == 200, res.text
    assert "access_token" in res.json()
    row = await db.execute(select(User).where(User.email == email))
    assert row.scalar_one_or_none() is not None


@pytest.mark.asyncio
async def test_closed_gate_still_requires_invite_code(client, signup_mode):
    """Bot protection does not replace the invite gate while beta is closed."""
    signup_mode(invite_codes="AUTHORA-TEST-CODE", secret=PASS_SECRET)
    res = await _register(client, _email(), turnstile_token="XXXX.DUMMY.TOKEN.XXXX")
    assert res.status_code == 403, res.text
    assert "invite" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_signup_config_tells_the_app_what_to_render(client, signup_mode):
    """The page must not have to guess whether to show a code or a widget."""
    signup_mode(invite_codes="", secret=PASS_SECRET)
    res = await client.get("/api/v1/auth/signup-config")
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["invite_required"] is False
    assert body["turnstile"]["enabled"] is True
    assert body["turnstile"]["site_key"] == DUMMY_SITE_KEY

    signup_mode(invite_codes="AUTHORA-TEST-CODE", secret="")
    res = await client.get("/api/v1/auth/signup-config")
    body = res.json()
    assert body["invite_required"] is True
    assert body["turnstile"]["enabled"] is False
