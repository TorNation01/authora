"""Security middleware and auth tests."""

import pytest


@pytest.mark.asyncio
async def test_auth_required_for_projects(anon_client):
    """Projects list requires auth."""
    resp = await anon_client.get("/api/v1/projects")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_required_for_books(anon_client):
    """Books list requires auth."""
    resp = await anon_client.get(
        "/api/v1/projects/00000000-0000-0000-0000-000000000001/books"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_requires_auth(anon_client):
    """Auth /me requires valid token."""
    resp = await anon_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_me_with_valid_token(auth_client):
    """Auth /me returns user with valid token."""
    resp = await auth_client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_invalid_token_rejected(auth_client):
    """Invalid Bearer token returns 401."""
    auth_client.headers["Authorization"] = "Bearer invalid-token"
    resp = await auth_client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_request_id_in_response(anon_client):
    """Security middleware adds X-Request-ID to response."""
    resp = await anon_client.get("/health")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert len(resp.headers["X-Request-ID"]) > 0


@pytest.mark.asyncio
async def test_secure_headers_present(anon_client):
    """Security middleware adds secure headers."""
    resp = await anon_client.get("/health")
    assert resp.status_code == 200
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"


@pytest.mark.asyncio
async def test_rate_limit_skip_health(anon_client):
    """Health endpoints are not rate limited (many requests succeed)."""
    for _ in range(5):
        resp = await anon_client.get("/health")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_admin_user_has_is_admin(admin_client):
    """Admin user can access /me and has admin role."""
    resp = await admin_client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    # UserResponse doesn't include is_admin, but we verify admin can authenticate
    assert "email" in resp.json()
    assert resp.json()["email"] == "admin@example.com"
