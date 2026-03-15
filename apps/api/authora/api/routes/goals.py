"""Goals API routes."""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import Goal

router = APIRouter(prefix="/goals", tags=["goals"])


class GoalCreate(BaseModel):
    target_words: int
    deadline: str | None = None
    book_id: uuid.UUID | None = None


class GoalResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    book_id: uuid.UUID | None
    target_words: int
    deadline: datetime | None
    completed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List user's goals."""
    result = await db.execute(
        select(Goal).where(Goal.user_id == current_user.id).order_by(Goal.created_at.desc())
    )
    goals = result.scalars().all()
    return [GoalResponse.model_validate(g) for g in goals]


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(
    data: GoalCreate,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create goal."""
    from datetime import datetime, timezone

    deadline = None
    if data.deadline:
        try:
            deadline = datetime.fromisoformat(data.deadline.replace("Z", "+00:00"))
        except ValueError:
            pass

    goal = Goal(
        user_id=current_user.id,
        target_words=data.target_words,
        deadline=deadline,
        book_id=data.book_id,
    )
    db.add(goal)
    await db.flush()
    await db.refresh(goal)
    return GoalResponse.model_validate(goal)
