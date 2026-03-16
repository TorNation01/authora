"""Goals API routes."""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import Goal
from authora.services.goal_service import create_goal as create_goal_svc

router = APIRouter(prefix="/goals", tags=["goals"])


class GoalCreate(BaseModel):
    target_words: int | None = None
    target_type: str | None = None
    target_value: int | None = None
    deadline: str | None = None
    book_id: uuid.UUID | None = None
    project_id: uuid.UUID | None = None
    preset: str | None = None  # gentle | balanced | aggressive
    extra_data: dict | None = None


class GoalUpdate(BaseModel):
    target_words: int | None = None
    target_value: int | None = None
    deadline: str | None = None
    is_paused: bool | None = None
    low_energy_mode: bool | None = None


class GoalResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    book_id: uuid.UUID | None
    project_id: uuid.UUID | None
    target_words: int
    target_type: str | None
    target_value: int | None
    deadline: datetime | None
    completed_at: datetime | None
    is_paused: bool
    low_energy_mode: bool
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
    project_id: uuid.UUID | None = None,
    book_id: uuid.UUID | None = None,
    active_only: bool = False,
):
    """List user's goals."""
    q = select(Goal).where(Goal.user_id == current_user.id)
    if project_id:
        q = q.where((Goal.project_id == project_id) | (Goal.project_id.is_(None)))
    if book_id:
        q = q.where((Goal.book_id == book_id) | (Goal.book_id.is_(None)))
    if active_only:
        q = q.where(Goal.completed_at.is_(None), Goal.is_paused == False)
    q = q.order_by(Goal.created_at.desc())
    result = await db.execute(q)
    goals = result.scalars().all()
    return [GoalResponse.model_validate(g) for g in goals]


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create goal. Use preset (gentle/balanced/aggressive) or explicit target_type/target_value."""
    deadline = None
    if data.deadline:
        try:
            deadline = datetime.fromisoformat(data.deadline.replace("Z", "+00:00"))
        except ValueError:
            pass

    goal = await create_goal_svc(
        db,
        current_user.id,
        target_type=data.target_type,
        target_value=data.target_value,
        target_words=data.target_words or 0,
        deadline=deadline,
        book_id=data.book_id,
        project_id=data.project_id,
        preset=data.preset,
        extra_data=data.extra_data,
    )
    return GoalResponse.model_validate(goal)


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: uuid.UUID,
    data: GoalUpdate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update a goal."""
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    if data.target_words is not None:
        goal.target_words = data.target_words
    if data.target_value is not None:
        goal.target_value = data.target_value
    if data.deadline is not None:
        try:
            goal.deadline = datetime.fromisoformat(data.deadline.replace("Z", "+00:00"))
        except ValueError:
            pass
    if data.is_paused is not None:
        goal.is_paused = data.is_paused
    if data.low_energy_mode is not None:
        goal.low_energy_mode = data.low_energy_mode
    await db.flush()
    await db.refresh(goal)
    return GoalResponse.model_validate(goal)


@router.post("/{goal_id}/pause")
async def pause_goal(
    goal_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Pause a goal."""
    from authora.services.goal_service import pause_goal as pause_goal_svc

    goal = await pause_goal_svc(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"ok": True, "is_paused": True}


@router.post("/{goal_id}/resume")
async def resume_goal(
    goal_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Resume a paused goal."""
    from authora.services.goal_service import resume_goal as resume_goal_svc

    goal = await resume_goal_svc(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"ok": True, "is_paused": False}


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a goal."""
    result = await db.execute(select(Goal).where(Goal.id == goal_id, Goal.user_id == current_user.id))
    goal = result.scalar_one_or_none()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    await db.delete(goal)
    await db.flush()
