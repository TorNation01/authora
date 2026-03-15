"""Journey API integration tests."""

import pytest


@pytest.mark.asyncio
async def test_journey_get(auth_client):
    """Get journey returns 200 (may have no journey yet)."""
    resp = await auth_client.get("/api/v1/journey")
    assert resp.status_code == 200
    data = resp.json()
    assert "has_journey" in data


@pytest.mark.asyncio
async def test_journey_onboarding(auth_client):
    """Submit onboarding creates journey."""
    resp = await auth_client.post(
        "/api/v1/journey/onboarding",
        json={
            "book_type": "fiction",
            "writing_mode": "solo",
            "writing_goals": "finish first draft",
            "genre_topic": "thriller",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "journey_id" in data or "current_phase" in data


@pytest.mark.asyncio
async def test_journey_requires_auth(anon_client):
    """Journey requires auth."""
    resp = await anon_client.get("/api/v1/journey")
    assert resp.status_code == 401
