"""Fiction and nonfiction workspace API integration tests."""

import pytest


@pytest.fixture
async def fiction_book(auth_client):
    """Create project and fiction book."""
    proj = await auth_client.post("/api/v1/projects", json={"name": "Fiction Project"})
    assert proj.status_code == 201
    project_id = proj.json()["id"]
    book = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "My Novel", "type": "fiction"},
    )
    assert book.status_code == 201
    return project_id, book.json()["id"]


@pytest.fixture
async def nonfiction_book(auth_client):
    """Create project and nonfiction book."""
    proj = await auth_client.post("/api/v1/projects", json={"name": "Nonfiction Project"})
    assert proj.status_code == 201
    project_id = proj.json()["id"]
    book = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "My Guide", "type": "nonfiction"},
    )
    assert book.status_code == 201
    return project_id, book.json()["id"]


@pytest.mark.asyncio
async def test_fiction_workspace_get_or_create(auth_client, fiction_book):
    """Get fiction workspace returns 200."""
    project_id, book_id = fiction_book
    resp = await auth_client.get(f"/api/v1/projects/{project_id}/books/{book_id}/fiction/workspace")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["book_id"] == book_id


@pytest.mark.asyncio
async def test_nonfiction_workspace_get_or_create(auth_client, nonfiction_book):
    """Get nonfiction workspace returns 200."""
    project_id, book_id = nonfiction_book
    resp = await auth_client.get(f"/api/v1/projects/{project_id}/books/{book_id}/nonfiction/workspace")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["book_id"] == book_id


@pytest.mark.asyncio
async def test_fiction_requires_auth(anon_client, fiction_book):
    """Fiction workspace requires auth."""
    project_id, book_id = fiction_book
    resp = await anon_client.get(f"/api/v1/projects/{project_id}/books/{book_id}/fiction/workspace")
    assert resp.status_code == 401
