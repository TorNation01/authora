"""Story Integrity Engine API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_with_access_or_404
from authora.config import get_settings
from authora.database import get_db
from authora.models import IntegrityIssue, IntegrityScan, Setting
from authora.schemas.integrity import (
    ChapterHealthListResponse,
    ChapterHealthResponse,
    IntegrityFixGuidance,
    IntegrityIssueResponse,
    IntegrityIssueUpdate,
    IntegrityScanCreate,
    IntegrityScanResponse,
    StoryHealthSummary,
)
from authora.services.integrity import get_fix_guidance, run_scan

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}", tags=["integrity"])


async def _story_integrity_enabled(db: AsyncSession) -> bool:
    """Check if Story Integrity Engine is enabled (config + DB override)."""
    settings = get_settings()
    enabled = getattr(settings, "feature_story_integrity", True)
    result = await db.execute(select(Setting).where(Setting.key == "feature.story_integrity"))
    row = result.scalar_one_or_none()
    if row and isinstance(row.value, dict) and "enabled" in row.value:
        enabled = bool(row.value["enabled"])
    return enabled


@router.post("/integrity/scan", response_model=IntegrityScanResponse)
async def create_scan(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: IntegrityScanCreate | None = None,
):
    """Run a story integrity scan on the book."""
    if not await _story_integrity_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Integrity Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    body = body or IntegrityScanCreate()
    try:
        scan = await run_scan(
            db,
            project_id=project_id,
            book_id=book_id,
            scan_type=body.scan_type,
            triggered_by=body.triggered_by,
        )
        await db.commit()
        await db.refresh(scan)
        return scan
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/integrity/scans", response_model=list[IntegrityScanResponse])
async def list_scans(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
):
    """List integrity scans for the book."""
    if not await _story_integrity_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Integrity Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(IntegrityScan)
        .where(IntegrityScan.book_id == book_id)
        .order_by(IntegrityScan.started_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/integrity/issues", response_model=list[IntegrityIssueResponse])
async def list_issues(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    severity: str | None = Query(None, description="Filter by severity"),
    category: str | None = Query(None, description="Filter by category"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    chapter_id: uuid.UUID | None = Query(None, description="Filter by chapter"),
    scan_id: uuid.UUID | None = Query(None, description="Filter by scan"),
    limit: int = Query(100, ge=1, le=500),
):
    """List integrity issues for the book with optional filters."""
    if not await _story_integrity_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Integrity Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    q = select(IntegrityIssue).where(IntegrityIssue.book_id == book_id)
    if severity:
        q = q.where(IntegrityIssue.severity == severity)
    if category:
        q = q.where(IntegrityIssue.category == category)
    if status_filter:
        q = q.where(IntegrityIssue.status == status_filter)
    if chapter_id:
        q = q.where(IntegrityIssue.chapter_id == chapter_id)
    if scan_id:
        q = q.where(IntegrityIssue.scan_id == scan_id)
    q = q.order_by(IntegrityIssue.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/integrity/chapter-health", response_model=ChapterHealthListResponse)
async def get_chapter_health(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get chapter health, pacing, and structure analysis from latest scan."""
    if not await _story_integrity_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Integrity Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)

    last_scan = await db.execute(
        select(IntegrityScan)
        .where(IntegrityScan.book_id == book_id, IntegrityScan.status == "completed")
        .order_by(IntegrityScan.completed_at.desc().nullslast())
        .limit(1)
    )
    scan = last_scan.scalar_one_or_none()
    if not scan or not scan.story_map_snapshot:
        return ChapterHealthListResponse(chapters=[], scan_id=None, last_scan_at=None)

    chapter_health = scan.story_map_snapshot.get("chapter_health", [])
    chapters = [
        ChapterHealthResponse(
            chapter_id=ch.get("chapter_id", ""),
            chapter_index=ch.get("chapter_index", 0),
            title=ch.get("title", "Untitled"),
            word_count=ch.get("word_count", 0),
            health=ch.get("health", "stable"),
            health_reason=ch.get("health_reason", ""),
            purpose_clarity=ch.get("purpose_clarity", 0.5),
            relationship_to_manuscript=ch.get("relationship_to_manuscript", 0.5),
            tension_level=ch.get("tension_level", 0.5),
            emotional_movement=ch.get("emotional_movement", 0.5),
            plot_movement=ch.get("plot_movement", 0.5),
            information_density=ch.get("information_density", 0.5),
            pacing=ch.get("pacing", 0.5),
            transition_quality=ch.get("transition_quality", 0.5),
            opening_strength=ch.get("opening_strength", 0.5),
            closing_strength=ch.get("closing_strength", 0.5),
            chapter_linkage=ch.get("chapter_linkage", 0.5),
            repetition=ch.get("repetition", 0),
            unresolved_internal=ch.get("unresolved_internal", 0),
            what_this_chapter_is_doing=ch.get("what_this_chapter_is_doing", ""),
            why_feels_off=ch.get("why_feels_off"),
            suggested_fixes=[
                {"action": f.get("action", ""), "label": f.get("label", "")}
                for f in ch.get("suggested_fixes", [])
            ],
            issues=[
                {
                    "type": i.get("type", ""),
                    "severity": i.get("severity", "low"),
                    "title": i.get("title", ""),
                    "suggestion": i.get("suggestion", ""),
                }
                for i in ch.get("issues", [])
            ],
        )
        for ch in chapter_health
    ]
    return ChapterHealthListResponse(
        chapters=chapters,
        scan_id=str(scan.id),
        last_scan_at=scan.completed_at,
    )


@router.get("/integrity/health", response_model=StoryHealthSummary)
async def get_story_health(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get story health summary for dashboard."""
    if not await _story_integrity_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Integrity Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)

    issues_q = select(IntegrityIssue).where(IntegrityIssue.book_id == book_id)
    result = await db.execute(issues_q)
    issues = list(result.scalars().all())

    last_scan = await db.execute(
        select(IntegrityScan)
        .where(IntegrityScan.book_id == book_id, IntegrityScan.status == "completed")
        .order_by(IntegrityScan.completed_at.desc().nullslast())
        .limit(1)
    )
    last = last_scan.scalar_one_or_none()

    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    open_count = 0
    for i in issues:
        by_severity[i.severity] = by_severity.get(i.severity, 0) + 1
        by_category[i.category] = by_category.get(i.category, 0) + 1
        if i.status == "open":
            open_count += 1

    return StoryHealthSummary(
        total_issues=len(issues),
        by_severity=by_severity,
        by_category=by_category,
        open_count=open_count,
        last_scan_at=last.completed_at if last else None,
        last_scan_issue_count=last.issue_count if last else None,
    )


@router.get("/integrity/issues/{issue_id}", response_model=IntegrityIssueResponse)
async def get_issue(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single issue by ID."""
    if not await _story_integrity_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Integrity Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(IntegrityIssue).where(
            IntegrityIssue.id == issue_id,
            IntegrityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue


@router.patch("/integrity/issues/{issue_id}", response_model=IntegrityIssueResponse)
async def update_issue(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    body: IntegrityIssueUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update issue status (resolve, ignore, mark intentional)."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(IntegrityIssue).where(
            IntegrityIssue.id == issue_id,
            IntegrityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    if body.status:
        if body.status not in ("open", "resolved", "ignored", "intentional"):
            raise HTTPException(status_code=400, detail="Invalid status")
        issue.status = body.status
        if body.status == "resolved":
            from datetime import datetime, timezone

            issue.resolved_at = datetime.now(timezone.utc)
            issue.resolved_by = current_user.id
        elif body.status == "intentional":
            from datetime import datetime, timezone

            issue.marked_intentional_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(issue)
    return issue


@router.get("/integrity/issues/{issue_id}/guidance", response_model=IntegrityFixGuidance)
async def get_issue_guidance(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get guided fix suggestions for an issue."""
    if not await _story_integrity_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Integrity Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(IntegrityIssue).where(
            IntegrityIssue.id == issue_id,
            IntegrityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    issue_dict = {
        "fix_suggestions": issue.fix_suggestions,
    }
    guidance = get_fix_guidance(issue.issue_type, issue_dict)
    return IntegrityFixGuidance(**guidance)
