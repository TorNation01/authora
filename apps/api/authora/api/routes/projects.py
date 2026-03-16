"""Projects API routes."""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.api.resolvers import get_project_or_404
from authora.core.audit import AuditLogger
from authora.database import get_db
from authora.models import Project
from authora.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    status_filter: str | None = Query(None, alias="status", description="active | archived | all"),
    q: str | None = Query(None, description="Search by project name"),
    sort: str = Query("updated_at", description="updated_at | name | created_at | last_accessed_at"),
):
    """List user's projects with optional filters and search."""
    base = select(Project).where(Project.user_id == current_user.id)

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

    result = await db.execute(base)
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/recent", response_model=ProjectResponse | None)
async def get_recent_project(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get most recently accessed project for continue-recent."""
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id, Project.deleted_at.is_(None))
        .order_by(Project.last_accessed_at.desc().nullslast(), Project.updated_at.desc())
        .limit(1)
    )
    p = result.scalar_one_or_none()
    return ProjectResponse.model_validate(p) if p else None


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
    project = Project(user_id=current_user.id, name=data.name)
    db.add(project)
    await db.flush()
    audit = AuditLogger(db)
    await audit.log("create", "project", str(project.id), current_user.id, {"name": data.name})
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get project by ID. Updates last_accessed_at."""
    project = await get_project_or_404(db, project_id, current_user.id)
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
