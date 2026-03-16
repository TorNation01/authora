"""Revision pass API routes."""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404, get_project_or_404
from authora.database import get_db
from authora.models import (
    Chapter,
    ContentComment,
    RevisionChecklistItem,
    RevisionPass,
    RevisionPassChapter,
)
from authora.schemas.revision_pass import (
    RevisionChecklistItemCreate,
    RevisionChecklistItemResponse,
    RevisionPassCreate,
    RevisionPassResponse,
    RevisionPassSummaryResponse,
    RevisionPassUpdate,
)
from authora.services.revision_pass_templates import DEFAULT_CHECKLISTS, REVISION_PASS_LABELS

router = APIRouter(prefix="/projects/{project_id}", tags=["revision-passes"])


@router.get("/revision-passes", response_model=RevisionPassSummaryResponse)
async def list_revision_passes(
    project_id: uuid.UUID,
    book_id: uuid.UUID | None = Query(None, description="Filter by book"),
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List revision passes for project, optionally filtered by book."""
    await get_project_or_404(db, project_id, current_user.id)
    q = select(RevisionPass).where(RevisionPass.project_id == project_id)
    if book_id:
        q = q.where((RevisionPass.book_id.is_(None)) | (RevisionPass.book_id == book_id))
    q = q.order_by(RevisionPass.sort_order, RevisionPass.created_at)
    result = await db.execute(q)
    passes = result.scalars().all()

    out = []
    total_unresolved = 0
    for p in passes:
        chapters = []
        if p.book_id:
            ch_result = await db.execute(
                select(Chapter).where(Chapter.book_id == p.book_id).order_by(Chapter.sort_order)
            )
            chapters = ch_result.scalars().all()
        else:
            from authora.models import Project
            proj = await db.get(Project, project_id)
            if proj and proj.books:
                for book in proj.books:
                    ch_result = await db.execute(
                        select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sort_order)
                    )
                    chapters.extend(ch_result.scalars().all())

        chapter_ids = [c.id for c in chapters]
        completed = 0
        for ch in chapters:
            rpc_result = await db.execute(
                select(RevisionPassChapter).where(
                    RevisionPassChapter.revision_pass_id == p.id,
                    RevisionPassChapter.chapter_id == ch.id,
                )
            )
            rpc = rpc_result.scalar_one_or_none()
            if rpc and rpc.completed_at:
                completed += 1

        unresolved = 0
        if chapter_ids:
            cmt = await db.execute(
                select(func.count(ContentComment.id)).where(
                    ContentComment.chapter_id.in_(chapter_ids),
                    ContentComment.revision_pass_id == p.id,
                    ContentComment.resolved_at.is_(None),
                    ContentComment.parent_id.is_(None),
                )
            )
            unresolved = cmt.scalar() or 0
        total_unresolved += unresolved

        checklist_result = await db.execute(
            select(RevisionChecklistItem)
            .where(RevisionChecklistItem.revision_pass_id == p.id)
            .order_by(RevisionChecklistItem.sort_order)
        )
        items = checklist_result.scalars().all()

        resp = RevisionPassResponse(
            id=p.id,
            project_id=p.project_id,
            book_id=p.book_id,
            pass_type=p.pass_type,
            name=p.name,
            sort_order=p.sort_order,
            completed_at=p.completed_at,
            created_at=p.created_at,
            updated_at=p.updated_at,
            chapters_total=len(chapters),
            chapters_completed=completed,
            unresolved_comments=unresolved,
            checklist_items=[RevisionChecklistItemResponse.model_validate(i) for i in items],
        )
        out.append(resp)

    return RevisionPassSummaryResponse(passes=out, total_unresolved=total_unresolved)


@router.post("/revision-passes", response_model=RevisionPassResponse, status_code=status.HTTP_201_CREATED)
async def create_revision_pass(
    project_id: uuid.UUID,
    data: RevisionPassCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a revision pass. If book_id is provided, scope to that book; otherwise project-wide."""
    await get_project_or_404(db, project_id, current_user.id)
    if data.book_id:
        await get_book_or_404(db, data.book_id, current_user.id, project_id)

    result = await db.execute(
        select(func.max(RevisionPass.sort_order)).where(RevisionPass.project_id == project_id)
    )
    max_order = result.scalar() or 0

    name = data.name or REVISION_PASS_LABELS.get(data.pass_type, data.pass_type)
    pass_obj = RevisionPass(
        project_id=project_id,
        book_id=data.book_id,
        pass_type=data.pass_type,
        name=name if data.pass_type == "custom" else None,
        sort_order=max_order + 1,
    )
    db.add(pass_obj)
    await db.flush()

    # Generate checklist items from template
    for i, title in enumerate(DEFAULT_CHECKLISTS.get(data.pass_type, [])):
        item = RevisionChecklistItem(
            revision_pass_id=pass_obj.id,
            title=title,
            sort_order=i,
        )
        db.add(item)

    await db.flush()
    await db.refresh(pass_obj)

    checklist_result = await db.execute(
        select(RevisionChecklistItem)
        .where(RevisionChecklistItem.revision_pass_id == pass_obj.id)
        .order_by(RevisionChecklistItem.sort_order)
    )
    items = checklist_result.scalars().all()

    return RevisionPassResponse(
        id=pass_obj.id,
        project_id=pass_obj.project_id,
        book_id=pass_obj.book_id,
        pass_type=pass_obj.pass_type,
        name=pass_obj.name,
        sort_order=pass_obj.sort_order,
        completed_at=pass_obj.completed_at,
        created_at=pass_obj.created_at,
        updated_at=pass_obj.updated_at,
        chapters_total=0,
        chapters_completed=0,
        unresolved_comments=0,
        checklist_items=[RevisionChecklistItemResponse.model_validate(i) for i in items],
    )


@router.get("/revision-passes/{pass_id}", response_model=RevisionPassResponse)
async def get_revision_pass(
    project_id: uuid.UUID,
    pass_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a revision pass by ID."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(RevisionPass).where(
            RevisionPass.id == pass_id,
            RevisionPass.project_id == project_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision pass not found")

    chapters = []
    if p.book_id:
        ch_result = await db.execute(
            select(Chapter).where(Chapter.book_id == p.book_id).order_by(Chapter.sort_order)
        )
        chapters = ch_result.scalars().all()
    else:
        from authora.models import Project
        proj = await db.get(Project, project_id)
        if proj and proj.books:
            for book in proj.books:
                ch_result = await db.execute(
                    select(Chapter).where(Chapter.book_id == book.id).order_by(Chapter.sort_order)
                )
                chapters.extend(ch_result.scalars().all())

    chapter_ids = [c.id for c in chapters]
    completed = 0
    for ch in chapters:
        rpc_result = await db.execute(
            select(RevisionPassChapter).where(
                RevisionPassChapter.revision_pass_id == p.id,
                RevisionPassChapter.chapter_id == ch.id,
            )
        )
        r = rpc_result.scalar_one_or_none()
        if r and r.completed_at:
            completed += 1

    unresolved = 0
    if chapter_ids:
        cmt = await db.execute(
            select(func.count(ContentComment.id)).where(
                ContentComment.chapter_id.in_(chapter_ids),
                ContentComment.revision_pass_id == p.id,
                ContentComment.resolved_at.is_(None),
                ContentComment.parent_id.is_(None),
            )
        )
        unresolved = cmt.scalar() or 0

    checklist_result = await db.execute(
        select(RevisionChecklistItem)
        .where(RevisionChecklistItem.revision_pass_id == p.id)
        .order_by(RevisionChecklistItem.sort_order)
    )
    items = checklist_result.scalars().all()

    return RevisionPassResponse(
        id=p.id,
        project_id=p.project_id,
        book_id=p.book_id,
        pass_type=p.pass_type,
        name=p.name,
        sort_order=p.sort_order,
        completed_at=p.completed_at,
        created_at=p.created_at,
        updated_at=p.updated_at,
        chapters_total=len(chapters),
        chapters_completed=completed,
        unresolved_comments=unresolved,
        checklist_items=[RevisionChecklistItemResponse.model_validate(i) for i in items],
    )


@router.patch("/revision-passes/{pass_id}", response_model=RevisionPassResponse)
async def update_revision_pass(
    project_id: uuid.UUID,
    pass_id: uuid.UUID,
    data: RevisionPassUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a revision pass."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(RevisionPass).where(
            RevisionPass.id == pass_id,
            RevisionPass.project_id == project_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision pass not found")

    if data.name is not None:
        p.name = data.name
    if data.sort_order is not None:
        p.sort_order = data.sort_order
    if data.completed is not None:
        p.completed_at = datetime.now(timezone.utc) if data.completed else None

    await db.flush()
    await db.refresh(p)
    return await get_revision_pass(project_id, pass_id, current_user, db)


@router.delete("/revision-passes/{pass_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_revision_pass(
    project_id: uuid.UUID,
    pass_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a revision pass."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(RevisionPass).where(
            RevisionPass.id == pass_id,
            RevisionPass.project_id == project_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision pass not found")
    await db.delete(p)


@router.post(
    "/revision-passes/{pass_id}/chapters/{chapter_id}/complete",
    status_code=status.HTTP_200_OK,
)
async def mark_chapter_complete(
    project_id: uuid.UUID,
    pass_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Mark a chapter as complete for a revision pass."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(RevisionPass).where(
            RevisionPass.id == pass_id,
            RevisionPass.project_id == project_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision pass not found")

    ch_result = await db.execute(select(Chapter).where(Chapter.id == chapter_id))
    ch = ch_result.scalar_one_or_none()
    if not ch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    if p.book_id and ch.book_id != p.book_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Chapter not in pass scope")

    rpc_result = await db.execute(
        select(RevisionPassChapter).where(
            RevisionPassChapter.revision_pass_id == pass_id,
            RevisionPassChapter.chapter_id == chapter_id,
        )
    )
    rpc = rpc_result.scalar_one_or_none()
    if not rpc:
        rpc = RevisionPassChapter(
            revision_pass_id=pass_id,
            chapter_id=chapter_id,
            completed_at=datetime.now(timezone.utc),
        )
        db.add(rpc)
    else:
        rpc.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return {"completed": True}


@router.post(
    "/revision-passes/{pass_id}/chapters/{chapter_id}/incomplete",
    status_code=status.HTTP_200_OK,
)
async def mark_chapter_incomplete(
    project_id: uuid.UUID,
    pass_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Mark a chapter as incomplete for a revision pass."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(RevisionPassChapter).where(
            RevisionPassChapter.revision_pass_id == pass_id,
            RevisionPassChapter.chapter_id == chapter_id,
        )
    )
    rpc = result.scalar_one_or_none()
    if rpc:
        rpc.completed_at = None
        await db.flush()
    return {"completed": False}


@router.post(
    "/revision-passes/{pass_id}/checklist-items",
    response_model=RevisionChecklistItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_checklist_item(
    project_id: uuid.UUID,
    pass_id: uuid.UUID,
    data: RevisionChecklistItemCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Add a checklist item to a revision pass."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(RevisionPass).where(
            RevisionPass.id == pass_id,
            RevisionPass.project_id == project_id,
        )
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision pass not found")

    max_order = 0
    for item in p.checklist_items:
        if item.sort_order >= max_order:
            max_order = item.sort_order + 1

    item = RevisionChecklistItem(
        revision_pass_id=pass_id,
        title=data.title,
        sort_order=data.sort_order if data.sort_order > 0 else max_order,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return RevisionChecklistItemResponse.model_validate(item)


@router.delete(
    "/revision-passes/{pass_id}/checklist-items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_checklist_item(
    project_id: uuid.UUID,
    pass_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Remove a checklist item."""
    await get_project_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(RevisionChecklistItem).where(
            RevisionChecklistItem.id == item_id,
            RevisionChecklistItem.revision_pass_id == pass_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Checklist item not found")
    await db.delete(item)
