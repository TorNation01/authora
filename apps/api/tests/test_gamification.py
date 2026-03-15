"""Gamification API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_gamification_stats_require_auth(client: AsyncClient):
    """Stats require authentication."""
    res = await client.get("/api/v1/gamification/stats")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_gamification_stats(auth_client: AsyncClient):
    """Get user stats."""
    res = await auth_client.get("/api/v1/gamification/stats")
    assert res.status_code == 200
    data = res.json()
    assert "total_words" in data or "xp" in data or "level" in data


@pytest.mark.asyncio
async def test_gamification_achievements(auth_client: AsyncClient):
    """Get achievements."""
    res = await auth_client.get("/api/v1/gamification/achievements")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
