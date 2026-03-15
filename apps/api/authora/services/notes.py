"""Notes service: search, tagging, note-to-draft conversion."""

import uuid
from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.models import Note


def normalize_tag(tag: str) -> str:
    """Normalize tag: lowercase, strip, collapse spaces."""
    return " ".join(tag.lower().strip().split())


def normalize_tags(tags: list[str]) -> list[str]:
    """Normalize and deduplicate tags."""
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        n = normalize_tag(t)
        if n and n not in seen:
            seen.add(n)
            out.append(n)
    return sorted(out)


def add_tags(existing: list[str], new: list[str]) -> list[str]:
    """Merge new tags into existing, normalized."""
    return normalize_tags(existing + new)


def remove_tag(existing: list[str], tag: str) -> list[str]:
    """Remove tag from list (case-insensitive)."""
    n = normalize_tag(tag)
    return [t for t in existing if normalize_tag(t) != n]


async def search_notes(
    db: AsyncSession,
    project_id: uuid.UUID,
    *,
    q: str | None = None,
    note_type: str | None = None,
    book_id: uuid.UUID | None = None,
    chapter_id: uuid.UUID | None = None,
    pinned: bool | None = None,
    is_inspiration: bool | None = None,
    category: str | None = None,
    tags: list[str] | None = None,
    limit: int = 100,
) -> Sequence[Note]:
    """Search notes with full-text and filters."""
    stmt = select(Note).options(selectinload(Note.attachments)).where(Note.project_id == project_id)

    if q and q.strip():
        # Full-text search: use raw SQL for tsvector (matches migration index)
        search_term = q.strip().replace("'", "''")  # escape for safety
        stmt = stmt.where(
            text(
                "to_tsvector('english', coalesce(notes.title,'') || ' ' || coalesce(notes.content,'')) "
                "@@ plainto_tsquery('english', :q)"
            ).bindparams(q=search_term)
        )

    if note_type:
        stmt = stmt.where(Note.note_type == note_type)
    if book_id is not None:
        stmt = stmt.where(Note.book_id == book_id)
    if chapter_id is not None:
        stmt = stmt.where(Note.chapter_id == chapter_id)
    if pinned is not None:
        stmt = stmt.where(Note.pinned == pinned)
    if is_inspiration is not None:
        stmt = stmt.where(Note.is_inspiration == is_inspiration)
    if category:
        stmt = stmt.where(Note.category == category)
    if tags:
        for tag in tags:
            stmt = stmt.where(Note.tags.contains([normalize_tag(tag)]))

    stmt = stmt.order_by(Note.pinned.desc(), Note.sort_order.asc(), Note.updated_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


def note_content_to_draft(note: Note) -> str:
    """Convert note content into draft-ready text (for insertion into chapter)."""
    parts: list[str] = []
    if note.source:
        parts.append(f"[Source: {note.source}]")
    if note.source_url:
        parts.append(f"[URL: {note.source_url}]")
    parts.append(note.content.strip())
    return "\n\n".join(p for p in parts if p)
