"""Publishing preparation - AI-generated synopsis, blurb, summaries, etc."""

import asyncio
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.models import Book, Chapter
from authora.services.ai import complete_sync
from authora.services.export import tiptap_to_plain_text


def _require(text: str | None, what: str) -> str:
    """Refuse to return silence: an empty model reply is a failure, not a result."""
    cleaned = (text or "").strip()
    if not cleaned:
        raise RuntimeError(f"The model returned nothing for the {what}. Check the AI provider in Settings.")
    return cleaned


async def _get_book_context(db: AsyncSession, book_id: UUID) -> tuple[Book, list[Chapter], str]:
    """Load book, chapters, and build context string."""
    result = await db.execute(
        select(Book).options(selectinload(Book.chapters)).where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise ValueError("Book not found")
    chapters = sorted(book.chapters, key=lambda c: c.sort_order)
    context_parts = []
    for ch in chapters[:10]:
        text = tiptap_to_plain_text(ch.content) if ch.content else ""
        context_parts.append(f"Chapter: {ch.title}\n{text[:1500]}...")
    return book, chapters, "\n\n".join(context_parts)


async def generate_synopsis(db: AsyncSession, book_id: UUID, extra: str | None = None) -> str:
    """Generate 1-2 page synopsis."""
    book, chapters, ctx = await _get_book_context(db, book_id)
    system = "You are a professional editor. Write a compelling synopsis suitable for agents and publishers."
    user = f"""Write a 1-2 page synopsis for this book.

Title: {book.title}
Genre: {book.genre or 'General'}

MANUSCRIPT EXCERPT:
{ctx[:8000]}

{extra or ''}

Write the synopsis:"""
    return _require(await complete_sync(user, system, max_tokens=1024), "synopsis")


async def generate_back_cover_blurb(db: AsyncSession, book_id: UUID, extra: str | None = None) -> str:
    """Generate back cover blurb (150-250 words)."""
    book, chapters, ctx = await _get_book_context(db, book_id)
    system = "You are a copywriter. Write a compelling back cover blurb that hooks readers."
    user = f"""Write a back cover blurb (150-250 words) for this book.

Title: {book.title}
Genre: {book.genre or 'General'}

MANUSCRIPT:
{ctx[:6000]}

{extra or ''}

Write the blurb. No spoilers. End with a hook:"""
    return _require(await complete_sync(user, system, max_tokens=512), "back cover blurb")


async def generate_chapter_summaries(db: AsyncSession, book_id: UUID) -> list[dict[str, str]]:
    """Generate 1-2 sentence summary per chapter."""
    book, chapters, _ = await _get_book_context(db, book_id)
    system = "Summarize this chapter in 1-2 sentences. Capture the key events or points."
    # Chapters are independent, so summarise them concurrently. Sequentially this
    # cost one LLM round-trip per chapter and blew past client timeouts on any
    # book longer than a few chapters.
    sem = asyncio.Semaphore(4)

    async def _one(ch):
        text = tiptap_to_plain_text(ch.content) if ch.content else ""
        if not text.strip():
            # Unwritten template chapter: the seeded brief is the only real
            # description we have, so use it instead of "(no content)".
            stored = (getattr(ch, "summary", None) or "").strip()
            if stored:
                return {"title": ch.title, "summary": stored}
            return {"title": ch.title, "summary": "(no content)"}
        async with sem:
            result = await complete_sync(f"Chapter: {ch.title}\n\n{text[:2000]}", system, max_tokens=200)
        return {"title": ch.title, "summary": (result or "").strip() or "(no summary produced)"}

    if not chapters:
        return []
    return list(await asyncio.gather(*[_one(ch) for ch in chapters]))


async def generate_beta_reader_pack(db: AsyncSession, book_id: UUID) -> dict[str, Any]:
    """Generate beta reader pack: synopsis, blurb, chapter summaries, feedback questions."""
    # These four products only depend on the manuscript, not on each other, so
    # run them together instead of chaining four full LLM round-trips.
    synopsis, blurb, summaries = await asyncio.gather(
        generate_synopsis(db, book_id),
        generate_back_cover_blurb(db, book_id),
        generate_chapter_summaries(db, book_id),
    )
    system = "Generate 5-7 feedback questions for beta readers. Mix plot, character, pacing, clarity."
    resp = await complete_sync(
        f"Book: {synopsis[:500]}...\n\nGenerate beta reader feedback questions:",
        system,
        max_tokens=400,
    )
    return {
        "synopsis": synopsis,
        "blurb": blurb,
        "chapter_summaries": summaries,
        "feedback_questions": [q.strip(" -\t*") for q in (resp or "").split("\n") if q.strip(" -\t*")],
    }


async def _author_identity(db: AsyncSession, book: Book) -> tuple[str, str]:
    """Author display name and their own profile notes, if either exists."""
    from authora.models import Profile, Project, User

    result = await db.execute(
        select(User, Profile)
        .join(Project, Project.user_id == User.id)
        .outerjoin(Profile, Profile.user_id == User.id)
        .where(Project.id == book.project_id)
    )
    row = result.first()
    if not row:
        return "", ""
    user, profile = row
    return (user.display_name or "", (profile.bio if profile else "") or "")


def _fallback_bio(name: str, book: Book) -> str:
    """Honest draft skeleton - never invents credits or biography."""
    who = name or "The author"
    genre = (book.genre or "fiction").strip()
    return (
        f"{who} writes {genre}. {book.title} is the current book in the series. "
        "Add publishing credits, where they write from, and what draws them to this subject "
        "before sending this bio anywhere."
    )


async def generate_author_bio_draft(db: AsyncSession, book_id: UUID, extra: str | None = None) -> str:
    """Generate draft author bio (50-100 words), grounded in the author's real details."""
    book, chapters, _ = await _get_book_context(db, book_id)
    name, profile_bio = await _author_identity(db, book)

    system = (
        "You are a publicist writing a book-jacket author bio. Use only the details supplied. "
        "Never invent prizes, sales figures, cities, degrees or previous titles."
    )
    user = f"""Write a 50-100 word third-person author bio.

Author name: {name or 'not supplied - use "The author"'}
Genre: {book.genre or 'General'}
Book: {book.title}
Draft chapters written: {len(chapters)}
Author's own notes: {profile_bio[:800] if profile_bio else 'none supplied'}
Extra context: {extra or 'none'}

If a detail is missing, leave it out rather than inventing it. Return only the bio text."""
    text = await complete_sync(user, system, max_tokens=320)
    if not (text or "").strip():
        retry_system = "You write short, factual author biographies. No invented facts."
        text = await complete_sync(user, retry_system, max_tokens=320)
    if not (text or "").strip():
        return _fallback_bio(name, book)
    return text.strip()


async def generate_handoff_pack(db: AsyncSession, book_id: UUID) -> dict[str, Any]:
    """Generate manuscript handoff pack for editor/designer."""
    pack = await generate_beta_reader_pack(db, book_id)
    book, _, _ = await _get_book_context(db, book_id)
    try:
        bio = await generate_author_bio_draft(db, book_id)
    except RuntimeError:
        name, _ = await _author_identity(db, book)
        bio = _fallback_bio(name, book)
    pack["author_bio"] = bio
    pack["handoff_notes"] = pack.get("feedback_questions", [])[:3]
    return pack


