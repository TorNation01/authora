"""Acceptance check: a real manuscript makes the round trip to Anema House.

Nothing on the house side is mocked. The pack is built from real chapters,
POSTed to the live intake service, read back out of the house's own admin API,
given a house decision, and then read back again through Authora's own status
refresh — so a green test means *both* legs work: author -> house, house ->
author.

It skips (never fails) when the intake service is not reachable, so a box with
the house switched off does not report a broken hand-over.

Run:
    cd apps/api && ANEMA_TEST_INTAKE_URL=http://127.0.0.1:8811 \
        /opt/authora-v2-venv/bin/python -m pytest tests/test_submission_roundtrip.py -q
"""

from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import shutil
import uuid
from pathlib import Path

import httpx
import pytest
from sqlalchemy import delete

from authora.config import get_settings
from authora.models import Book, Chapter, Project, User
from authora.services.auth import create_access_token, hash_password
from authora.services.submission import build_manuscript

INTAKE_URL = os.environ.get("ANEMA_TEST_INTAKE_URL", "http://127.0.0.1:8811").rstrip("/")
INTAKE_DATA = Path(os.environ.get("ANEMA_TEST_DATA", "/opt/anema-intake/data"))

# The DB fixtures run in the session loop (see pyproject: asyncio_default_fixture_loop_scope).
# Run the test body there too, or the pooled connection crosses loops and asyncpg refuses it.
pytestmark = pytest.mark.asyncio(loop_scope="session")

HOUSE = "Anema House Publishing"
AUTHOR_NAME = "Ellery Vance"
BOOK_TITLE = "The Salt Road"

# A real manuscript, not filler: the house queue is read by a human, and a pack
# built from placeholder text would prove nothing about ordering or encoding.
PROSE = """The tide went out at four in the morning and did not come back. By six the
whole bay was a field of green glass, and the boats that had been moored at the
jetty lay on their sides like animals asleep in the sun. My mother stood at the
kitchen window with her hands wrapped around a cup and said, without turning
round, that she had not slept either.

She had been waiting for the water to leave for thirty years. I knew this the
way you know a door is locked in a house you grew up in: not from being told,
but from the way people stopped talking when they walked past it.

The ledgers were in the shed behind the boathouse, under a tarpaulin that had
gone the colour of old bone. There were eleven of them, one for each summer the
village had kept records, and every one was written in the same slanting hand
until the last, which was mine. I was nine when my father taught me to enter a
catch. Weight, buyer, price, weather. He said the sea only ever lies in the
telling, and that a ledger was a promise you made to a stranger about a fish.

I carried them up the hill in two trips. On the second trip the gulls came down
and stood along the seawall in a line, all facing the same way, out towards
where the water should have been. My mother watched them from the step and said
they had come for the herring, and that the herring had come for the cold, and
that the cold had come for something we had not been told about.

Nobody in the village would say the word. They said the bay had turned, the way
you say a person has turned: a change of face rather than a death. But I had
seen the photographs in the county archive, and I had read the survey from the
year the causeway was built, and I knew that the water had gone out once before,
in the summer of my grandmother's confirmation, and that it had stayed out for
nine days and then come back so fast that a man on the flats had drowned in it.

The eleventh ledger had one page left. I inked the nib and set the ruler against
the margin and wrote the date, and under it, in the column where the weather
goes, I wrote: still."""


def _doc(text: str) -> dict:
    paragraphs = [p.strip().replace("\n", " ") for p in text.strip().split("\n\n") if p.strip()]
    return {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": paragraph}]}
            for paragraph in paragraphs
        ],
    }


def _admin_token() -> str:
    token = os.environ.get("ANEMA_TEST_ADMIN_TOKEN", "").strip()
    if token:
        return token
    env_file = Path("/opt/anema-intake/.env")
    if env_file.is_file():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("ANEMA_ADMIN_TOKEN="):
                return line.split("=", 1)[1].strip().strip("\"'")
    pytest.skip("no Anema House admin token available")


def _house_or_skip() -> str:
    try:
        response = httpx.get(f"{INTAKE_URL}/health", timeout=5)
    except httpx.HTTPError as exc:
        pytest.skip(f"Anema House intake unreachable at {INTAKE_URL}: {exc}")
    if response.status_code != 200:
        pytest.skip(f"Anema House intake unhealthy at {INTAKE_URL}: {response.status_code}")
    return _admin_token()


@pytest.fixture
async def manuscript(db):
    """An author, a project, a book and one chapter carrying real prose."""
    user = User(
        id=uuid.uuid4(),
        email=f"roundtrip-{uuid.uuid4().hex[:8]}@qa.authora.local",
        hashed_password=hash_password("Qa!roundtrip!1"),
        display_name=AUTHOR_NAME,
    )
    db.add(user)
    await db.flush()

    project = Project(user_id=user.id, name="QA — round trip")
    db.add(project)
    await db.flush()

    book = Book(project_id=project.id, title=BOOK_TITLE, genre="literary fiction")
    db.add(book)
    await db.flush()

    chapter = Chapter(
        book_id=book.id,
        title="Chapter One — The Salt Road",
        sort_order=0,
        content=_doc(PROSE),
        summary="The tide goes out and does not come back.",
        word_count=len(PROSE.split()),
    )
    db.add(chapter)
    await db.flush()

    yield user, book, chapter

    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()


async def test_manuscript_round_trips_to_anema_house(client, db, manuscript, monkeypatch):
    user, book, chapter = manuscript
    admin = _house_or_skip()

    # Post where we will read: the house the test verifies against.
    monkeypatch.setattr(get_settings(), "anema_intake_url", INTAKE_URL)

    token, _expires = create_access_token(user.id)
    headers = {"Authorization": f"Bearer {token}"}
    true_words = len(PROSE.split())
    expected = build_manuscript(book, [chapter], AUTHOR_NAME)

    # --- author leg -------------------------------------------------------
    response = await client.post(
        f"/api/v1/publish/books/{book.id}/submission",
        json={
            "publisher_name": HOUSE,
            "author_name": AUTHOR_NAME,
            "email": user.email,
            "title": BOOK_TITLE,
            "series": "",
            "genre": "literary fiction",
            # The author left the word-count box blank. The count the house sees
            # must come from the manuscript itself, not from an empty form field.
            "word_count": None,
            "pitch": "A drowned village, a returning son, and the ledgers his mother kept.",
            "include_cover": False,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    receipt = response.json()
    ref = receipt["submission"]["ref"]
    assert re.fullmatch(r"AH-\d{4}-\d{4}", ref), f"house returned a malformed reference: {ref!r}"

    record_dir = INTAKE_DATA / "submissions" / ref
    try:
        # --- what the house actually stored -------------------------------
        async with httpx.AsyncClient(timeout=15) as http:
            house = await http.get(f"{INTAKE_URL}/api/submissions/{ref}", headers={"X-Admin-Token": admin})
            assert house.status_code == 200, house.text
            stored = house.json()

            assert stored["source"] == "authora", stored
            assert stored["email"] == user.email
            assert stored["title"] == BOOK_TITLE
            assert stored["status"] == "received"
            assert stored["word_count"] == true_words, (
                f"house shows {stored['word_count']} words for a {true_words}-word manuscript"
            )

            files = stored["files"]
            assert len(files) == 1, files
            assert files[0]["original"] == expected.filename
            assert files[0]["bytes"] == len(expected.content)
            assert files[0]["sha256"] == hashlib.sha256(expected.content).hexdigest()[:16], (
                "the bytes in the house queue are not the bytes Authora packed"
            )

            # --- house leg: a human decision, read back through Authora ----
            decided = await http.post(
                f"{INTAKE_URL}/api/submissions/{ref}/decision",
                json={"decision": "reviewing", "note": "QA round-trip probe"},
                headers={"X-Admin-Token": admin},
            )
            assert decided.status_code == 200, decided.text
            assert decided.json()["status"] == "reviewing"
            house_decision = decided.json()["status"]

        refreshed = await client.post(
            f"/api/v1/publish/books/{book.id}/submission/refresh", headers=headers
        )
        assert refreshed.status_code == 200, refreshed.text
        assert refreshed.json()["submission"]["status"] == "reviewing", refreshed.text
        assert refreshed.json()["submission"]["ref"] == ref

        # The author's own view of the pack must match what was sent.
        view = await client.get(f"/api/v1/publish/books/{book.id}/submission", headers=headers)
        assert view.status_code == 200, view.text
        body = view.json()
        assert body["submission"]["ref"] == ref
        assert body["submission"]["status"] == "reviewing"
        assert body["pack"]["chapters"] == 1
        assert body["defaults"]["word_count"] == true_words

        print(
            f"\nround trip OK: {ref} | house={INTAKE_URL} | source={stored['source']}"
            f" | {stored['word_count']} words | {files[0]['bytes']} bytes"
            f" | sha256[:16]={files[0]['sha256']}"
            f" | house decision={house_decision!r} -> author refresh={body['submission']['status']!r}"
        )
    finally:
        _remove_from_house(ref, record_dir)


def _remove_from_house(ref: str, record_dir: Path) -> None:
    """A probe left in the queue is a fake submission a real editor will triage."""
    if not (INTAKE_DATA / "intake.db").is_file():
        shutil.rmtree(record_dir, ignore_errors=True)
        return
    conn = sqlite3.connect(INTAKE_DATA / "intake.db")
    try:
        conn.execute("DELETE FROM decisions WHERE ref=?", (ref,))
        conn.execute("DELETE FROM submissions WHERE ref=?", (ref,))
        conn.commit()
    finally:
        conn.close()
    shutil.rmtree(record_dir, ignore_errors=True)
