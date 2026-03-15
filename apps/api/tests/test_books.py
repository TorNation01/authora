"""Book and chapter CRUD tests."""

import pytest


@pytest.fixture
async def project_id(auth_client):
    """Create a project and return its ID."""
    resp = await auth_client.post("/api/v1/projects", json={"name": "Test Project"})
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_list_books_empty(auth_client, project_id):
    """List books when project has none."""
    resp = await auth_client.get(f"/api/v1/projects/{project_id}/books")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_book(auth_client, project_id):
    """Create a book."""
    resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "My Book", "type": "fiction"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Book"
    assert data["type"] == "fiction"
    assert data["project_id"] == project_id
    assert "id" in data


@pytest.mark.asyncio
async def test_create_book_requires_auth(auth_client, anon_client):
    """Create book without auth returns 401."""
    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Test"})
    project_id = proj_resp.json()["id"]
    resp = await anon_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "My Book"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_book_with_chapters(auth_client, project_id):
    """Get book with chapters."""
    create_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Book With Chapters", "type": "fiction"},
    )
    assert create_resp.status_code == 201
    book_id = create_resp.json()["id"]

    resp = await auth_client.get(f"/api/v1/projects/{project_id}/books/{book_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Book With Chapters"
    assert "chapters" in data
    assert data["chapters"] == []


@pytest.mark.asyncio
async def test_create_chapter(auth_client, project_id):
    """Create a chapter."""
    book_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Chapter Book", "type": "fiction"},
    )
    book_id = book_resp.json()["id"]

    resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books/{book_id}/chapters",
        json={
            "title": "Chapter 1",
            "sort_order": 0,
            "content": {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello"}]}]},
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Chapter 1"
    assert data["sort_order"] == 0
    assert data["word_count"] >= 0
    assert "id" in data


@pytest.mark.asyncio
async def test_update_chapter(auth_client, project_id):
    """Update chapter title."""
    book_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Update Book", "type": "fiction"},
    )
    book_id = book_resp.json()["id"]
    ch_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books/{book_id}/chapters",
        json={"title": "Old Title", "sort_order": 0, "content": {}},
    )
    chapter_id = ch_resp.json()["id"]

    resp = await auth_client.patch(
        f"/api/v1/projects/{project_id}/books/{book_id}/chapters/{chapter_id}",
        json={"title": "New Title"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"


@pytest.mark.asyncio
async def test_delete_chapter(auth_client, project_id):
    """Delete chapter."""
    book_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Delete Book", "type": "fiction"},
    )
    book_id = book_resp.json()["id"]
    ch_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books/{book_id}/chapters",
        json={"title": "To Delete", "sort_order": 0, "content": {}},
    )
    chapter_id = ch_resp.json()["id"]

    resp = await auth_client.delete(
        f"/api/v1/projects/{project_id}/books/{book_id}/chapters/{chapter_id}"
    )
    assert resp.status_code == 204

    get_resp = await auth_client.get(
        f"/api/v1/projects/{project_id}/books/{book_id}"
    )
    chapters = get_resp.json()["chapters"]
    assert len(chapters) == 0


@pytest.mark.asyncio
async def test_update_book(auth_client, project_id):
    """Update book title."""
    create_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Original Title", "type": "fiction"},
    )
    book_id = create_resp.json()["id"]

    resp = await auth_client.patch(
        f"/api/v1/projects/{project_id}/books/{book_id}",
        json={"title": "Updated Title"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_delete_book(auth_client, project_id):
    """Delete book."""
    create_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "To Delete", "type": "fiction"},
    )
    book_id = create_resp.json()["id"]

    resp = await auth_client.delete(
        f"/api/v1/projects/{project_id}/books/{book_id}"
    )
    assert resp.status_code == 204

    list_resp = await auth_client.get(f"/api/v1/projects/{project_id}/books")
    assert len(list_resp.json()) == 0
