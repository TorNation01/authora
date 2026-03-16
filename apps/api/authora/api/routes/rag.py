"""RAG and semantic search API."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status

from authora.api.dependencies import get_current_user
from authora.api.resolvers import get_project_or_404
from authora.database import get_db
from authora.models import User
from authora.services.embedding_service import is_embeddings_configured
from authora.services.rag import semantic_search
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/projects/{project_id}/rag", tags=["rag"])


@router.get("/search")
async def rag_search(
    project_id: uuid.UUID,
    q: str = Query(..., min_length=1),
    book_id: uuid.UUID | None = Query(None),
    source_types: str | None = Query(None, description="Comma-separated: note,chapter,chapter_brief,outline_chapter"),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Semantic search within a project."""
    await get_project_or_404(db, project_id, current_user.id)
    if not is_embeddings_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Semantic search is not configured. Enable embeddings in admin.",
        )
    types = [t.strip() for t in source_types.split(",")] if source_types else None
    results = await semantic_search(
        db,
        project_id,
        q,
        user_id=current_user.id,
        book_id=book_id,
        source_types=types,
        limit=limit,
    )
    return {
        "query": q,
        "results": [
            {
                "source_type": r.source_type,
                "source_id": r.source_id,
                "book_id": r.book_id,
                "chapter_id": r.chapter_id,
                "content_text": r.content_text,
                "chunk_index": r.chunk_index,
                "score": round(r.score, 4),
                "metadata": r.metadata,
            }
            for r in results
        ],
    }


@router.post("/reindex")
async def rag_reindex_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger reindex of project content. Admin or project owner."""
    await get_project_or_404(db, project_id, current_user.id)
    if not is_embeddings_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Embeddings not configured.",
        )
    from authora.services.rag.indexer import reindex_source
    from authora.services.rag.chunker import chunk_note, chunk_chapter, chunk_chapter_brief, chunk_outline
    from authora.services.export import tiptap_to_plain_text
    from authora.models import Note, Book, Chapter, GhostwriterWorkspace, Project
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    indexed = 0
    projects_result = await db.execute(
        select(Project).where(Project.id == project_id, Project.user_id == current_user.id)
    )
    project = projects_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    notes_result = await db.execute(select(Note).where(Note.project_id == project_id, Note.deleted_at.is_(None)))
    for note in notes_result.scalars().all():
        chunks = chunk_note(note.title, note.content or "", str(note.id), str(project_id), str(note.book_id) if note.book_id else None, str(note.chapter_id) if note.chapter_id else None)
        if chunks:
            n = await reindex_source(db, "note", note.id, current_user.id, project_id, chunks, note.book_id)
            indexed += n

    from sqlalchemy.orm import selectinload

    books_result = await db.execute(
        select(Book)
        .options(
            selectinload(Book.chapters),
            selectinload(Book.ghostwriter_workspace).selectinload(GhostwriterWorkspace.chapter_briefs),
        )
        .where(Book.project_id == project_id)
    )
    for book in books_result.scalars().all():
        for ch in sorted(book.chapters, key=lambda c: c.sort_order):
            text = tiptap_to_plain_text(ch.content) if ch.content else ""
            chunks = chunk_chapter(ch.title or "Untitled", text, str(ch.id), str(book.id), str(project_id))
            if chunks:
                n = await reindex_source(db, "chapter", ch.id, current_user.id, project_id, chunks, book.id)
                indexed += n

        gw = book.ghostwriter_workspace
        if gw and gw.outline:
            chunks = chunk_outline(gw.outline, str(book.id), str(project_id))
            if chunks:
                n = await reindex_source(db, "outline_chapter", book.id, current_user.id, project_id, chunks, book.id)
                indexed += n

        if gw:
            for brief in gw.chapter_briefs:
                if brief.brief_text:
                    chunks = chunk_chapter_brief(brief.brief_text, str(brief.id), str(brief.chapter_id), str(book.id), str(project_id))
                    if chunks:
                        n = await reindex_source(db, "chapter_brief", brief.id, current_user.id, project_id, chunks, book.id)
                        indexed += n

    await db.commit()
    return {"indexed": indexed, "message": f"Indexed {indexed} chunks"}
