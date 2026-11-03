"""Email verification, password policy and the signup domain throttle."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models.user import User
from authora.services.email_verification import issue_verification

GOOD_PASSWORD = "a-long-enough-secret-9"


@pytest.mark.asyncio
async def test_register_creates_unverified_account_with_token(client: AsyncClient, db: AsyncSession):
    res = await client.post(
        "/api/v1/auth/register",
        json={"email": "unverified@mailbox.test", "password": GOOD_PASSWORD},
    )
    assert res.status_code == 200, res.text

    user = (
        await db.execute(select(User).where(User.email == "unverified@mailbox.test"))
    ).scalar_one()
    assert user.email_verified is False
    assert user.email_verification_token_hash, "a token must be armed at signup"
    assert len(user.email_verification_token_hash) == 64


@pytest.mark.asyncio
async def test_verification_link_marks_account_once(client: AsyncClient, db: AsyncSession):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "confirm-me@mailbox.test", "password": GOOD_PASSWORD},
    )
    user = (
        await db.execute(select(User).where(User.email == "confirm-me@mailbox.test"))
    ).scalar_one()

    token = await issue_verification(db, user, force=True)
    assert token

    first = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert first.status_code == 200, first.text
    assert first.json()["verified"] is True

    await db.refresh(user)
    assert user.email_verified is True
    assert user.email_verification_token_hash is None

    # Single use: the same link must not work twice.
    second = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert second.status_code == 400


@pytest.mark.asyncio
async def test_checkout_is_closed_until_email_is_confirmed(auth_client: AsyncClient, test_user: User):
    res = await auth_client.post(
        "/api/v1/billing/checkout/create",
        json={"plan_slug": "starter", "billing_interval": "monthly"},
    )
    assert res.status_code == 403
    assert "confirm your email" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_weak_passwords_are_refused(client: AsyncClient):
    short = await client.post(
        "/api/v1/auth/register",
        json={"email": "short@mailbox.test", "password": "short1234"},
    )
    assert short.status_code == 422

    common = await client.post(
        "/api/v1/auth/register",
        json={"email": "common@mailbox.test", "password": "passwordpassword"},
    )
    assert common.status_code == 422

    about_self = await client.post(
        "/api/v1/auth/register",
        json={"email": "aboutself@mailbox.test", "password": "aboutself-is-my-pass"},
    )
    assert about_self.status_code == 422


@pytest.mark.asyncio
async def test_sixth_account_from_one_domain_in_an_hour_is_throttled(
    client: AsyncClient, monkeypatch
):
    from authora.config import get_settings

    monkeypatch.setattr(get_settings(), "signup_domain_limit_per_hour", 5)
    for i in range(5):
        await client.post(
            "/api/v1/auth/register",
            json={"email": f"farm{i}@bulk-domain.test", "password": GOOD_PASSWORD},
        )

    sixth = await client.post(
        "/api/v1/auth/register",
        json={"email": "farm5@bulk-domain.test", "password": GOOD_PASSWORD},
    )
    assert sixth.status_code == 429
