"""Publishing preparation - AI-generated synopsis, blurb, summaries, etc."""

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.models import Book, Chapter
from authora.services.ai_registry import TASK_EDITING_POLISH
from authora.services.ai_service import complete_sync
from authora.services.export import tiptap_to_plain_text


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
    resp = await complete_sync(user, system, max_tokens=1024, task=TASK_EDITING_POLISH)
    return resp.text


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
    resp = await complete_sync(user, system, max_tokens=512, task=TASK_EDITING_POLISH)
    return resp.text


async def generate_chapter_summaries(db: AsyncSession, book_id: UUID) -> list[dict[str, str]]:
    """Generate 1-2 sentence summary per chapter."""
    book, chapters, _ = await _get_book_context(db, book_id)
    summaries = []
    for ch in chapters:
        text = tiptap_to_plain_text(ch.content) if ch.content else ""
        if not text.strip():
            summaries.append({"title": ch.title, "summary": "(no content)"})
            continue
        system = "Summarize this chapter in 1-2 sentences. Capture the key events or points."
        result = await complete_sync(f"Chapter: {ch.title}\n\n{text[:2000]}", system, max_tokens=150)
        summaries.append({"title": ch.title, "summary": result.strip()})
    return summaries


async def generate_beta_reader_pack(db: AsyncSession, book_id: UUID) -> dict[str, Any]:
    """Generate beta reader pack: synopsis, blurb, chapter summaries, feedback questions."""
    synopsis = await generate_synopsis(db, book_id)
    blurb = await generate_back_cover_blurb(db, book_id)
    summaries = await generate_chapter_summaries(db, book_id)
    system = "Generate 5-7 feedback questions for beta readers. Mix plot, character, pacing, clarity."
    resp = await complete_sync(
        f"Book: {synopsis[:500]}...\n\nGenerate beta reader feedback questions:",
        system,
        max_tokens=300,
        task=TASK_EDITING_POLISH,
    )
    return {
        "synopsis": synopsis,
        "blurb": blurb,
        "chapter_summaries": summaries,
        "feedback_questions": questions.strip().split("\n"),
    }


async def generate_author_bio_draft(db: AsyncSession, book_id: UUID, extra: str | None = None) -> str:
    """Generate draft author bio (50-100 words)."""
    book, _, ctx = await _get_book_context(db, book_id)
    system = "You are a publicist. Write a professional author bio suitable for book jacket."
    user = f"""Write a 50-100 word author bio for this book.

Title: {book.title}
Genre: {book.genre or 'General'}

{extra or 'Write a generic professional bio.'}

Write the bio in third person:"""
    resp = await complete_sync(user, system, max_tokens=256, task=TASK_EDITING_POLISH)
    return resp.text


async def generate_handoff_pack(db: AsyncSession, book_id: UUID) -> dict[str, Any]:
    """Generate manuscript handoff pack for editor/designer."""
    pack = await generate_beta_reader_pack(db, book_id)
    bio = await generate_author_bio_draft(db, book_id)
    pack["author_bio"] = bio
    pack["handoff_notes"] = pack.get("feedback_questions", [])[:3]
    return pack
