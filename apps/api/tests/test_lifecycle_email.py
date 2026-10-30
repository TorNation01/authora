"""Lifecycle email — the seven-message ladder from signup to first published book.

These tests are the acceptance check for the task "Lifecycle email: 7-message
sequence from signup to first published book". They exercise the real planner
against the real database models and a stubbed transport boundary only.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select

from authora.models import Book, Chapter, LifecycleEmailLog, Project, PublisherSubmission, User
from authora.services import lifecycle_email as lc


def _doc(text: str) -> dict:
    """Minimal ProseMirror document holding `text`."""
    return {
        "type": "doc",
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ],
    }


@pytest.fixture
def outbox(monkeypatch):
    """Capture what would be mailed instead of opening an SMTP connection."""
    sent: list[dict] = []

    async def fake_deliver(to: str, subject: str, text: str, html: str) -> bool:
        sent.append({"to": to, "subject": subject, "text": text, "html": html})
        return True

    monkeypatch.setattr(lc, "_deliver", fake_deliver)
    return sent


async def _user(db, *, email: str, age_hours: float, name: str = "Probe") -> User:
    u = User(
        email=email,
        hashed_password="x",
        display_name=name,
        is_active=True,
        created_at=datetime.now(timezone.utc) - timedelta(hours=age_hours),
    )
    db.add(u)
    await db.flush()
    return u


async def _project_with_book(db, user: User, *, words: int = 0, bible: bool = False):
    p = Project(user_id=user.id, name="Probe Project")
    db.add(p)
    await db.flush()
    b = Book(project_id=p.id, title="Probe Book")
    db.add(b)
    await db.flush()
    if words:
        c = Chapter(book_id=b.id, title="Chapter 1", sort_order=0, content=_doc(" ".join(["word"] * words)))
        db.add(c)
    if bible:
        from authora.models import BookBible

        db.add(BookBible(book_id=b.id, sections={}, section_status={}))
    await db.flush()
    return p, b


# ---------------------------------------------------------------- the ladder
def test_sequence_is_seven_messages_from_signup_to_published():
    steps = lc.LIFECYCLE_STEPS
    assert len(steps) == 7, f"expected 7 messages, got {len(steps)}"
    keys = [s.key for s in steps]
    assert len(set(keys)) == 7, f"duplicate step keys: {keys}"
    assert keys[0] == "welcome"
    assert keys[-1] == "published"
    # the six timed messages must be an ordered ladder, published is event-driven
    delays = [s.delay_hours for s in steps[:-1]]
    assert delays == sorted(delays), f"timed ladder out of order: {delays}"
    assert steps[-1].delay_hours == 0
    for s in steps:
        assert s.subject and s.heading, f"{s.key} has no subject/heading"


async def test_new_signup_gets_welcome_first_and_nothing_else(db, outbox):
    user = await _user(db, email="lc-new@example.com", age_hours=2)
    result = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert result["sent"] == 1, result
    assert len(outbox) == 1
    assert outbox[0]["to"] == "lc-new@example.com"
    assert "Welcome" in outbox[0]["subject"]
    assert "dashboard" in outbox[0]["text"].lower()
    rows = (await db.execute(select(LifecycleEmailLog).where(LifecycleEmailLog.user_id == user.id))).scalars().all()
    assert [(r.step, r.status) for r in rows] == [("welcome", "sent")]


async def test_idle_signup_with_no_project_is_nudged_after_a_day(db, outbox):
    user = await _user(db, email="lc-idle@example.com", age_hours=25)
    await lc.run_lifecycle_sweep(db, user_ids=[user.id])  # welcome
    await lc.run_lifecycle_sweep(db, user_ids=[user.id])  # day-1 nudge
    assert [m["subject"] for m in outbox][-1].lower().startswith("start your first book")
    assert "start a book" in outbox[-1]["text"].lower()


async def test_user_who_already_started_is_not_told_to_start(db, outbox):
    user = await _user(db, email="lc-started@example.com", age_hours=25)
    await _project_with_book(db, user)
    await lc.run_lifecycle_sweep(db, user_ids=[user.id])  # welcome
    result = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert result["sent"] == 0, result  # nothing relevant yet; first_book was skipped
    rows = (await db.execute(select(LifecycleEmailLog).where(LifecycleEmailLog.user_id == user.id))).scalars().all()
    assert ("first_book", "skipped") in {(r.step, r.status) for r in rows}
    assert all("first book" not in m["subject"].lower() for m in outbox)


async def test_published_user_skips_the_nudges_and_gets_the_published_note(db, outbox):
    user = await _user(db, email="lc-published@example.com", age_hours=2000)
    _, book = await _project_with_book(db, user, words=1200, bible=True)
    db.add(
        PublisherSubmission(
            book_id=book.id,
            user_id=user.id,
            publisher_name="Anema House Publishing",
            ref="AHP-TEST-1",
            status="received",
            payload={},
            files=[],
        )
    )
    await db.flush()
    # a shipped book ends the ladder: the nudges are recorded as skipped and the
    # published note goes out on the first sweep that sees the submission.
    result = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert result["sent"] == 1, result
    assert "first book is out" in outbox[-1]["subject"].lower()
    rows = (await db.execute(select(LifecycleEmailLog).where(LifecycleEmailLog.user_id == user.id))).scalars().all()
    statuses = {r.step: r.status for r in rows}
    assert statuses["published"] == "sent"
    assert all(v == "skipped" for k, v in statuses.items() if k not in {"welcome", "published"})


async def test_a_message_is_never_sent_twice(db, outbox):
    user = await _user(db, email="lc-once@example.com", age_hours=25)
    first = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    second = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    third = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert first["sent"] == 1 and second["sent"] == 1, (first, second)
    assert third["sent"] == 0, third
    emails = [m["subject"] for m in outbox]
    assert len(emails) == len(set(emails)) == 2, emails


async def test_writer_with_words_is_pushed_to_export_not_to_start(db, outbox):
    user = await _user(db, email="lc-writer@example.com", age_hours=400)
    await _project_with_book(db, user, words=20000, bible=True)
    await lc.run_lifecycle_sweep(db, user_ids=[user.id])  # welcome
    result = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert result["sent"] == 1, result
    assert "export" in outbox[-1]["subject"].lower()
    assert "start a book" not in outbox[-1]["text"].lower()


async def test_sweep_ignores_inactive_accounts(db, outbox):
    user = await _user(db, email="lc-off@example.com", age_hours=100)
    user.is_active = False
    await db.flush()
    result = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert result["sent"] == 0 and not outbox


async def test_failed_send_is_logged_and_retried_next_run(db, monkeypatch):
    user = await _user(db, email="lc-fail@example.com", age_hours=2)
    calls = {"n": 0}

    async def broken(to, subject, text, html):
        calls["n"] += 1
        return False

    monkeypatch.setattr(lc, "_deliver", broken)
    first = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert first["failed"] == 1, first
    rows = (await db.execute(select(LifecycleEmailLog).where(LifecycleEmailLog.user_id == user.id))).scalars().all()
    assert [(r.step, r.status) for r in rows] == [("welcome", "failed")]

    ok_calls = []

    async def fixed(to, subject, text, html):
        ok_calls.append(subject)
        return True

    monkeypatch.setattr(lc, "_deliver", fixed)
    second = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert second["sent"] == 1 and len(ok_calls) == 1


async def test_registration_welcome_stamp_prevents_a_second_welcome(db, outbox):
    """Registration stamps step 1 itself; the sweep must respect that stamp."""
    user = await _user(db, email="lc-stamped@example.com", age_hours=2)
    db.add(LifecycleEmailLog(user_id=user.id, step="welcome", status="sent", detail="at registration"))
    await db.flush()
    result = await lc.run_lifecycle_sweep(db, user_ids=[user.id])
    assert result["sent"] == 0 and not outbox, (result, outbox)
