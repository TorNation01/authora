"""Projects API routes."""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_project_or_404, get_project_with_access_or_404
from authora.core.audit import AuditLogger
from authora.database import get_db
from authora.models import Book, Chapter, Project, ProjectMember
from authora.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectWizardRequest

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str | None = Query(None, alias="status", description="active | archived | all"),
    q: str | None = Query(None, description="Search by project name"),
    sort: str = Query("updated_at", description="updated_at | name | created_at | last_accessed_at"),
    limit: int = Query(50, ge=1, le=200, description="Max projects to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
):
    """List user's projects (owned or shared) with optional filters, search, and pagination."""
    # Include owned projects and projects where user is a member
    member_project_ids = select(ProjectMember.project_id).where(
        ProjectMember.user_id == current_user.id
    )
    base = select(Project).where(
        or_(Project.user_id == current_user.id, Project.id.in_(member_project_ids))
    )

    if status_filter == "archived":
        base = base.where(Project.deleted_at.isnot(None))
    elif status_filter != "all":
        base = base.where(Project.deleted_at.is_(None))

    if q and q.strip():
        base = base.where(or_(Project.name.ilike(f"%{q.strip()}%")))

    if sort == "name":
        base = base.order_by(Project.name.asc())
    elif sort == "created_at":
        base = base.order_by(Project.created_at.desc())
    elif sort == "last_accessed_at":
        base = base.order_by(
            Project.last_accessed_at.desc().nullslast(),
            Project.updated_at.desc(),
        )
    else:
        base = base.order_by(Project.updated_at.desc())

    base = base.offset(offset).limit(limit)
    result = await db.execute(base)
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/recent", response_model=ProjectResponse | None)
async def get_recent_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get most recently accessed project for continue-recent."""
    member_project_ids = select(ProjectMember.project_id).where(
        ProjectMember.user_id == current_user.id
    )
    result = await db.execute(
        select(Project)
        .where(
            or_(Project.user_id == current_user.id, Project.id.in_(member_project_ids)),
            Project.deleted_at.is_(None),
        )
        .order_by(Project.last_accessed_at.desc().nullslast(), Project.updated_at.desc())
        .limit(1)
    )
    p = result.scalar_one_or_none()
    return ProjectResponse.model_validate(p) if p else None


class ProjectWizardResponse(BaseModel):
    """Response from project wizard."""

    project: ProjectResponse
    book_id: uuid.UUID
    book_title: str

    model_config = {"from_attributes": True}


@router.post("/from-wizard", response_model=ProjectWizardResponse, status_code=status.HTTP_201_CREATED)
async def create_project_from_wizard(
    data: ProjectWizardRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create project and book from template via guided wizard."""
    from authora.models import ProjectTemplate
    from authora.services.onboarding_analytics import (
        record_first_project_created,
        record_project_wizard_completed,
    )
    from authora.services.project_wizard import create_project_from_wizard

    try:
        project, book = await create_project_from_wizard(
            db,
            current_user.id,
            template_id=data.template_id,
            project_name=data.project_name,
            book_title=data.book_title,
            book_type=data.book_type,
            genre=data.genre,
            core_idea=data.core_idea,
            wizard_answers=data.wizard_answers,
            structure_framework=data.structure_framework,
            framework_id=data.framework_id,
            target_words=data.target_words,
            target_date=data.target_date,
            guidance_mode=data.guidance_mode,
            knowledge_mode=getattr(data, "knowledge_mode", None),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    audit = AuditLogger(db)
    await audit.log(
        "create",
        "project",
        str(project.id),
        current_user.id,
        {"name": project.name, "from_wizard": True, "template_id": str(data.template_id) if data.template_id else None},
    )
    template_slug = None
    if project.template_id:
        tpl = await db.get(ProjectTemplate, project.template_id)
        template_slug = tpl.slug if tpl else None
    await record_project_wizard_completed(
        db,
        current_user.id,
        template_id=project.template_id,
        template_slug=template_slug,
        guidance_mode=data.guidance_mode or project.guidance_mode,
    )
    await record_first_project_created(
        db, current_user.id, project.id, template_slug=template_slug, from_wizard=True
    )
    await db.commit()
    await db.refresh(project)
    await db.refresh(book)
    return ProjectWizardResponse(
        project=ProjectResponse.model_validate(project),
        book_id=book.id,
        book_title=book.title,
    )


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create project."""
    from authora.services.billing_service import check_project_limit

    allowed, current, limit = await check_project_limit(db, current_user.id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Project limit reached ({current}/{limit}). Upgrade to Premium for more.",
        )
    project = Project(
        user_id=current_user.id,
        name=data.name,
        guidance_mode=getattr(data, "guidance_mode", "guided") or "guided",
        knowledge_mode=getattr(data, "knowledge_mode", "fiction") or "fiction",
        knowledge_modules=getattr(data, "knowledge_modules", None),
    )
    db.add(project)
    await db.flush()
    # Add owner as project member for collaboration consistency
    owner_member = ProjectMember(
        user_id=current_user.id,
        project_id=project.id,
        role="owner",
        invited_by=None,
    )
    db.add(owner_member)
    await db.flush()
    audit = AuditLogger(db)
    await audit.log("create", "project", str(project.id), current_user.id, {"name": data.name})
    from authora.services.onboarding_analytics import record_first_project_created

    await record_first_project_created(db, current_user.id, project.id, from_wizard=False)
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}/progress")
async def get_project_progress(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get project progress: total words, chapters, per-book stats."""
    await get_project_with_access_or_404(db, project_id, current_user.id)
    result = await db.execute(
        select(Book).where(Book.project_id == project_id).order_by(Book.updated_at.desc())
    )
    books = result.scalars().all()
    book_stats = []
    total_words = 0
    total_chapters = 0
    chapters_done = 0
    for b in books:
        ch_result = await db.execute(
            select(Chapter).where(Chapter.book_id == b.id).order_by(Chapter.sort_order)
        )
        chapters = ch_result.scalars().all()
        words = sum(c.word_count for c in chapters)
        done = sum(1 for c in chapters if getattr(c, "section_status", None) == "done")
        total_words += words
        total_chapters += len(chapters)
        chapters_done += done
        book_stats.append({
            "id": str(b.id),
            "title": b.title,
            "word_count": words,
            "chapter_count": len(chapters),
            "chapters_done": done,
        })
    progress_pct = (chapters_done / total_chapters * 100) if total_chapters else 0
    return {
        "total_words": total_words,
        "total_chapters": total_chapters,
        "chapters_done": chapters_done,
        "progress_pct": round(progress_pct, 1),
        "books": book_stats,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get project by ID. Updates last_accessed_at. Accessible to owner and members."""
    project, _ = await get_project_with_access_or_404(db, project_id, current_user.id)
    project.last_accessed_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update project."""
    project = await get_project_or_404(db, project_id, current_user.id)
    if data.name is not None:
        project.name = data.name
    if data.guidance_mode is not None:
        if data.guidance_mode not in ("guided", "flexible", "freeform"):
            raise HTTPException(status_code=400, detail="Invalid guidance_mode")
        project.guidance_mode = data.guidance_mode
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Archive project (soft delete)."""
    project = await get_project_or_404(db, project_id, current_user.id)
    project.deleted_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}/restore", response_model=ProjectResponse)
async def restore_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Restore archived project."""
    project = await get_project_or_404(db, project_id, current_user.id)
    project.deleted_at = None
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


class DuplicateProjectRequest(BaseModel):
    """Duplicate project request."""

    name: str | None = Field(None, description="Name for the copy")


@router.post("/{project_id}/duplicate", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    body: DuplicateProjectRequest | None = Body(None),
):
    """Duplicate project with books, chapters, notes, and workspace data."""
    from authora.services.billing_service import check_project_limit
    from authora.services.project_duplication import duplicate_project as do_duplicate

    allowed, current, limit = await check_project_limit(db, current_user.id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Project limit reached ({current}/{limit}). Upgrade to Premium for more.",
        )

    new_name = body.name if body and body.name else None
    project = await do_duplicate(db, project_id, current_user.id, new_name)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await db.commit()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    confirm: bool = Query(False, description="Must be true to permanently delete"),
):
    """Delete project permanently. Requires confirm=true."""
    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deletion requires confirm=true query parameter",
        )
    project = await get_project_or_404(db, project_id, current_user.id)
    await db.delete(project)
