"""Export API routes - book, outline, notes, chapter, publishing prep."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel, Field
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.config import get_settings
from authora.database import get_db
from authora.models import Book, Chapter, ExportJob, ExportProfile, Note, Project
from authora.schemas.export_schema import ExportOptions
from authora.services.compile_engine import CompileOptions, CompileType, compile_manuscript
from authora.services.export import (
    export_docx,
    export_epub,
    export_pdf,
    export_txt,
    tiptap_to_plain_text,
)
from authora.services.export_extended import (
    ExportParams,
    export_beta_reader_package,
    export_chapter_summary_sheet,
    export_chapters_zip,
    export_formatting_preview_html,
    export_full_docx,
    export_full_epub,
    export_full_html,
    export_full_json,
    export_full_markdown,
    export_full_pdf,
    export_full_txt,
    export_ghostwriter_handoff,
    export_notes_txt,
    export_outline,
    export_synopsis_package,
    validate_export_content,
)
from authora.services.export_filename import get_export_filename
from authora.services.export_presets import get_all_system_presets, get_system_preset
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


def _chapters_data(book: Book, include_meta: bool = False) -> list[dict]:
    """Build chapters data for export. include_meta adds id, sort_order, section_status, deleted_at for compile."""
    out = []
    for c in sorted(book.chapters, key=lambda x: x.sort_order):
        d = {"title": c.title, "content": c.content}
        if include_meta:
            d["id"] = str(c.id)
            d["sort_order"] = c.sort_order
            d["section_status"] = c.section_status
            d["deleted_at"] = c.deleted_at.isoformat() if c.deleted_at else None
        out.append(d)
    return out


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


@router.get("/books/{book_id}/export-history")
async def export_history(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(20, ge=1, le=100),
):
    """List recent exports for this book."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    result = await db.execute(
        select(ExportJob)
        .where(and_(ExportJob.book_id == book_id, ExportJob.user_id == current_user.id))
        .order_by(desc(ExportJob.created_at))
        .limit(limit)
    )
    jobs = result.scalars().all()
    return {
        "book_id": str(book_id),
        "exports": [
            {
                "id": str(j.id),
                "format": j.format,
                "status": j.status,
                "created_at": j.created_at.isoformat() if j.created_at else None,
                "options": j.options,
            }
            for j in jobs
        ],
    }


@router.get("/books/{book_id}/validate")
async def export_validate(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
    require_author: bool = Query(False),
    check_placeholders: bool = Query(True),
    check_unresolved_comments: bool = Query(False),
):
    """Validate content before export. Returns warnings, errors, and suggested fixes."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    chapters_data = _chapters_data(book)
    from sqlalchemy import func, select
    from authora.models import ContentComment

    unresolved = 0
    if check_unresolved_comments:
        stmt = (
            select(func.count(ContentComment.id))
            .select_from(ContentComment)
            .join(Chapter, ContentComment.chapter_id == Chapter.id)
            .where(Chapter.book_id == book_id, ContentComment.resolved_at.is_(None))
        )
        r = await db.execute(stmt)
        unresolved = r.scalar() or 0
    return validate_export_content(
        chapters_data,
        book_title=book.title,
        author_name=author_name,
        require_author=require_author,
        check_placeholders=check_placeholders,
        check_unresolved_comments=check_unresolved_comments,
        unresolved_comment_count=unresolved,
    )


@router.get("/books/{book_id}/preview")
async def export_preview(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
    front_matter: str | None = Query(None),
    back_matter: str | None = Query(None),
    dedication: str | None = Query(None),
    epigraph: str | None = Query(None),
    copyright_notice: str | None = Query(None),
    author_bio: str | None = Query(None),
    acknowledgements: str | None = Query(None),
    format_style: str = Query("manuscript", pattern="^(manuscript|print|ebook|workbook)$"),
):
    """Preview export structure. Use format_preview for HTML rendering."""
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
        "has_front_matter": bool(dedication or epigraph or copyright_notice or front_matter),
        "has_back_matter": bool(acknowledgements or author_bio or back_matter),
        "has_acknowledgements": bool(acknowledgements),
    }


@router.get("/books/{book_id}/format-preview")
async def export_format_preview(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
    front_matter: str | None = Query(None),
    back_matter: str | None = Query(None),
    dedication: str | None = Query(None),
    epigraph: str | None = Query(None),
    copyright_notice: str | None = Query(None),
    author_bio: str | None = Query(None),
    acknowledgements: str | None = Query(None),
    include_title_page: bool = Query(True),
    include_toc: bool = Query(True),
    format_style: str = Query("manuscript", pattern="^(manuscript|print|ebook|workbook)$"),
):
    """HTML preview of export structure for review before download."""
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
        dedication=dedication,
        epigraph=epigraph,
        copyright_notice=copyright_notice,
        author_bio=author_bio,
        format_style=format_style,
    )
    html_content = export_formatting_preview_html(chapters_data, params)
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)


class CompilePreviewRequest(BaseModel):
    """Request for compile preview."""

    compile_type: str = "full"
    chapter_ids: list[str] | None = None
    include_archived: bool = False
    include_unfinished: bool = True
    exclude_notes_comments: bool = True
    exclude_highlights: bool = True
    exclude_revision_marks: bool = True


@router.post("/books/{book_id}/compile-preview")
async def export_compile_preview(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: CompilePreviewRequest | None = None,
):
    """Preview compiled manuscript structure before export."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    chapters_data = _chapters_data(book, include_meta=True)
    try:
        ct = CompileType(body.compile_type) if body and body.compile_type else CompileType.FULL
    except ValueError:
        ct = CompileType.FULL
    opts = CompileOptions(
        compile_type=ct,
        chapter_ids=body.chapter_ids if body else None,
        include_archived=body.include_archived if body else False,
        include_unfinished=body.include_unfinished if body else True,
        exclude_notes_comments=body.exclude_notes_comments if body else True,
        exclude_highlights=body.exclude_highlights if body else True,
        exclude_revision_marks=body.exclude_revision_marks if body else True,
    )
    if body and body.compile_type:
        opts.apply_preset(body.compile_type)

    opts.front_matter_blocks = opts.front_matter_blocks or []
    opts.back_matter_blocks = opts.back_matter_blocks or []

    chapters_for_export, result = compile_manuscript(
        chapters_data,
        opts,
        book_title=book.title,
        author_name="Author",
    )

    return {
        "structure": result.structure_preview,
        "total_words": result.total_words,
        "total_pages_estimate": result.total_pages_estimate,
        "chapter_count": len(chapters_for_export),
        "toc_entries": result.toc_entries,
        "warnings": result.warnings,
        "included_chapters": [c.title for c in result.chapters if c.included],
        "excluded_chapters": [
            {"title": c.title, "reason": c.reason_excluded}
            for c in result.chapters
            if not c.included
        ],
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
    dedication: str | None = Query(None),
    epigraph: str | None = Query(None),
    copyright_notice: str | None = Query(None),
    author_bio: str | None = Query(None),
    format_style: str = Query("manuscript", pattern="^(manuscript|print|ebook|workbook)$"),
    backup_style: bool = Query(False, description="Use backup-style filename (title-backup-YYYY-MM-DD.ext)"),
):
    """Export book to specified format. Supports front/back matter via query params."""
    from authora.config import get_settings
    from authora.services.billing_service import check_export_limit, record_usage

    if format not in ("docx", "pdf", "epub", "txt", "md", "html", "json"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid format")

    settings = get_settings()
    if settings.feature_billing:
        allowed, used, limit = await check_export_limit(db, current_user.id, format)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Export limit reached ({used}/{limit} this month) or format not in plan. Upgrade for more.",
            )

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
        dedication=dedication,
        epigraph=epigraph,
        copyright_notice=copyright_notice,
        author_bio=author_bio,
        format_style=format_style,
    )

    fmt_map = {
        "txt": ("text/plain", export_full_txt),
        "docx": ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", export_full_docx),
        "pdf": ("application/pdf", export_full_pdf),
        "epub": ("application/epub+zip", export_full_epub),
        "md": ("text/markdown", export_full_markdown),
        "html": ("text/html", export_full_html),
        "json": ("application/json", export_full_json),
    }
    media_type, export_fn = fmt_map[format]
    content = export_fn(chapters_data, params)

    if settings.feature_billing:
        await record_usage(db, current_user.id, "exports", 1)

    job = ExportJob(
        user_id=current_user.id,
        book_id=book_id,
        format=format,
        status="completed",
        options={"backup_style": backup_style},
    )
    db.add(job)
    await db.flush()
    from authora.services.onboarding_analytics import record_first_export_completed

    await record_first_export_completed(db, current_user.id, book_id, format)
    await db.commit()

    ext = "docx" if format == "docx" else format
    filename = get_export_filename(book.title, ext, backup_style=backup_style)
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/books/{book_id}/priority/{export_type}")
async def export_priority(
    book_id: uuid.UUID,
    export_type: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
    dedication: str | None = Query(None),
    epigraph: str | None = Query(None),
    copyright_notice: str | None = Query(None),
    author_bio: str | None = Query(None),
    acknowledgements: str | None = Query(None),
    format_style: str = Query("manuscript", pattern="^(manuscript|print|ebook|workbook)$"),
    max_chapters: int = Query(3, ge=1, le=50, description="For sample-chapters: max chapters to include"),
):
    """
    Premium export for priority real-world outputs. Uses intelligent naming and compile options.

    Types: clean-manuscript, clean-manuscript-pdf, editor-review, beta-reader, submission,
    sample-chapters, workbook, ghostwriter
    """
    from authora.config import get_settings
    from authora.services.billing_service import check_export_limit, record_usage

    if export_type not in (
        "clean-manuscript",
        "clean-manuscript-pdf",
        "editor-review",
        "beta-reader",
        "submission",
        "sample-chapters",
        "workbook",
        "ghostwriter",
    ):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown export type")

    settings = get_settings()
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    author = author_name or "Author"
    today = __import__("datetime").date.today().isoformat()
    safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in (book.title or "manuscript"))[:50] or "manuscript"

    if export_type in ("beta-reader", "ghostwriter"):
        if settings.feature_billing:
            allowed, used, limit = await check_export_limit(db, current_user.id, "zip")
            if not allowed:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Export limit reached")
        if settings.openai_api_key or settings.anthropic_api_key:
            if export_type == "beta-reader":
                pack = await generate_beta_reader_pack(db, book_id)
                chapters_data = _chapters_data(book)
                params = ExportParams(
                    book_title=book.title,
                    author_name=author,
                    include_title_page=True,
                    include_toc=True,
                    include_acknowledgements=bool(acknowledgements),
                    dedication=dedication,
                    epigraph=epigraph,
                    copyright_notice=copyright_notice,
                    acknowledgements=acknowledgements,
                )
                content = export_beta_reader_package(chapters_data, pack, params)
                filename = f"{safe_title}_BetaReader_{today}.zip"
            else:
                pack = await generate_handoff_pack(db, book_id)
                chapters_data = _chapters_data(book)
                params = ExportParams(
                    book_title=book.title,
                    author_name=author,
                    include_title_page=True,
                    include_toc=True,
                    include_acknowledgements=bool(acknowledgements),
                    dedication=dedication,
                    epigraph=epigraph,
                    copyright_notice=copyright_notice,
                    acknowledgements=acknowledgements,
                )
                content = export_ghostwriter_handoff(chapters_data, pack, params, has_ghostwriter_content=False)
                filename = f"{safe_title}_GhostwriterDelivery_{today}.zip"
        else:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured for these packages")
        if settings.feature_billing:
            await record_usage(db, current_user.id, "exports", 1)
        return Response(
            content=content,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    chapters_data = _chapters_data(book)
    if export_type == "sample-chapters":
        chapters_data = chapters_data[:max_chapters]

    fmt_style = "workbook" if export_type == "workbook" else format_style
    fmt_style = "manuscript" if export_type in ("submission", "clean-manuscript", "editor-review", "sample-chapters") else fmt_style
    fmt_style = "print" if export_type == "clean-manuscript-pdf" else fmt_style

    params = ExportParams(
        book_title=book.title,
        author_name=author,
        include_title_page=True,
        include_toc=True,
        include_acknowledgements=bool(acknowledgements) or export_type == "editor-review",
        dedication=dedication,
        epigraph=epigraph,
        copyright_notice=copyright_notice,
        author_bio=author_bio,
        acknowledgements=acknowledgements,
        format_style=fmt_style,
    )

    if export_type == "clean-manuscript":
        content = export_full_docx(chapters_data, params)
        filename = f"{safe_title}_CleanManuscript_{today}.docx"
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif export_type == "clean-manuscript-pdf":
        content = export_full_pdf(chapters_data, params)
        filename = f"{safe_title}_CleanManuscript_{today}.pdf"
        media_type = "application/pdf"
    elif export_type == "editor-review":
        content = export_full_docx(chapters_data, params)
        filename = f"{safe_title}_EditorReview_{today}.docx"
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif export_type == "submission":
        content = export_full_docx(chapters_data, params)
        filename = f"{safe_title}_Submission_{today}.docx"
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif export_type == "sample-chapters":
        content = export_full_docx(chapters_data, params)
        filename = f"{safe_title}_SampleChapters_{today}.docx"
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif export_type == "workbook":
        content = export_full_pdf(chapters_data, params)
        filename = f"{safe_title}_Workbook_{today}.pdf"
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown export type")

    if settings.feature_billing:
        fmt = "docx" if "docx" in media_type else "pdf"
        allowed, used, limit = await check_export_limit(db, current_user.id, fmt)
        if not allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Export limit reached")
        await record_usage(db, current_user.id, "exports", 1)

    job = ExportJob(
        user_id=current_user.id,
        book_id=book_id,
        format=export_type.replace("-", "_"),
        status="completed",
        options={"priority": True},
    )
    db.add(job)
    await db.flush()
    from authora.services.onboarding_analytics import record_first_export_completed

    await record_first_export_completed(db, current_user.id, book_id, export_type.replace("-", "_"))
    await db.commit()

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
    filename = get_export_filename(book.title, "txt", suffix="_outline")
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
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


@router.get("/books/{book_id}/packages/beta-reader")
async def export_beta_reader_package_route(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
):
    """Export beta reader package (ZIP): manuscript + synopsis + feedback form + chapter summaries."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    pack = await generate_beta_reader_pack(db, book_id)
    chapters_data = _chapters_data(book)
    params = ExportParams(
        book_title=book.title,
        author_name=author_name or "Author",
        include_title_page=True,
        include_toc=True,
    )
    content = export_beta_reader_package(chapters_data, pack, params)
    filename = get_export_filename(book.title, "zip", suffix="_beta_package")
    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/books/{book_id}/packages/ghostwriter-handoff")
async def export_ghostwriter_handoff_route(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
):
    """Export ghostwriter delivery handoff (ZIP): manuscript + synopsis + summaries + bio + handoff notes."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    pack = await generate_handoff_pack(db, book_id)
    chapters_data = _chapters_data(book)
    params = ExportParams(
        book_title=book.title,
        author_name=author_name or "Author",
        include_title_page=True,
        include_toc=True,
    )
    content = export_ghostwriter_handoff(chapters_data, pack, params, has_ghostwriter_content=False)
    filename = get_export_filename(book.title, "zip", suffix="_handoff")
    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/books/{book_id}/packages/chapter-summary-sheet")
async def export_chapter_summary_sheet_route(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
):
    """Export chapter summary sheet (DOCX) for editor handoff."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    summaries = await generate_chapter_summaries(db, book_id)
    content = export_chapter_summary_sheet(summaries, book.title, author_name or "Author")
    filename = get_export_filename(book.title, "docx", suffix="_chapter_summaries")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/books/{book_id}/packages/blurb")
async def export_back_cover_blurb_route(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Export back cover blurb as TXT."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    blurb = await generate_back_cover_blurb(db, book_id)
    content = f"BACK COVER BLURB\n\n{book.title}\n\n{blurb}".encode("utf-8")
    filename = get_export_filename(book.title, "txt", suffix="_blurb")
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/profiles")
async def list_export_profiles(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List export profiles: system presets + user's custom profiles."""
    system = get_all_system_presets()
    result = await db.execute(
        select(ExportProfile)
        .where(ExportProfile.user_id == current_user.id)
        .order_by(ExportProfile.sort_order, ExportProfile.name)
    )
    custom = result.scalars().all()
    return {
        "system_presets": system,
        "custom_profiles": [
            {
                "id": str(p.id),
                "name": p.name,
                "description": p.description,
                "format": p.format,
                "compile_type": p.compile_type,
                "format_style": p.format_style,
                "options": p.options,
                "naming_pattern": p.naming_pattern,
                "project_type": p.project_type,
            }
            for p in custom
        ],
    }


class ExportProfileCreate(BaseModel):
    """Create export profile."""

    name: str
    description: str | None = None
    format: str = "docx"
    compile_type: str = "full"
    format_style: str = "manuscript"
    options: dict | None = None
    front_matter_blocks: list[dict] | None = None
    back_matter_blocks: list[dict] | None = None
    naming_pattern: str | None = None
    project_type: str | None = None


@router.post("/profiles")
async def create_export_profile(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: ExportProfileCreate,
):
    """Create custom export profile."""
    profile = ExportProfile(
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        is_system=False,
        format=body.format,
        compile_type=body.compile_type,
        format_style=body.format_style,
        options=body.options,
        front_matter_blocks=body.front_matter_blocks,
        back_matter_blocks=body.back_matter_blocks,
        naming_pattern=body.naming_pattern,
        project_type=body.project_type,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return {"id": str(profile.id), "name": profile.name}


@router.get("/profiles/{profile_id}")
async def get_export_profile(
    profile_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get export profile by ID (UUID) or system key (e.g. clean_manuscript)."""
    system = get_system_preset(profile_id)
    if system:
        return {"type": "system", **system}
    try:
        profile_uuid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    result = await db.execute(
        select(ExportProfile).where(
            ExportProfile.id == profile_uuid, ExportProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return {
        "type": "custom",
        "id": str(profile.id),
        "name": profile.name,
        "description": profile.description,
        "format": profile.format,
        "compile_type": profile.compile_type,
        "format_style": profile.format_style,
        "options": profile.options,
        "front_matter_blocks": profile.front_matter_blocks,
        "back_matter_blocks": profile.back_matter_blocks,
        "naming_pattern": profile.naming_pattern,
        "project_type": profile.project_type,
    }


class ExportProfileUpdate(BaseModel):
    """Update export profile."""

    name: str | None = None
    description: str | None = None
    format: str | None = None
    compile_type: str | None = None
    format_style: str | None = None
    options: dict | None = None
    front_matter_blocks: list[dict] | None = None
    back_matter_blocks: list[dict] | None = None
    naming_pattern: str | None = None
    project_type: str | None = None


@router.put("/profiles/{profile_id}")
async def update_export_profile(
    profile_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: ExportProfileUpdate,
):
    """Update custom export profile."""
    try:
        profile_uuid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    result = await db.execute(
        select(ExportProfile).where(
            ExportProfile.id == profile_uuid, ExportProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile or profile.is_system:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    if body.name is not None:
        profile.name = body.name
    if body.description is not None:
        profile.description = body.description
    if body.format is not None:
        profile.format = body.format
    if body.compile_type is not None:
        profile.compile_type = body.compile_type
    if body.format_style is not None:
        profile.format_style = body.format_style
    if body.options is not None:
        profile.options = body.options
    if body.front_matter_blocks is not None:
        profile.front_matter_blocks = body.front_matter_blocks
    if body.back_matter_blocks is not None:
        profile.back_matter_blocks = body.back_matter_blocks
    if body.naming_pattern is not None:
        profile.naming_pattern = body.naming_pattern
    if body.project_type is not None:
        profile.project_type = body.project_type
    await db.commit()
    return {"id": str(profile.id), "name": profile.name}


@router.delete("/profiles/{profile_id}")
async def delete_export_profile(
    profile_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete custom export profile."""
    try:
        profile_uuid = uuid.UUID(profile_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    result = await db.execute(
        select(ExportProfile).where(
            ExportProfile.id == profile_uuid, ExportProfile.user_id == current_user.id
        )
    )
    profile = result.scalar_one_or_none()
    if not profile or profile.is_system:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    await db.delete(profile)
    await db.commit()
    return {"deleted": True}


@router.post("/profiles/{profile_id}/duplicate")
async def duplicate_export_profile(
    profile_id: str,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    new_name: str | None = Query(None),
):
    """Duplicate a custom or system profile as a new custom profile."""
    system = get_system_preset(profile_id)
    if system:
        profile = ExportProfile(
            user_id=current_user.id,
            name=new_name or f"{system['name']} (Copy)",
            description=system.get("description"),
            is_system=False,
            system_key=system.get("system_key"),
            format=system.get("format", "docx"),
            compile_type=system.get("compile_type", "full"),
            format_style=system.get("format_style", "manuscript"),
            options=system.get("options"),
            naming_pattern=system.get("naming_pattern"),
            project_type=system.get("project_type"),
        )
    else:
        try:
            profile_uuid = uuid.UUID(profile_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        result = await db.execute(
            select(ExportProfile).where(
                ExportProfile.id == profile_uuid, ExportProfile.user_id == current_user.id
            )
        )
        orig = result.scalar_one_or_none()
        if not orig:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        profile = ExportProfile(
            user_id=current_user.id,
            name=new_name or f"{orig.name} (Copy)",
            description=orig.description,
            is_system=False,
            format=orig.format,
            compile_type=orig.compile_type,
            format_style=orig.format_style,
            options=orig.options,
            front_matter_blocks=orig.front_matter_blocks,
            back_matter_blocks=orig.back_matter_blocks,
            naming_pattern=orig.naming_pattern,
            project_type=orig.project_type,
        )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return {"id": str(profile.id), "name": profile.name}


@router.get("/books/{book_id}/packages/synopsis")
async def export_synopsis_package_route(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    author_name: str | None = Query(None),
):
    """Export synopsis as DOCX."""
    book = await get_book_with_chapters(db, book_id, current_user.id)
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    settings = get_settings()
    if not settings.openai_api_key and not settings.anthropic_api_key:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="AI not configured")

    synopsis = await generate_synopsis(db, book_id)
    content = export_synopsis_package(synopsis, book.title, author_name or "Author")
    filename = get_export_filename(book.title, "docx", suffix="_synopsis")
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
