"""Project CRUD tests."""

import pytest


@pytest.mark.asyncio
async def test_list_projects_empty(auth_client):
    """List projects when user has none."""
    resp = await auth_client.get("/api/v1/projects")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_project(auth_client):
    """Create a project."""
    resp = await auth_client.post("/api/v1/projects", json={"name": "My Novel"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Novel"
    assert "id" in data
    assert "user_id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_project_requires_auth(anon_client):
    """Create project without auth returns 401."""
    resp = await anon_client.post("/api/v1/projects", json={"name": "My Novel"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_projects_after_create(auth_client):
    """List projects returns created project."""
    create_resp = await auth_client.post("/api/v1/projects", json={"name": "Book One"})
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    list_resp = await auth_client.get("/api/v1/projects")
    assert list_resp.status_code == 200
    projects = list_resp.json()
    assert len(projects) == 1
    assert projects[0]["id"] == project_id
    assert projects[0]["name"] == "Book One"


@pytest.mark.asyncio
async def test_get_project(auth_client):
    """Get project by ID."""
    create_resp = await auth_client.post("/api/v1/projects", json={"name": "Get Me"})
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    resp = await auth_client.get(f"/api/v1/projects/{project_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get Me"
    assert resp.json()["id"] == project_id


@pytest.mark.asyncio
async def test_get_project_404(auth_client):
    """Get non-existent project returns 404."""
    resp = await auth_client.get(
        "/api/v1/projects/00000000-0000-0000-0000-000000000001"
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_project(auth_client):
    """Update project name."""
    create_resp = await auth_client.post("/api/v1/projects", json={"name": "Original"})
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    resp = await auth_client.patch(
        f"/api/v1/projects/{project_id}",
        json={"name": "Updated Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Name"

    get_resp = await auth_client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.json()["name"] == "Updated Name"


@pytest.mark.asyncio
async def test_delete_project(auth_client):
    """Delete project."""
    create_resp = await auth_client.post("/api/v1/projects", json={"name": "To Delete"})
    assert create_resp.status_code == 201
    project_id = create_resp.json()["id"]

    resp = await auth_client.delete(f"/api/v1/projects/{project_id}")
    assert resp.status_code == 204

    get_resp = await auth_client.get(f"/api/v1/projects/{project_id}")
    assert get_resp.status_code == 404
