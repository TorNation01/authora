"""Content highlights and comments API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_with_access_or_404, get_project_with_access_or_404
from authora.models.collaboration import PERMISSION_COMMENT, has_permission
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
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
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
    """Create highlight on chapter content. Requires comment permission."""
    _, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_comment_permission(role)
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
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
    """Delete highlight. Requires comment permission."""
    _, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_comment_permission(role)
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
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


@router.get("/comments", response_model=list[ContentCommentResponse])
async def list_book_comments(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    chapter_id: uuid.UUID | None = Query(None, description="Filter by chapter"),
    user_id: uuid.UUID | None = Query(None, description="Filter by user"),
    tag: str | None = Query(None, alias="comment_type", description="Filter by tag"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    role: str | None = Query(None, description="Filter by collaboration_role"),
    unresolved_only: bool = Query(False, description="Filter to unresolved"),
):
    """List comments across all chapters in a book. Supports filtering by chapter, user, tag, role, status."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    q = (
        select(ContentComment)
        .join(Chapter, ContentComment.chapter_id == Chapter.id)
        .where(Chapter.book_id == book_id, ContentComment.parent_id.is_(None))
    )
    if chapter_id is not None:
        q = q.where(ContentComment.chapter_id == chapter_id)
    if user_id is not None:
        q = q.where(ContentComment.user_id == user_id)
    if tag is not None:
        q = q.where(ContentComment.comment_type == tag)
    if status_filter is not None:
        q = q.where(ContentComment.status == status_filter)
    if role is not None:
        q = q.where(ContentComment.collaboration_role == role)
    result = await db.execute(q.order_by(ContentComment.created_at))
    roots = result.scalars().all()
    if unresolved_only:
        roots = [r for r in roots if r.resolved_at is None]
    from authora.models import User

    def _comment_to_response(c: ContentComment) -> ContentCommentResponse:
        d = ContentCommentResponse.model_validate(c)
        d.user_id = c.user_id
        return d

    async def _with_user_info(comments: list) -> list[ContentCommentResponse]:
        out_list = []
        for r in comments:
            data = _comment_to_response(r)
            if r.user_id:
                u = await db.get(User, r.user_id)
                if u:
                    data.user_email = u.email
                    data.user_display_name = u.display_name
            result = await db.execute(
                select(ContentComment)
                .where(ContentComment.parent_id == r.id)
                .order_by(ContentComment.created_at)
            )
            replies = result.scalars().all()
            data.replies = []
            for reply in replies:
                rd = _comment_to_response(reply)
                if reply.user_id:
                    u = await db.get(User, reply.user_id)
                    if u:
                        rd.user_email = u.email
                        rd.user_display_name = u.display_name
                data.replies.append(rd)
            out_list.append(data)
        return out_list

    return await _with_user_info(roots)


@router.get("/chapters/{chapter_id}/comments", response_model=list[ContentCommentResponse])
async def list_comments(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    unresolved_only: bool = Query(False, description="Filter to unresolved comments"),
    revision_pass_id: uuid.UUID | None = Query(None, description="Filter by revision pass"),
    user_id: uuid.UUID | None = Query(None, description="Filter by reviewer/user who wrote the comment"),
    tag: str | None = Query(None, alias="comment_type", description="Filter by comment tag"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status: open, in_review, resolved, deferred, needs_decision"),
    role: str | None = Query(None, description="Filter by collaboration_role"),
):
    """List comments for a chapter (top-level, with replies nested). Returns all collaborators' comments."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.book_id == book_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    q = (
        select(ContentComment)
        .where(
            ContentComment.chapter_id == chapter_id,
            ContentComment.parent_id.is_(None),
        )
    )
    if revision_pass_id is not None:
        q = q.where(ContentComment.revision_pass_id == revision_pass_id)
    if user_id is not None:
        q = q.where(ContentComment.user_id == user_id)
    if tag is not None:
        q = q.where(ContentComment.comment_type == tag)
    if status_filter is not None:
        q = q.where(ContentComment.status == status_filter)
    if role is not None:
        q = q.where(ContentComment.collaboration_role == role)
    result = await db.execute(q.order_by(ContentComment.created_at))
    roots = result.scalars().all()
    if unresolved_only:
        roots = [r for r in roots if r.resolved_at is None]
    from authora.models import User

    def _comment_to_response(c: ContentComment) -> ContentCommentResponse:
        d = ContentCommentResponse.model_validate(c)
        d.user_id = c.user_id
        return d

    async def _with_user_info(comments: list) -> list[ContentCommentResponse]:
        out_list = []
        for r in comments:
            data = _comment_to_response(r)
            if r.user_id:
                u = await db.get(User, r.user_id)
                if u:
                    data.user_email = u.email
                    data.user_display_name = u.display_name
            result = await db.execute(
                select(ContentComment)
                .where(ContentComment.parent_id == r.id)
                .order_by(ContentComment.created_at)
            )
            replies = result.scalars().all()
            data.replies = []
            for reply in replies:
                rd = _comment_to_response(reply)
                if reply.user_id:
                    u = await db.get(User, reply.user_id)
                    if u:
                        rd.user_email = u.email
                        rd.user_display_name = u.display_name
                data.replies.append(rd)
            out_list.append(data)
        return out_list

    return await _with_user_info(roots)


def _require_comment_permission(role: str) -> None:
    if not has_permission(role, PERMISSION_COMMENT):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to comment")


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
    """Create comment on chapter content. Requires comment permission."""
    _, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_comment_permission(role)
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
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
        comment_type=getattr(data, "comment_type", None),
        collaboration_role=getattr(data, "collaboration_role", None),
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
    """Update comment (body, tag, status, or resolved). Requires comment permission."""
    _, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_comment_permission(role)
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(ContentComment).where(
            ContentComment.id == comment_id,
            ContentComment.chapter_id == chapter_id,
        )
    )
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    # Body and comment_type: author only; status and resolved: any collaborator with access
    if data.body is not None:
        if c.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the comment author can edit the body")
        c.body = data.body
    if data.comment_type is not None:
        if c.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the comment author can change the tag")
        c.comment_type = data.comment_type
    if data.status is not None:
        c.status = data.status
        if data.status == "resolved":
            from datetime import datetime, timezone
            c.resolved_at = datetime.now(timezone.utc)
        elif c.resolved_at and data.status != "resolved":
            c.resolved_at = None
    if data.resolved is not None:
        from datetime import datetime, timezone
        c.resolved_at = datetime.now(timezone.utc) if data.resolved else None
        c.status = "resolved" if data.resolved else "open"
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
    """Delete comment and its replies. Requires comment permission."""
    _, role = await get_project_with_access_or_404(db, project_id, current_user.id)
    _require_comment_permission(role)
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
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
