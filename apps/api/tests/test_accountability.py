"""Accountability API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_accountability_settings_require_auth(client: AsyncClient):
    """Settings require authentication."""
    res = await client.get("/api/v1/accountability/settings")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_accountability_settings_get(auth_client: AsyncClient):
    """Get accountability settings."""
    res = await auth_client.get("/api/v1/accountability/settings")
    assert res.status_code in (200, 404)
    if res.status_code == 200:
        data = res.json()
        assert "daily_word_goal" in data or "settings" in data


@pytest.mark.asyncio
async def test_accountability_settings_update(auth_client: AsyncClient):
    """Update accountability settings."""
    res = await auth_client.patch(
        "/api/v1/accountability/settings",
        json={"daily_word_goal": 500, "reminder_enabled": True},
    )
    assert res.status_code in (200, 201)


@pytest.mark.asyncio
async def test_accountability_settings_invalid_type(auth_client: AsyncClient):
    """Invalid type rejected."""
    res = await auth_client.patch(
        "/api/v1/accountability/settings",
        json={"daily_word_goal": "not_a_number"},
    )
    assert res.status_code == 422
