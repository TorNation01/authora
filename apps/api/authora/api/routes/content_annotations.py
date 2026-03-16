"""Content highlights and comments API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404
from authora.database import get_db
from authora.models import Chapter, ContentComment, ContentHighlight
from authora.schemas.content_annotation import (
    ContentCommentCreate,
    ContentCommentResponse,
    ContentCommentUpdate,
    ContentHighlightCreate,
    ContentHighlightResponse,
)

router = APIRouter(
    prefix="/projects/{project_id}/books/{book_id}",
    tags=["content-annotations"],
)


# --- Highlights ---


@router.get("/chapters/{chapter_id}/highlights", response_model=list[ContentHighlightResponse])
async def list_highlights(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List highlights for a chapter."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    result = await db.execute(
        select(ContentHighlight)
        .where(ContentHighlight.chapter_id == chapter_id, ContentHighlight.user_id == current_user.id)
        .order_by(ContentHighlight.start_offset)
    )
    return [ContentHighlightResponse.model_validate(h) for h in result.scalars().all()]


@router.post(
    "/chapters/{chapter_id}/highlights",
    response_model=ContentHighlightResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_highlight(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ContentHighlightCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create highlight on chapter content."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    if data.start_offset >= data.end_offset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="start_offset must be less than end_offset")
    highlight = ContentHighlight(
        user_id=current_user.id,
        chapter_id=chapter_id,
        start_offset=data.start_offset,
        end_offset=data.end_offset,
        color=data.color,
    )
    db.add(highlight)
    await db.flush()
    await db.refresh(highlight)
    return ContentHighlightResponse.model_validate(highlight)


@router.delete("/chapters/{chapter_id}/highlights/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_highlight(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    highlight_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete highlight."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(ContentHighlight).where(
            ContentHighlight.id == highlight_id,
            ContentHighlight.chapter_id == chapter_id,
            ContentHighlight.user_id == current_user.id,
        )
    )
    h = result.scalar_one_or_none()
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Highlight not found")
    await db.delete(h)


# --- Comments ---


@router.get("/chapters/{chapter_id}/comments", response_model=list[ContentCommentResponse])
async def list_comments(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    unresolved_only: bool = Query(False, description="Filter to unresolved comments"),
    revision_pass_id: uuid.UUID | None = Query(None, description="Filter by revision pass"),
):
    """List comments for a chapter (top-level, with replies nested)."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    q = (
        select(ContentComment)
        .where(
            ContentComment.chapter_id == chapter_id,
            ContentComment.user_id == current_user.id,
            ContentComment.parent_id.is_(None),
        )
    )
    if revision_pass_id is not None:
        q = q.where(ContentComment.revision_pass_id == revision_pass_id)
    result = await db.execute(q.order_by(ContentComment.created_at))
    roots = result.scalars().all()
    if unresolved_only:
        roots = [r for r in roots if r.resolved_at is None]
    out = []
    for r in roots:
        data = ContentCommentResponse.model_validate(r)
        result = await db.execute(
            select(ContentComment)
            .where(ContentComment.parent_id == r.id)
            .order_by(ContentComment.created_at)
        )
        data.replies = [ContentCommentResponse.model_validate(c) for c in result.scalars().all()]
        out.append(data)
    return out


@router.post(
    "/chapters/{chapter_id}/comments",
    response_model=ContentCommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    data: ContentCommentCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create comment on chapter content."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    comment = ContentComment(
        user_id=current_user.id,
        chapter_id=chapter_id,
        parent_id=data.parent_id,
        start_offset=data.start_offset,
        end_offset=data.end_offset,
        body=data.body,
        revision_pass_id=data.revision_pass_id,
    )
    db.add(comment)
    await db.flush()
    await db.refresh(comment)
    return ContentCommentResponse.model_validate(comment)


@router.patch("/chapters/{chapter_id}/comments/{comment_id}", response_model=ContentCommentResponse)
async def update_comment(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    comment_id: uuid.UUID,
    data: ContentCommentUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update comment (body or resolved status)."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(ContentComment).where(
            ContentComment.id == comment_id,
            ContentComment.chapter_id == chapter_id,
            ContentComment.user_id == current_user.id,
        )
    )
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if data.body is not None:
        c.body = data.body
    if data.resolved is not None:
        from datetime import datetime, timezone

        c.resolved_at = datetime.now(timezone.utc) if data.resolved else None
    await db.flush()
    await db.refresh(c)
    return ContentCommentResponse.model_validate(c)


@router.delete("/chapters/{chapter_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    comment_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete comment and its replies."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(ContentComment).where(
            ContentComment.id == comment_id,
            ContentComment.chapter_id == chapter_id,
            ContentComment.user_id == current_user.id,
        )
    )
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await db.delete(c)
