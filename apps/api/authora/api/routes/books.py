"""Books and chapters API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404, get_project_or_404
from authora.core.audit import AuditLogger
from authora.database import get_db
from authora.models import Book, Chapter, ChapterVersion, Project
from authora.services.finish_mode import get_finish_mode_stats, update_finish_mode_settings
from authora.schemas.book import (
    BookCreate,
    BookResponse,
    BookUpdate,
    BookWithChaptersResponse,
    ChapterCreate,
    ChapterResponse,
    ChapterUpdate,
    ChapterVersionResponse,
    ChaptersReorder,
)

router = APIRouter(prefix="/projects/{project_id}/books", tags=["books"])


def count_words(content: dict) -> int:
    """Count words in TipTap JSON content."""
    text = ""
    if isinstance(content, dict):
        if "content" in content and isinstance(content["content"], list):
            for node in content["content"]:
                if isinstance(node, dict) and "content" in node:
                    for c in node["content"]:
                        if isinstance(c, dict) and "text" in c:
                            text += c.get("text", "") + " "
                elif isinstance(node, dict) and "text" in node:
                    text += node.get("text", "") + " "
    return len(text.split())


@router.get("", response_model=list[BookResponse])
async def list_books(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List books in project."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(select(Book).where(Book.project_id == project_id).order_by(Book.updated_at.desc()))
    books = result.scalars().all()
    return [BookResponse.model_validate(b) for b in books]


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    project_id: uuid.UUID,
    data: BookCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create book in project."""
    from authora.services.billing_service import check_book_limit

    await get_project_or_404(db, project_id, current_user.id)
    allowed, current, limit = await check_book_limit(db, current_user.id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Book limit reached ({current}/{limit}). Upgrade to Premium for more.",
        )
    book = Book(
        project_id=project_id,
        title=data.title,
        genre=data.genre,
        type=data.type,
        planner_data=data.planner_data,
    )
    db.add(book)
    await db.flush()
    audit = AuditLogger(db)
    await audit.log("create", "book", str(book.id), current_user.id, {"title": data.title, "project_id": str(project_id)})
    await db.refresh(book)
    return BookResponse.model_validate(book)


@router.get("/{book_id}", response_model=BookWithChaptersResponse)
async def get_book(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get book with chapters."""
    result = await db.execute(
        select(Book).options(selectinload(Book.chapters)).join(Project).where(Book.id == book_id, Project.user_id == current_user.id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return BookWithChaptersResponse(
        **BookResponse.model_validate(book).model_dump(),
        chapters=[ChapterResponse.model_validate(c) for c in sorted(book.chapters, key=lambda x: x.sort_order)],
    )


@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: BookUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update book."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    if data.title is not None:
        book.title = data.title
    if data.genre is not None:
        book.genre = data.genre
    if data.type is not None:
        book.type = data.type
    if data.planner_data is not None:
        book.planner_data = data.planner_data
    await db.flush()
    await db.refresh(book)
    return BookResponse.model_validate(book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete book."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    await db.delete(book)


# Chapters
@router.post("/{book_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: ChapterCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create chapter."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    chapter = Chapter(
        book_id=book_id,
        title=data.title,
        sort_order=data.sort_order,
        content=data.content,
        word_count=count_words(data.content),
    )
    db.add(chapter)
    await db.flush()
    await db.refresh(chapter)
    return ChapterResponse.model_validate(chapter)


@router.patch("/{book_id}/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ChapterUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update chapter."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    if data.title is not None:
        chapter.title = data.title
    if data.sort_order is not None:
        chapter.sort_order = data.sort_order
    if data.section_status is not None:
        chapter.section_status = data.section_status
        if data.section_status == "done" and chapter.gamification_completed_at is None:
            from authora.services.gamification import record_chapter_complete
            await record_chapter_complete(db, current_user.id, chapter.id, book_id)
    if data.content is not None:
        # Save version before overwriting
        version = ChapterVersion(
            chapter_id=chapter.id,
            content=chapter.content,
            word_count=chapter.word_count,
            content_source=chapter.content_source,
            created_by=current_user.id,
        )
        db.add(version)
        old_count = chapter.word_count
        chapter.content = data.content
        chapter.word_count = count_words(data.content)
        if data.content_source is not None:
            chapter.content_source = data.content_source
        delta = chapter.word_count - old_count
        if delta > 0:
            from authora.services.gamification import record_words
            await record_words(db, current_user.id, delta, book_id)

    await db.flush()
    await db.refresh(chapter)
    return ChapterResponse.model_validate(chapter)


@router.post("/{book_id}/chapters/reorder", response_model=list[ChapterResponse])
async def reorder_chapters(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    data: ChaptersReorder,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Reorder chapters by id list."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order)
    )
    chapters = {c.id: c for c in result.scalars().all()}
    for i, ch_id in enumerate(data.chapter_ids):
        if ch_id in chapters:
            chapters[ch_id].sort_order = i
    await db.flush()
    result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order)
    )
    return [ChapterResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/{book_id}/chapters/{chapter_id}/versions", response_model=list[ChapterVersionResponse])
async def list_chapter_versions(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List version history for a chapter."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    result = await db.execute(
        select(ChapterVersion).where(ChapterVersion.chapter_id == chapter_id).order_by(ChapterVersion.created_at.desc()).limit(50)
    )
    return [ChapterVersionResponse.model_validate(v) for v in result.scalars().all()]


@router.delete("/{book_id}/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete chapter."""
    book = await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id))
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    await db.delete(chapter)


# Finish Mode
@router.get("/{book_id}/finish-mode")
async def get_finish_mode(
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get finish mode stats and settings."""
    stats = await get_finish_mode_stats(db, book_id, current_user.id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return stats


class FinishModeUpdate(BaseModel):
    """Finish mode settings update."""

    enabled: bool | None = None
    target_date: str | None = None
    words_per_day: int | None = None


@router.patch("/{book_id}/finish-mode")
async def patch_finish_mode(
    book_id: uuid.UUID,
    data: FinishModeUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Enable, disable, or update finish mode settings."""
    stats = await update_finish_mode_settings(
        db,
        book_id,
        current_user.id,
        enabled=data.enabled,
        target_date=data.target_date,
        words_per_day=data.words_per_day,
    )
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return stats
