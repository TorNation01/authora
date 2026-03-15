"""Health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_liveness(anon_client):
    """Health liveness returns ok."""
    resp = await anon_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "app" in data


@pytest.mark.asyncio
async def test_health_ready(anon_client):
    """Health readiness returns structure with checks."""
    resp = await anon_client.get("/health/ready")
    # 200 if DB and Redis ok, 503 if degraded
    assert resp.status_code in (200, 503)
    data = resp.json()
    assert "status" in data
    assert data["status"] in ("ready", "degraded")
    assert "checks" in data
    assert "database" in data["checks"]
    assert "redis" in data["checks"]
    assert "app" in data


@pytest.mark.asyncio
async def test_root(anon_client):
    """Root returns app info."""
    resp = await anon_client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "app" in data
    assert "docs" in data
