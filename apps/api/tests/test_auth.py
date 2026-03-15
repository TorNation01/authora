"""Auth API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration."""
    res = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "display_name": "Test User",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test login after registration."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    res = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "password123"},
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    """Test /me with valid token."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": "password123"},
    )
    token = reg.json()["access_token"]
    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_preferences_get_empty(client: AsyncClient):
    """Test GET /me/preferences returns empty when none set."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "prefs@example.com", "password": "password123"},
    )
    token = reg.json()["access_token"]
    res = await client.get(
        "/api/v1/auth/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.json()["preferences"] == {}


@pytest.mark.asyncio
async def test_preferences_patch_merge(client: AsyncClient):
    """Test PATCH /me/preferences merges with existing."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "prefs2@example.com", "password": "password123"},
    )
    token = reg.json()["access_token"]
    res = await client.patch(
        "/api/v1/auth/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
        json={"preferences": {"theme": "dark", "font_size": 14}},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["preferences"]["theme"] == "dark"
    assert data["preferences"]["font_size"] == 14
    res2 = await client.patch(
        "/api/v1/auth/me/preferences",
        headers={"Authorization": f"Bearer {token}"},
        json={"preferences": {"font_size": 16, "sidebar": True}},
    )
    assert res2.status_code == 200
    merged = res2.json()["preferences"]
    assert merged["theme"] == "dark"
    assert merged["font_size"] == 16
    assert merged["sidebar"] is True
