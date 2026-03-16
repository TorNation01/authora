"""Permission and access control tests - RBAC, project boundaries, collaboration."""

import uuid

import pytest

from authora.models import Project, User


@pytest.mark.asyncio
async def test_project_access_requires_auth(anon_client):
    """Project list requires auth."""
    resp = await anon_client.get("/api/v1/projects")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_user_cannot_access_other_user_project(auth_client, db, test_user):
    """User cannot access project they don't own or aren't invited to."""
    # Create another user and their project
    from authora.services.auth import hash_password

    other = User(
        email="other@example.com",
        hashed_password=hash_password("otherpass"),
        display_name="Other",
        is_active=True,
    )
    db.add(other)
    await db.flush()
    proj = Project(name="Other Project", user_id=other.id)
    db.add(proj)
    await db.flush()

    # test_user (auth_client) tries to access other's project
    resp = await auth_client.get(f"/api/v1/projects/{proj.id}")
    assert resp.status_code in (403, 404)


@pytest.mark.asyncio
async def test_admin_routes_require_admin(auth_client, admin_client):
    """Admin routes require is_admin."""
    resp = await auth_client.get("/api/v1/admin/users")
    assert resp.status_code == 403

    resp = await admin_client.get("/api/v1/admin/users")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_export_requires_book_access(auth_client, anon_client):
    """Export requires auth and book access."""
    fake_id = str(uuid.uuid4())
    resp = await anon_client.get(f"/api/v1/export/books/{fake_id}/preview")
    assert resp.status_code == 401

    resp = await auth_client.get(f"/api/v1/export/books/{fake_id}/preview")
    assert resp.status_code in (403, 404)
