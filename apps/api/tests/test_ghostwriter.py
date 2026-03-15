"""Ghostwriter API integration tests."""

import pytest


@pytest.fixture
async def ghostwriter_book(auth_client):
    """Create project and book for ghostwriter."""
    proj = await auth_client.post("/api/v1/projects", json={"name": "Ghostwriter Project"})
    assert proj.status_code == 201
    project_id = proj.json()["id"]
    book = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Ghostwritten Book", "type": "nonfiction"},
    )
    assert book.status_code == 201
    return project_id, book.json()["id"]


@pytest.mark.asyncio
async def test_ghostwriter_workspace_get(auth_client, ghostwriter_book):
    """Get ghostwriter workspace returns 200."""
    project_id, book_id = ghostwriter_book
    resp = await auth_client.get(f"/api/v1/projects/{project_id}/books/{book_id}/ghostwriter")
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["book_id"] == book_id
    assert "intake" in data or "chapter_briefs" in data or "outline" in data


@pytest.mark.asyncio
async def test_ghostwriter_requires_auth(anon_client):
    """Ghostwriter requires auth."""
    resp = await anon_client.get(
        "/api/v1/projects/00000000-0000-0000-0000-000000000001/books/00000000-0000-0000-0000-000000000002/ghostwriter"
    )
    assert resp.status_code == 401
