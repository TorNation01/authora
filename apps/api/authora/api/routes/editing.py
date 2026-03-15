"""Editing and polish engine API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_or_404, get_chapter_or_404
from authora.database import get_db
from authora.models import Book, Chapter, EditorialAnalysis, EditorialJob, EditorialSuggestion, Project
from authora.services.editing.engine import (
    build_chapter_scorecard,
    build_manuscript_health,
    run_book_analysis,
    run_chapter_analysis,
)

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}", tags=["editing"])


class AnalysisJobResponse(BaseModel):
    id: str
    scope: str
    status: str
    created_at: str
    completed_at: str | None


class SuggestionAccept(BaseModel):
    accepted: bool


@router.post("/editorial/analyze/chapter/{chapter_id}", response_model=AnalysisJobResponse)
async def analyze_chapter(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Run editorial analysis on a chapter."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    job = await run_chapter_analysis(db, chapter_id, book_id, current_user.id)
    await db.commit()
    return AnalysisJobResponse(
        id=str(job.id),
        scope=job.scope,
        status=job.status,
        created_at=job.created_at.isoformat(),
        completed_at=job.completed_at.isoformat() if job.completed_at else None,
    )


@router.post("/editorial/analyze/book", response_model=list[AnalysisJobResponse])
async def analyze_book(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Run editorial analysis on all chapters."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    jobs = await run_book_analysis(db, book_id, current_user.id)
    await db.commit()
    return [
        AnalysisJobResponse(
            id=str(j.id),
            scope=j.scope,
            status=j.status,
            created_at=j.created_at.isoformat(),
            completed_at=j.completed_at.isoformat() if j.completed_at else None,
        )
        for j in jobs
    ]


@router.get("/editorial/chapter/{chapter_id}/scorecard")
async def get_chapter_scorecard(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get chapter editorial scorecard."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(EditorialAnalysis).where(EditorialAnalysis.chapter_id == chapter_id)
    )
    analyses = list(result.scalars().all())
    scorecard = build_chapter_scorecard(analyses)
    return scorecard


@router.get("/editorial/manuscript-health")
async def get_manuscript_health(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get manuscript health dashboard."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(Chapter).where(Chapter.book_id == book_id).order_by(Chapter.sort_order)
    )
    chapters = list(result.scalars().all())
    chapters_data = []
    for ch in chapters:
        r = await db.execute(select(EditorialAnalysis).where(EditorialAnalysis.chapter_id == ch.id))
        analyses = list(r.scalars().all())
        scorecard = build_chapter_scorecard(analyses)
        scorecard["chapter_id"] = str(ch.id)
        scorecard["chapter_title"] = ch.title
        chapters_data.append(scorecard)
    return build_manuscript_health(chapters_data)


@router.get("/editorial/chapter/{chapter_id}/suggestions")
async def get_chapter_suggestions(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get inline suggestions for a chapter."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    await get_chapter_or_404(db, book_id, chapter_id)
    result = await db.execute(
        select(EditorialSuggestion)
        .where(EditorialSuggestion.chapter_id == chapter_id, EditorialSuggestion.status == "pending")
    )
    suggestions = list(result.scalars().all())
    return [
        {
            "id": str(s.id),
            "type": s.suggestion_type,
            "original_text": s.original_text,
            "suggested_text": s.suggested_text,
            "position_start": s.position_start,
            "position_end": s.position_end,
            "status": s.status,
        }
        for s in suggestions
    ]


@router.post("/editorial/chapter/{chapter_id}/snapshot")
async def create_snapshot(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create before/after snapshot (call before applying edits)."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    chapter = await get_chapter_or_404(db, book_id, chapter_id)
    from authora.models import EditorialSnapshot
    snapshot = EditorialSnapshot(
        chapter_id=chapter_id,
        content_before=chapter.content,
        content_after=None,
        snapshot_type="pre_edit",
    )
    db.add(snapshot)
    await db.flush()
    await db.commit()
    return {"id": str(snapshot.id), "created_at": snapshot.created_at.isoformat()}


@router.post("/editorial/suggestions/{suggestion_id}/accept")
async def accept_suggestion(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    suggestion_id: uuid.UUID,
    data: SuggestionAccept,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Accept or reject an inline suggestion."""
    await get_book_or_404(db, book_id, current_user.id, project_id)
    result = await db.execute(
        select(EditorialSuggestion, Chapter).join(
            Chapter, EditorialSuggestion.chapter_id == Chapter.id
        ).where(
            EditorialSuggestion.id == suggestion_id,
            Chapter.book_id == book_id,
        )
    )
    row = result.one_or_none()
    suggestion = row[0] if row else None
    if not suggestion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Suggestion not found")
    from datetime import datetime, timezone
    if data.accepted:
        suggestion.status = "accepted"
        suggestion.accepted_at = datetime.now(timezone.utc)
    else:
        suggestion.status = "rejected"
        suggestion.rejected_at = datetime.now(timezone.utc)
    await db.flush()
    await db.commit()
    return {"status": suggestion.status}
