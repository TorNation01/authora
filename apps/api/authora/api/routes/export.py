"""Export API routes - book, outline, notes, chapter, publishing prep."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.config import get_settings
from authora.database import get_db
from authora.models import Book, Chapter, Note, Project
from authora.schemas.export_schema import ExportOptions
from authora.services.export import (
    export_docx,
    export_epub,
    export_pdf,
    export_txt,
    get_export_filename,
    tiptap_to_plain_text,
)
from authora.services.export_extended import (
    ExportParams,
    export_chapters_zip,
    export_full_docx,
    export_full_epub,
    export_full_pdf,
    export_full_txt,
    export_notes_txt,
    export_outline,
)
from authora.services.publishing_prep import (
    generate_author_bio_draft,
    generate_back_cover_blurb,
    generate_beta_reader_pack,
    generate_chapter_summaries,
    generate_handoff_pack,
    generate_synopsis,
)

router = APIRouter(prefix="/export", tags=["export"])


async def get_book_with_chapters(db: AsyncSession, book_id: uuid.UUID, user_id: uuid.UUID) -> Book | None:
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.chapters))
        .join(Project)
        .where(Book.id == book_id, Project.user_id == user_id)
    )
    return result.scalar_one_or_none()


def _chapters_data(book: Book) -> list[dict]:
    return [
        {"title": c.title, "content": c.content}
        for c in sorted(book.chapters, key=lambda x: x.sort_order)
    ]


def _export_params_from_options(opts: ExportOptions | None, book_title: str) -> ExportParams:
    if not opts:
        return ExportParams(book_title=book_title)
    return ExportParams(
        book_title=book_title,
        author_name=opts.author_name or "Author",
        include_title_page=opts.include_title_page,
        include_toc=opts.include_toc,
        include_acknowledgements=opts.include_acknowledgements,
        front_matter=opts.front_matter,
        back_matter=opts.back_matter,
        acknowledgements=opts.acknowledgements,
        format_style=opts.format_style,
    )


@router.get("/books/{book_id}/preview")
async def export_preview(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Preview export structure before final export."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    chapters = sorted(book.chapters, key=lambda x: x.sort_order)
    total_words = sum(
        len(tiptap_to_plain_text(c.content).split())
        for c in chapters
    )
    return {
        "book_title": book.title,
        "chapter_count": len(chapters),
        "total_words": total_words,
        "chapters": [{"title": c.title, "word_count": c.word_count} for c in chapters],
        "has_front_matter": False,
        "has_back_matter": False,
        "has_acknowledgements": False,
    }


class ExportRequest(BaseModel):
    """Export request with options."""

    options: ExportOptions | None = None


@router.get("/books/{book_id}/{format}")
async def export_book(
    book_id: uuid.UUID,
    format: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    include_title_page: bool = Query(True),
    include_toc: bool = Query(True),
    author_name: str | None = Query(None),
    front_matter: str | None = Query(None),
    back_matter: str | None = Query(None),
    acknowledgements: str | None = Query(None),
    format_style: str = Query("manuscript", pattern="^(manuscript|print|ebook)$"),
):
    """Export book to specified format. Supports front/back matter via query params."""
    if format not in ("docx", "pdf", "epub", "txt"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format")

    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    chapters_data = _chapters_data(book)
    params = ExportParams(
        book_title=book.title,
        author_name=author_name or "Author",
        include_title_page=include_title_page,
        include_toc=include_toc,
        front_matter=front_matter,
        back_matter=back_matter,
        acknowledgements=acknowledgements,
        include_acknowledgements=bool(acknowledgements),
        format_style=format_style,
    )

    if format == "txt":
        content = export_full_txt(chapters_data, params)
        media_type = "text/plain"
    elif format == "docx":
        content = export_full_docx(chapters_data, params)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif format == "pdf":
        content = export_full_pdf(chapters_data, params)
        media_type = "application/pdf"
    elif format == "epub":
        content = export_full_epub(chapters_data, params)
        media_type = "application/epub+zip"
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format")

    filename = get_export_filename(book.title, format)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/books/{book_id}/outline")
async def export_book_outline(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Export chapter outline only."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    chapters_data = _chapters_data(book)
    content = export_outline(chapters_data)
    filename = get_export_filename(book.title, "txt")
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename.replace(".txt", "_outline.txt")}"'},
    )


@router.get("/books/{book_id}/chapters")
async def export_chapters(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    format: str = Query("docx", pattern="^(docx|txt|pdf)$"),
    as_zip: bool = Query(True, description="Export each chapter as separate file in ZIP"),
):
    """Export chapters - single ZIP or individual files."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    chapters_data = _chapters_data(book)
    if as_zip:
        content = export_chapters_zip(chapters_data, book.title, format)
        ext = "zip"
        media_type = "application/zip"
    else:
        content = export_chapters_zip(chapters_data, book.title, format)
        ext = "zip"
        media_type = "application/zip"

    filename = get_export_filename(book.title, ext)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/projects/{project_id}/notes")
async def export_project_notes(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_id: uuid.UUID | None = Query(None),
):
    """Export project notes as TXT."""
    result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    stmt = select(Note).where(Note.project_id == project_id)
    if book_id:
        stmt = stmt.where(Note.book_id == book_id)
    result = await db.execute(stmt)
    notes = result.scalars().all()

    notes_data = [
        {
            "title": n.title,
            "content": n.content,
            "note_type": n.note_type,
            "source": n.source,
            "tags": n.tags or [],
        }
        for n in notes
    ]
    content = export_notes_txt(notes_data)
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": 'attachment; filename="notes_export.txt"'},
    )


# Publishing prep
class PublishingPrepRequest(BaseModel):
    """Request for publishing prep generation."""

    type: str = Field(..., pattern="^(synopsis|blurb|chapter_summaries|beta_pack|author_bio|handoff_pack)$")
    extra_context: str | None = None


@router.get("/books/{book_id}/publishing-prep/{prep_type}")
async def get_publishing_prep(
    book_id: uuid.UUID,
    prep_type: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    extra_context: str | None = Query(None),
):
    """Generate publishing prep content (synopsis, blurb, etc.)."""
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    result = await db.execute(
        select(Book).options(selectinload(Book.chapters)).join(Project).where(
            Book.id == book_id, Project.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    if prep_type == "synopsis":
        text = await generate_synopsis(db, book_id, extra_context)
        return {"type": "synopsis", "content": text}
    if prep_type == "blurb":
        text = await generate_back_cover_blurb(db, book_id, extra_context)
        return {"type": "blurb", "content": text}
    if prep_type == "chapter_summaries":
        summaries = await generate_chapter_summaries(db, book_id)
        return {"type": "chapter_summaries", "content": summaries}
    if prep_type == "beta_pack":
        pack = await generate_beta_reader_pack(db, book_id)
        return {"type": "beta_pack", "content": pack}
    if prep_type == "author_bio":
        text = await generate_author_bio_draft(db, book_id, extra_context)
        return {"type": "author_bio", "content": text}
    if prep_type == "handoff_pack":
        pack = await generate_handoff_pack(db, book_id)
        return {"type": "handoff_pack", "content": pack}
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prep type")
