"""Notes API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404, get_project_or_404
from authora.database import get_db
from authora.infrastructure.storage.factory import get_storage_provider
from authora.models import Book, Chapter, Note, NoteAttachment, Project
from authora.services.file_validation import validate_file_upload
from authora.schemas.note import NoteCreate, NoteLinkChapter, NoteResponse, NoteUpdate
from authora.services.notes import normalize_tags, note_content_to_draft, search_notes

router = APIRouter(tags=["notes"])

# Project-level notes
project_router = APIRouter(prefix="/projects/{project_id}/notes", tags=["notes"])


async def get_note_or_404(
    db: AsyncSession, note_id: uuid.UUID, project_id: uuid.UUID, user_id: uuid.UUID
) -> Note:
    result = await db.execute(
        select(Note)
        .options(selectinload(Note.attachments))
        .where(Note.id == note_id, Note.project_id == project_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note


def _note_to_response(note: Note) -> NoteResponse:
    return NoteResponse.model_validate(note)


# --- Project-level notes ---


@project_router.get("", response_model=list[NoteResponse])
async def list_project_notes(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str | None = Query(None, description="Search query"),
    note_type: str | None = Query(None, description="Filter by type"),
    book_id: uuid.UUID | None = Query(None),
    chapter_id: uuid.UUID | None = Query(None),
    pinned: bool | None = Query(None),
    is_inspiration: bool | None = Query(None),
    category: str | None = Query(None),
    tags: list[str] | None = Query(None),
):
    """List notes for project (with optional search and filters)."""
    await get_project_or_404(db, project_id, current_user.id)
    notes = await search_notes(
        db,
        project_id,
        q=q,
        note_type=note_type,
        book_id=book_id,
        chapter_id=chapter_id,
        pinned=pinned,
        is_inspiration=is_inspiration,
        category=category,
        tags=tags,
    )
    return [_note_to_response(n) for n in notes]


@project_router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_project_note(
    project_id: uuid.UUID,
    data: NoteCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create note (project-level or book-linked)."""
    await get_project_or_404(db, project_id, current_user.id)
    book_id = data.book_id
    chapter_id = data.chapter_id
    if chapter_id and not book_id:
        result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
        ch = result.scalar_one_or_none()
        if ch:
            book_id = ch.book_id
    note = Note(
        project_id=project_id,
        book_id=book_id,
        chapter_id=chapter_id,
        user_id=current_user.id,
        title=data.title,
        content=data.content,
        note_type=data.note_type,
        source=data.source,
        source_url=data.source_url,
        pinned=data.pinned,
        is_inspiration=data.is_inspiration,
        category=data.category,
        tags=normalize_tags(data.tags),
    )
    db.add(note)
    await db.flush()
    await db.refresh(note)
    await db.run_sync(lambda s: selectinload(Note.attachments).load(note))
    return _note_to_response(note)


@project_router.get("/search", response_model=list[NoteResponse])
async def search_project_notes(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    q: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=100),
):
    """Full-text search notes."""
    await get_project_or_404(db, project_id, current_user.id)
    notes = await search_notes(db, project_id, q=q, limit=limit)
    return [_note_to_response(n) for n in notes]


@project_router.get("/{note_id}", response_model=NoteResponse)
async def get_project_note(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get note by ID."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    return _note_to_response(note)


@project_router.patch("/{note_id}", response_model=NoteResponse)
async def update_project_note(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    data: NoteUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update note."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    if data.title is not None:
        note.title = data.title
    if data.content is not None:
        note.content = data.content
    if data.note_type is not None:
        note.note_type = data.note_type
    if data.book_id is not None:
        note.book_id = data.book_id
    if data.chapter_id is not None:
        note.chapter_id = data.chapter_id
    if data.source is not None:
        note.source = data.source
    if data.source_url is not None:
        note.source_url = data.source_url
    if data.pinned is not None:
        note.pinned = data.pinned
    if data.is_inspiration is not None:
        note.is_inspiration = data.is_inspiration
    if data.category is not None:
        note.category = data.category
    if data.tags is not None:
        note.tags = normalize_tags(data.tags)
    await db.flush()
    await db.refresh(note)
    return _note_to_response(note)


@project_router.post("/{note_id}/link-chapter", response_model=NoteResponse)
async def link_note_to_chapter(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    data: NoteLinkChapter,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Link note to chapter (drag into chapter)."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    if data.chapter_id:
        result = await db.execute(
            select(Chapter).join(Book).where(Chapter.id == data.chapter_id, Book.project_id == project_id)
        )
        ch = result.scalar_one_or_none()
        if not ch:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
        note.chapter_id = data.chapter_id
        note.book_id = ch.book_id
    else:
        note.chapter_id = None
    await db.flush()
    await db.refresh(note)
    return _note_to_response(note)


@project_router.post("/{note_id}/pin", response_model=NoteResponse)
async def pin_note(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Pin note."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    note.pinned = True
    await db.flush()
    await db.refresh(note)
    return _note_to_response(note)


@project_router.post("/{note_id}/unpin", response_model=NoteResponse)
async def unpin_note(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Unpin note."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    note.pinned = False
    await db.flush()
    await db.refresh(note)
    return _note_to_response(note)


@project_router.post("/{note_id}/inspiration", response_model=NoteResponse)
async def set_inspiration(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add to inspiration board."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    note.is_inspiration = True
    await db.flush()
    await db.refresh(note)
    return _note_to_response(note)


@project_router.delete("/{note_id}/inspiration", response_model=NoteResponse)
async def remove_inspiration(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove from inspiration board."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    note.is_inspiration = False
    await db.flush()
    await db.refresh(note)
    return _note_to_response(note)


@project_router.post("/{note_id}/attachments", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    file: UploadFile,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Upload file attachment to note."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    content = await file.read()
    filename = file.filename or "attachment"
    valid, err = validate_file_upload(
        filename=filename,
        content_type=file.content_type,
        content_length=len(content),
    )
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err or "File validation failed",
        )
    content_type = file.content_type
    key = f"notes/{project_id}/{note_id}/{uuid.uuid4()}_{filename}"
    storage = get_storage_provider()
    await storage.put(key, content, content_type=content_type)
    attachment = NoteAttachment(
        note_id=note.id,
        file_key=key,
        filename=filename,
        content_type=content_type,
        file_size=len(content),
    )
    db.add(attachment)
    await db.flush()
    await db.refresh(note)
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    return _note_to_response(note)


@project_router.get("/{note_id}/attachments/{attachment_id}")
async def download_attachment(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    attachment_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Download attachment."""
    await get_note_or_404(db, note_id, project_id, current_user.id)
    result = await db.execute(
        select(NoteAttachment).where(
            NoteAttachment.id == attachment_id,
            NoteAttachment.note_id == note_id,
        )
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
    storage = get_storage_provider()
    content = await storage.get(att.file_key)
    return Response(
        content=content,
        media_type=att.content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{att.filename}"'},
    )


@project_router.get("/{note_id}/to-draft")
async def get_note_as_draft(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get note content formatted for insertion into chapter draft."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    return {"content": note_content_to_draft(note)}


@project_router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_note(
    project_id: uuid.UUID,
    note_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete note."""
    note = await get_note_or_404(db, note_id, project_id, current_user.id)
    await db.delete(note)


# --- Book-level notes (legacy path, delegates to project) ---
book_router = APIRouter(prefix="/projects/{project_id}/books/{book_id}/notes", tags=["notes"])


@book_router.get("", response_model=list[NoteResponse])
async def list_book_notes(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List notes for book."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    notes = await search_notes(db, project_id, book_id=book_id)
    return [_note_to_response(n) for n in notes]


@book_router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_book_note(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: NoteCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create note for book."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    create_data = NoteCreate(
        **data.model_dump(),
        book_id=book_id,
        chapter_id=data.chapter_id,
    )
    return await create_project_note(project_id, create_data, current_user, db)
