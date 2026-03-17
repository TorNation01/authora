"""Story Density Engine API routes."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_book_with_access_or_404
from authora.config import get_settings
from authora.database import get_db
from authora.models import (
    DensityIssue,
    DensityScan,
    RevisionChecklistItem,
    RevisionPass,
    Setting,
)
from pydantic import BaseModel, Field

from authora.schemas.density import (
    DensityFixGuidance,
    DensityHealthSummary,
    DensityIssueResponse,
    DensityIssueUpdate,
    DensityScanCreate,
    DensityScanResponse,
)
from authora.services.density import (
    decide_action,
    get_alternatives_comparison,
    get_density_fix_guidance,
    run_density_scan,
)

router = APIRouter(prefix="/projects/{project_id}/books/{book_id}", tags=["density"])


async def _story_density_enabled(db: AsyncSession) -> bool:
    """Check if Story Density Engine is enabled (config + DB override)."""
    settings = get_settings()
    enabled = getattr(settings, "feature_story_density", True)
    result = await db.execute(select(Setting).where(Setting.key == "feature.story_density"))
    row = result.scalar_one_or_none()
    if row and isinstance(row.value, dict) and "enabled" in row.value:
        enabled = bool(row.value["enabled"])
    return enabled


@router.post("/density/scan", response_model=DensityScanResponse)
async def create_density_scan(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: DensityScanCreate | None = None,
):
    """Run a density scan on the book."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    body = body or DensityScanCreate()
    try:
        scan = await run_density_scan(
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


@router.get("/density/scans", response_model=list[DensityScanResponse])
async def list_density_scans(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = Query(10, ge=1, le=50),
):
    """List density scans for the book."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(DensityScan)
        .where(DensityScan.book_id == book_id)
        .order_by(DensityScan.started_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/density/issues", response_model=list[DensityIssueResponse])
async def list_density_issues(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    severity: str | None = Query(None, description="Filter by severity"),
    category: str | None = Query(None, description="Filter by category"),
    action_category: str | None = Query(None, description="Filter by action category"),
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    chapter_id: uuid.UUID | None = Query(None, description="Filter by chapter"),
    scan_id: uuid.UUID | None = Query(None, description="Filter by scan"),
    limit: int = Query(100, ge=1, le=500),
):
    """List density issues for the book with optional filters."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    q = select(DensityIssue).where(DensityIssue.book_id == book_id)
    if severity:
        q = q.where(DensityIssue.severity == severity)
    if category:
        q = q.where(DensityIssue.category == category)
    if action_category:
        q = q.where(DensityIssue.action_category == action_category)
    if status_filter:
        q = q.where(DensityIssue.status == status_filter)
    if chapter_id:
        q = q.where(DensityIssue.chapter_id == chapter_id)
    if scan_id:
        q = q.where(DensityIssue.scan_id == scan_id)
    q = q.order_by(DensityIssue.created_at.desc()).limit(limit)
    result = await db.execute(q)
    return list(result.scalars().all())


@router.get("/density/health", response_model=DensityHealthSummary)
async def get_density_health(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get manuscript density health summary for dashboard."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)

    issues_q = select(DensityIssue).where(DensityIssue.book_id == book_id)
    result = await db.execute(issues_q)
    issues = list(result.scalars().all())

    last_scan = await db.execute(
        select(DensityScan)
        .where(DensityScan.book_id == book_id, DensityScan.status == "completed")
        .order_by(DensityScan.completed_at.desc().nullslast())
        .limit(1)
    )
    last = last_scan.scalar_one_or_none()

    by_severity: dict[str, int] = {}
    by_category: dict[str, int] = {}
    by_action: dict[str, int] = {}
    open_count = 0
    for i in issues:
        by_severity[i.severity] = by_severity.get(i.severity, 0) + 1
        by_category[i.category] = by_category.get(i.category, 0) + 1
        by_action[i.action_category] = by_action.get(i.action_category, 0) + 1
        if i.status == "open":
            open_count += 1

    return DensityHealthSummary(
        total_issues=len(issues),
        by_severity=by_severity,
        by_category=by_category,
        by_action=by_action,
        open_count=open_count,
        manuscript_density_score=last.manuscript_density_score if last else None,
        last_scan_at=last.completed_at if last else None,
        last_scan_issue_count=last.issue_count if last else None,
    )


@router.get("/density/issues/{issue_id}", response_model=DensityIssueResponse)
async def get_density_issue(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get a single density issue by ID."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(DensityIssue).where(
            DensityIssue.id == issue_id,
            DensityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")
    return issue


@router.patch("/density/issues/{issue_id}", response_model=DensityIssueResponse)
async def update_density_issue(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    body: DensityIssueUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update density issue status (resolve, ignore, mark intentional)."""
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(DensityIssue).where(
            DensityIssue.id == issue_id,
            DensityIssue.book_id == book_id,
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


@router.get("/density/issues/{issue_id}/guidance", response_model=DensityFixGuidance)
async def get_density_issue_guidance(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get guided trim/compress/strengthen suggestions for a density issue."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(DensityIssue).where(
            DensityIssue.id == issue_id,
            DensityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    issue_dict = {
        "issue_type": issue.issue_type,
        "category": issue.category,
        "action_category": issue.action_category,
        "chapter_id": str(issue.chapter_id) if issue.chapter_id else None,
        "related_chapter_ids": issue.related_chapter_ids or [],
        "fix_suggestions": issue.fix_suggestions or [],
    }
    context = {}
    last_scan = await db.execute(
        select(DensityScan)
        .where(DensityScan.id == issue.scan_id)
        .limit(1)
    )
    scan = last_scan.scalar_one_or_none()
    if scan and scan.density_map_snapshot:
        context = {
            **scan.density_map_snapshot,
            "project_type": scan.density_map_snapshot.get("project_type", "fiction"),
            "guidance_mode": scan.density_map_snapshot.get("guidance_mode", "flexible"),
        }
    guidance = get_density_fix_guidance(issue.issue_type, issue_dict, context)
    return DensityFixGuidance(**guidance)


@router.get("/density/analysis")
async def get_density_analysis(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get scene purpose, chapter drag, and repetition analysis from latest scan."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)

    last_scan = await db.execute(
        select(DensityScan)
        .where(DensityScan.book_id == book_id, DensityScan.status == "completed")
        .order_by(DensityScan.completed_at.desc().nullslast())
        .limit(1)
    )
    scan = last_scan.scalar_one_or_none()
    if not scan or not scan.density_map_snapshot:
        return {
            "scan_id": None,
            "last_scan_at": None,
            "scene_purpose_analysis": None,
            "chapter_drag_analysis": None,
            "repetition_analysis": None,
        }

    dm = scan.density_map_snapshot
    return {
        "scan_id": str(scan.id),
        "last_scan_at": scan.completed_at.isoformat() if scan.completed_at else None,
        "scene_purpose_analysis": dm.get("scene_purpose_analysis"),
        "chapter_drag_analysis": dm.get("chapter_drag_analysis"),
        "repetition_analysis": dm.get("repetition_analysis"),
    }


@router.get("/density/chapters/{chapter_id}/summary")
async def get_chapter_density_summary(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    chapter_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get 'what this chapter is doing', 'where dragging', 'repetitive parts' for a chapter."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)

    last_scan = await db.execute(
        select(DensityScan)
        .where(DensityScan.book_id == book_id, DensityScan.status == "completed")
        .order_by(DensityScan.completed_at.desc().nullslast())
        .limit(1)
    )
    scan = last_scan.scalar_one_or_none()
    if not scan or not scan.density_map_snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No density scan found. Run a scan first.")

    dm = scan.density_map_snapshot
    ch_id_str = str(chapter_id)

    what_doing = None
    where_dragging = None
    repetitive_parts = None

    purpose = dm.get("scene_purpose_analysis") or {}
    chapter_purposes = purpose.get("chapter_purposes", [])
    for cp in chapter_purposes:
        if cp.get("chapter_id") == ch_id_str:
            jobs = cp.get("primary_jobs", [])
            what_doing = "Primarily: " + ", ".join(jobs) if jobs else "Unclear purpose"
            break

    drag = dm.get("chapter_drag_analysis") or {}
    chapter_scores = drag.get("chapter_drag_scores", [])
    for cs in chapter_scores:
        if cs.get("chapter_id") == ch_id_str:
            if cs.get("is_dragging"):
                where_dragging = {
                    "is_dragging": True,
                    "drag_score": cs.get("drag_score"),
                    "suggestion": "Consider trimming or tightening this chapter.",
                }
            else:
                where_dragging = {"is_dragging": False}
            break

    rep = dm.get("repetition_analysis") or {}
    chapter_heat = rep.get("chapter_repetition_heat", [])
    for ch in chapter_heat:
        if ch.get("chapter_id") == ch_id_str:
            heat = ch.get("repetition_heat", 0)
            level = ch.get("heat_level", "low")
            repetitive_parts = {
                "repetition_heat": heat,
                "heat_level": level,
                "in_chapter_repetition": ch.get("in_chapter_repetition"),
                "cross_chapter_overlap": ch.get("cross_chapter_overlap"),
            }
            break

    return {
        "chapter_id": ch_id_str,
        "what_this_chapter_is_doing": what_doing,
        "where_this_chapter_is_dragging": where_dragging,
        "which_parts_feel_repetitive": repetitive_parts,
    }


class CreateRevisionTaskBody(BaseModel):
    """Create revision task from density recommendation."""

    revision_pass_id: uuid.UUID | None = Field(None, description="Existing pass; if None, creates a custom pass")
    title: str | None = Field(None, description="Override task title; if None, uses recommendation")


@router.get("/density/issues/{issue_id}/decision")
async def get_density_issue_decision(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get trim-vs-strengthen decision for a density issue."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(DensityIssue).where(
            DensityIssue.id == issue_id,
            DensityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    scan_result = await db.execute(select(DensityScan).where(DensityScan.id == issue.scan_id).limit(1))
    scan = scan_result.scalar_one_or_none()
    context = {}
    if scan and scan.density_map_snapshot:
        context = {
            **scan.density_map_snapshot,
            "project_type": scan.density_map_snapshot.get("project_type", "fiction"),
            "guidance_mode": scan.density_map_snapshot.get("guidance_mode", "flexible"),
        }

    issue_dict = {
        "issue_type": issue.issue_type,
        "category": issue.category,
        "action_category": issue.action_category,
        "chapter_id": str(issue.chapter_id) if issue.chapter_id else None,
        "related_chapter_ids": issue.related_chapter_ids or [],
    }
    decision = decide_action(issue_dict, context)
    return decision


@router.get("/density/issues/{issue_id}/alternatives")
async def get_density_issue_alternatives(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Compare alternative repair paths for a density issue."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    result = await db.execute(
        select(DensityIssue).where(
            DensityIssue.id == issue_id,
            DensityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    scan_result = await db.execute(select(DensityScan).where(DensityScan.id == issue.scan_id).limit(1))
    scan = scan_result.scalar_one_or_none()
    context = {}
    if scan and scan.density_map_snapshot:
        context = {
            **scan.density_map_snapshot,
            "project_type": scan.density_map_snapshot.get("project_type", "fiction"),
            "guidance_mode": scan.density_map_snapshot.get("guidance_mode", "flexible"),
        }

    issue_dict = {
        "issue_type": issue.issue_type,
        "category": issue.category,
        "action_category": issue.action_category,
        "chapter_id": str(issue.chapter_id) if issue.chapter_id else None,
        "related_chapter_ids": issue.related_chapter_ids or [],
    }
    alts = get_alternatives_comparison(issue_dict, context)
    return {"alternatives": alts}


@router.post("/density/issues/{issue_id}/create-revision-task")
async def create_revision_task_from_density(
    project_id: uuid.UUID,
    book_id: uuid.UUID,
    issue_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: CreateRevisionTaskBody | None = None,
):
    """Create a revision task (checklist item) from a density recommendation."""
    if not await _story_density_enabled(db):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story Density Engine is disabled")
    await get_book_with_access_or_404(db, book_id, project_id, current_user.id)
    body = body or CreateRevisionTaskBody()

    result = await db.execute(
        select(DensityIssue).where(
            DensityIssue.id == issue_id,
            DensityIssue.book_id == book_id,
        )
    )
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found")

    scan_result = await db.execute(select(DensityScan).where(DensityScan.id == issue.scan_id).limit(1))
    scan = scan_result.scalar_one_or_none()
    context = {}
    if scan and scan.density_map_snapshot:
        context = {
            **scan.density_map_snapshot,
            "project_type": scan.density_map_snapshot.get("project_type", "fiction"),
            "guidance_mode": scan.density_map_snapshot.get("guidance_mode", "flexible"),
        }

    issue_dict = {
        "issue_type": issue.issue_type,
        "category": issue.category,
        "action_category": issue.action_category,
        "chapter_id": str(issue.chapter_id) if issue.chapter_id else None,
        "related_chapter_ids": issue.related_chapter_ids or [],
    }
    decision = decide_action(issue_dict, context)
    task_title = body.title or decision.get("revision_task_suggestion") or f"Review: {issue.title}"

    if body.revision_pass_id:
        pass_result = await db.execute(
            select(RevisionPass).where(
                RevisionPass.id == body.revision_pass_id,
                RevisionPass.project_id == project_id,
            )
        )
        rev_pass = pass_result.scalar_one_or_none()
        if not rev_pass:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Revision pass not found")
    else:
        from authora.models import Book

        sort_result = await db.execute(
            select(RevisionPass).where(RevisionPass.project_id == project_id).order_by(RevisionPass.sort_order.desc())
        )
        max_order = 0
        for r in sort_result.scalars().all():
            max_order = max(max_order, r.sort_order or 0)
        rev_pass = RevisionPass(
            project_id=project_id,
            book_id=book_id,
            pass_type="custom",
            name="Density cleanup",
            sort_order=max_order + 1,
        )
        db.add(rev_pass)
        await db.flush()

    checklist_result = await db.execute(
        select(RevisionChecklistItem)
        .where(RevisionChecklistItem.revision_pass_id == rev_pass.id)
        .order_by(RevisionChecklistItem.sort_order.desc())
    )
    max_sort = 0
    for c in checklist_result.scalars().all():
        max_sort = max(max_sort, c.sort_order or 0)

    item = RevisionChecklistItem(
        revision_pass_id=rev_pass.id,
        title=task_title[:500],
        sort_order=max_sort + 1,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {
        "id": str(item.id),
        "revision_pass_id": str(rev_pass.id),
        "title": item.title,
        "sort_order": item.sort_order,
    }
