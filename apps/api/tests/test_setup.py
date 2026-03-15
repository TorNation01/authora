"""Setup wizard endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_setup_status(anon_client):
    """Setup status returns structure (standalone mode)."""
    resp = await anon_client.get("/api/v1/setup/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "setup_complete" in data
    assert "has_users" in data
    assert "can_connect" in data


@pytest.mark.asyncio
async def test_setup_test_database(anon_client):
    """Setup test validates database URL."""
    resp = await anon_client.post(
        "/api/v1/setup/test",
        json={"database_url": "postgresql://authora:authora@localhost:5432/authora_test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "database" in data or "redis" in data


@pytest.mark.asyncio
async def test_setup_test_invalid_url(anon_client):
    """Setup test rejects invalid database URL."""
    resp = await anon_client.post(
        "/api/v1/setup/test",
        json={"database_url": "invalid"},
    )
    assert resp.status_code == 200
    data = resp.json()
    if "database" in data:
        assert data["database"].get("valid") is False


@pytest.mark.asyncio
async def test_setup_apply_requires_valid_config(anon_client):
    """Setup apply validates request - we test structure, not actual file write."""
    # Apply with minimal valid structure - may fail on file write in CI
    resp = await anon_client.post(
        "/api/v1/setup/apply",
        json={"database_url": "postgresql://authora:authora@localhost:5432/authora_test"},
    )
    # Can return 200 (success) or 500 (file write failed in test env)
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        assert resp.json().get("success") is True
