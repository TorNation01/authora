"""Notes API integration tests."""

import pytest


@pytest.fixture
async def project_and_book(auth_client):
    """Create project and book, return (project_id, book_id)."""
    proj = await auth_client.post("/api/v1/projects", json={"name": "Notes Project"})
    assert proj.status_code == 201
    project_id = proj.json()["id"]
    book = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Notes Book", "type": "fiction"},
    )
    assert book.status_code == 201
    book_id = book.json()["id"]
    return project_id, book_id


@pytest.mark.asyncio
async def test_list_project_notes_empty(auth_client, project_and_book):
    """List notes when project has none."""
    project_id, _ = project_and_book
    resp = await auth_client.get(f"/api/v1/projects/{project_id}/notes")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_project_note(auth_client, project_and_book):
    """Create a project note."""
    project_id, book_id = project_and_book
    resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/notes",
        json={
            "title": "My note",
            "content": "Note content",
            "note_type": "general",
            "book_id": book_id,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["note_type"] == "general"
    assert data["book_id"] == book_id


@pytest.mark.asyncio
async def test_create_note_requires_auth(anon_client):
    """Create note without auth returns 401."""
    resp = await anon_client.post(
        "/api/v1/projects/00000000-0000-0000-0000-000000000001/notes",
        json={"title": "Test", "content": "", "note_type": "general"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_search_notes(auth_client, project_and_book):
    """Search notes returns 200."""
    project_id, book_id = project_and_book
    await auth_client.post(
        f"/api/v1/projects/{project_id}/notes",
        json={"title": "Searchable note", "content": "content", "note_type": "general", "book_id": book_id},
    )
    resp = await auth_client.get(f"/api/v1/projects/{project_id}/notes?q=note")
    assert resp.status_code == 200
