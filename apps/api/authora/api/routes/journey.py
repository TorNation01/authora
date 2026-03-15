"""Journey and onboarding API routes."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import JourneyTask, UserJourney
from authora.services.journey_engine import (
    complete_task,
    get_next_step,
    get_or_create_journey,
    get_recovery_nudge,
)

router = APIRouter(prefix="/journey", tags=["journey"])


class OnboardingRequest(BaseModel):
    book_type: str  # fiction | nonfiction
    writing_mode: str  # solo | cowrite | ghostwriter
    writing_goals: str | None = None
    target_timeline: str | None = None
    writing_schedule: str | None = None
    accountability_style: str | None = None
    ai_comfort_level: str | None = None
    genre_topic: str | None = None


class CompleteTaskRequest(BaseModel):
    task_id: str


@router.post("/onboarding")
async def submit_onboarding(
    data: OnboardingRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Submit onboarding answers and create personalized journey."""
    journey = await get_or_create_journey(db, str(current_user.id), data.model_dump())
    return {
        "journey_id": str(journey.id),
        "current_phase": journey.current_phase,
        "roadmap": journey.roadmap,
        "message": "Your personalized writing journey is ready.",
    }


@router.get("")
async def get_journey(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get user's journey and current state."""
    result = await db.execute(select(UserJourney).where(UserJourney.user_id == current_user.id))
    journey = result.scalar_one_or_none()
    if not journey:
        return {"has_journey": False, "message": "Complete onboarding to create your journey."}

    nudge = await get_recovery_nudge(journey)
    next_step = await get_next_step(db, journey)

    # Fetch current phase tasks for checklist
    tasks_result = await db.execute(
        select(JourneyTask)
        .where(JourneyTask.journey_id == journey.id, JourneyTask.phase == journey.current_phase)
        .order_by(JourneyTask.sort_order)
    )
    tasks = tasks_result.scalars().all()

    return {
        "has_journey": True,
        "journey": {
            "id": str(journey.id),
            "book_type": journey.book_type,
            "writing_mode": journey.writing_mode,
            "current_phase": journey.current_phase,
            "roadmap": journey.roadmap,
            "last_active_at": journey.last_active_at.isoformat() if journey.last_active_at else None,
            "completed_at": journey.completed_at.isoformat() if journey.completed_at else None,
        },
        "tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "task_type": t.task_type,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in tasks
        ],
        "nudge": nudge,
        "next_step": next_step,
    }


@router.get("/next-step")
async def get_next_step_endpoint(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get the next recommended task."""
    result = await db.execute(select(UserJourney).where(UserJourney.user_id == current_user.id))
    journey = result.scalar_one_or_none()
    if not journey:
        raise HTTPException(status_code=404, detail="No journey. Complete onboarding first.")

    return await get_next_step(db, journey)


@router.post("/tasks/complete")
async def complete_task_endpoint(
    data: CompleteTaskRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Mark a task as complete."""
    task = await complete_task(db, data.task_id, str(current_user.id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"completed": True, "task_id": str(task.id)}


@router.get("/recover")
async def get_recovery(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get recovery nudge and next step for returning users."""
    result = await db.execute(select(UserJourney).where(UserJourney.user_id == current_user.id))
    journey = result.scalar_one_or_none()
    if not journey:
        return {"has_journey": False, "nudge": {"type": "welcome", "message": "Complete onboarding to start your journey."}}

    nudge = await get_recovery_nudge(journey)
    next_step = await get_next_step(db, journey)
    return {"nudge": nudge, "next_step": next_step}
