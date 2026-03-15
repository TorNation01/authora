"""Export endpoint tests - use mock/minimal content."""

import pytest

# Minimal TipTap content for tests
MOCK_CHAPTER_CONTENT = {
    "type": "doc",
    "content": [
        {"type": "paragraph", "content": [{"type": "text", "text": "Sample chapter text for export."}]}
    ],
}


@pytest.fixture
async def book_with_chapters(auth_client):
    """Create a project and book with chapters for export tests."""
    proj_resp = await auth_client.post("/api/v1/projects", json={"name": "Export Project"})
    assert proj_resp.status_code == 201
    project_id = proj_resp.json()["id"]

    book_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books",
        json={"title": "Export Book", "type": "fiction"},
    )
    assert book_resp.status_code == 201
    book_id = book_resp.json()["id"]

    ch_resp = await auth_client.post(
        f"/api/v1/projects/{project_id}/books/{book_id}/chapters",
        json={
            "title": "Chapter 1",
            "sort_order": 0,
            "content": MOCK_CHAPTER_CONTENT,
        },
    )
    assert ch_resp.status_code == 201

    return {"project_id": project_id, "book_id": book_id}


@pytest.mark.asyncio
async def test_export_preview(auth_client, book_with_chapters):
    """Export preview returns structure."""
    book_id = book_with_chapters["book_id"]
    resp = await auth_client.get(f"/api/v1/export/books/{book_id}/preview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["book_title"] == "Export Book"
    assert data["chapter_count"] == 1
    assert "total_words" in data
    assert len(data["chapters"]) == 1
    assert data["chapters"][0]["title"] == "Chapter 1"


@pytest.mark.asyncio
async def test_export_preview_requires_auth(auth_client, anon_client, book_with_chapters):
    """Export preview requires auth."""
    book_id = book_with_chapters["book_id"]
    resp = await anon_client.get(f"/api/v1/export/books/{book_id}/preview")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_export_txt(auth_client, book_with_chapters):
    """Export book as TXT."""
    book_id = book_with_chapters["book_id"]
    resp = await auth_client.get(f"/api/v1/export/books/{book_id}/txt")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")
    assert "Content-Disposition" in resp.headers
    assert "attachment" in resp.headers["Content-Disposition"]
    assert len(resp.content) > 0


@pytest.mark.asyncio
async def test_export_docx(auth_client, book_with_chapters):
    """Export book as DOCX."""
    book_id = book_with_chapters["book_id"]
    resp = await auth_client.get(f"/api/v1/export/books/{book_id}/docx")
    assert resp.status_code == 200
    assert "wordprocessingml" in resp.headers.get("content-type", "")
    assert "Content-Disposition" in resp.headers
    assert len(resp.content) > 0


@pytest.mark.asyncio
async def test_export_outline(auth_client, book_with_chapters):
    """Export chapter outline."""
    book_id = book_with_chapters["book_id"]
    resp = await auth_client.get(f"/api/v1/export/books/{book_id}/outline")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers.get("content-type", "")
    assert len(resp.content) > 0


@pytest.mark.asyncio
async def test_export_invalid_format(auth_client, book_with_chapters):
    """Invalid export format returns 400."""
    book_id = book_with_chapters["book_id"]
    resp = await auth_client.get(f"/api/v1/export/books/{book_id}/invalid")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_export_404(auth_client):
    """Export non-existent book returns 404."""
    resp = await auth_client.get(
        "/api/v1/export/books/00000000-0000-0000-0000-000000000001/txt"
    )
    assert resp.status_code == 404
