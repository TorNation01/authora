"""Gamification API routes."""

import uuid
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import CurrentUser
from authora.database import get_db
from authora.models import Achievement, FocusSession, UserJourney, UserStats
from authora.services.gamification import get_or_create_user_stats, get_user_achievements
from authora.services.gamification_engine import get_milestone_progress, get_next_milestone

router = APIRouter(prefix="/gamification", tags=["gamification"])


class UserStatsResponse(BaseModel):
    total_words: int
    current_streak: int
    longest_streak: int
    xp: int
    level: int
    best_daily_words: int = 0
    best_weekly_words: int = 0
    next_milestone: int | None = None
    milestone_progress: tuple[int, int] | None = None

    class Config:
        from_attributes = True


class AchievementResponse(BaseModel):
    id: str
    type: str
    badge_id: str | None
    earned_at: str

    class Config:
        from_attributes = True


class QuestResponse(BaseModel):
    id: str
    title: str
    target_value: int
    current_value: int
    xp_reward: int
    completed_at: str | None


class JourneyPhaseProgress(BaseModel):
    phase: str
    label: str
    completed: bool
    current: bool
    progress: float


class JourneyMapResponse(BaseModel):
    phases: list[JourneyPhaseProgress]
    current_phase_index: int
    overall_progress: float


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


PHASE_LABELS = {
    "idea": "Idea",
    "concept": "Concept",
    "outline": "Outline",
    "chapter_planning": "Chapter planning",
    "drafting": "Drafting",
    "revision": "Revision",
    "polish": "Polish",
    "export_prep": "Export",
}


@router.get("/stats", response_model=UserStatsResponse)
async def get_stats(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get user gamification stats."""
    stats = await get_or_create_user_stats(db, current_user.id)
    next_m = get_next_milestone(stats.total_words)
    prog = get_milestone_progress(stats.total_words)
    return UserStatsResponse(
        total_words=stats.total_words,
        current_streak=stats.current_streak,
        longest_streak=stats.longest_streak,
        xp=stats.xp,
        level=stats.level,
        best_daily_words=getattr(stats, "best_daily_words", 0),
        best_weekly_words=getattr(stats, "best_weekly_words", 0),
        next_milestone=next_m,
        milestone_progress=prog,
    )


@router.get("/achievements", response_model=list[AchievementResponse])
async def get_achievements(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get user achievements/badges."""
    achievements = await get_user_achievements(db, current_user.id)
    return [
        AchievementResponse(
            id=str(a.id),
            type=a.type,
            badge_id=a.badge_id,
            earned_at=a.earned_at.isoformat(),
        )
        for a in achievements
    ]


@router.get("/quests/daily", response_model=list[QuestResponse])
async def get_daily_quests(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get today's daily quests."""
    from authora.services.gamification_service import get_or_create_daily_quests
    quests = await get_or_create_daily_quests(db, current_user.id)
    return [
        QuestResponse(
            id=str(q.id),
            title=q.title,
            target_value=q.target_value,
            current_value=q.current_value,
            xp_reward=q.xp_reward,
            completed_at=q.completed_at.isoformat() if q.completed_at else None,
        )
        for q in quests
    ]


@router.get("/quests/weekly", response_model=list[QuestResponse])
async def get_weekly_missions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get this week's missions."""
    from authora.services.gamification_service import get_or_create_weekly_missions
    missions = await get_or_create_weekly_missions(db, current_user.id)
    return [
        QuestResponse(
            id=str(m.id),
            title=m.title,
            target_value=m.target_value,
            current_value=m.current_value,
            xp_reward=m.xp_reward,
            completed_at=m.completed_at.isoformat() if m.completed_at else None,
        )
        for m in missions
    ]


class FocusSessionCreate(BaseModel):
    target_minutes: int
    book_id: str | None = None


class FocusSessionComplete(BaseModel):
    actual_minutes: int
    words_written: int


@router.post("/focus/start")
async def start_focus_session(
    data: FocusSessionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Start a focus session."""
    session = FocusSession(
        user_id=current_user.id,
        book_id=uuid.UUID(data.book_id) if data.book_id else None,
        target_minutes=data.target_minutes,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return {"id": str(session.id), "started_at": session.started_at.isoformat() if session.started_at else None}


@router.post("/focus/{session_id}/complete")
async def complete_focus_session_endpoint(
    session_id: uuid.UUID,
    data: FocusSessionComplete,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Complete a focus session and award XP."""
    from authora.services.gamification import complete_focus_session
    result = await complete_focus_session(
        db, current_user.id, session_id,
        data.actual_minutes, data.words_written,
    )
    return {"events": result.get("events", []), "stats": result.get("stats")}


@router.get("/journey-map", response_model=JourneyMapResponse)
async def get_journey_map(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Get book journey map with phase progress."""
    r = await db.execute(
        select(UserJourney).where(UserJourney.user_id == current_user.id)
    )
    journey = r.scalar_one_or_none()
    phases_order = [
        "idea", "concept", "outline", "chapter_planning",
        "drafting", "revision", "polish", "export_prep",
    ]
    if not journey:
        return JourneyMapResponse(
            phases=[
                JourneyPhaseProgress(
                    phase=p,
                    label=PHASE_LABELS.get(p, p),
                    completed=False,
                    current=(i == 0),
                    progress=0.0,
                )
                for i, p in enumerate(phases_order)
            ],
            current_phase_index=0,
            overall_progress=0.0,
        )
    current_idx = phases_order.index(journey.current_phase) if journey.current_phase in phases_order else 0
    phases = []
    for i, p in enumerate(phases_order):
        completed = i < current_idx
        current = i == current_idx
        progress = 1.0 if completed else (0.5 if current else 0.0)
        phases.append(
            JourneyPhaseProgress(
                phase=p,
                label=PHASE_LABELS.get(p, p),
                completed=completed,
                current=current,
                progress=progress,
            )
        )
    overall = (current_idx + 0.5) / len(phases_order) if phases_order else 0.0
    return JourneyMapResponse(
        phases=phases,
        current_phase_index=current_idx,
        overall_progress=overall,
    )
