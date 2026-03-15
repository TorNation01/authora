"""Journey engine - roadmap generation, next-step, phase progression."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import UserJourney, JourneyTask

PHASES = [
    ("idea", "Idea", "Capture your core idea and inspiration"),
    ("concept", "Concept shaping", "Refine the concept and direction"),
    ("outline", "Outline", "Create a high-level structure"),
    ("chapter_planning", "Chapter planning", "Plan each chapter or section"),
    ("drafting", "Drafting", "Write your first draft"),
    ("revision", "Revision", "Revise and restructure"),
    ("polish", "Polish", "Edit and refine the prose"),
    ("export_prep", "Export & publish prep", "Prepare for export and publishing"),
]

PHASE_TASKS: dict[str, list[dict[str, Any]]] = {
    "idea": [
        {"title": "Write your core idea in one sentence", "task_type": "checklist"},
        {"title": "Note what inspired this idea", "task_type": "checklist"},
        {"title": "Identify your target reader", "task_type": "checklist"},
    ],
    "concept": [
        {"title": "Expand your idea into a paragraph", "task_type": "checklist"},
        {"title": "Define the central conflict or thesis", "task_type": "checklist"},
        {"title": "Sketch the beginning, middle, and end", "task_type": "checklist"},
    ],
    "outline": [
        {"title": "Create a high-level outline (3-7 sections)", "task_type": "checklist"},
        {"title": "Add key plot points or arguments per section", "task_type": "checklist"},
        {"title": "Review and adjust the flow", "task_type": "checklist"},
    ],
    "chapter_planning": [
        {"title": "Break outline into chapters", "task_type": "checklist"},
        {"title": "Add one-sentence summary per chapter", "task_type": "checklist"},
        {"title": "Create your first chapter", "task_type": "action"},
    ],
    "drafting": [
        {"title": "Write chapter by chapter", "task_type": "milestone"},
        {"title": "Aim for progress, not perfection", "task_type": "checklist"},
        {"title": "Complete your first draft", "task_type": "milestone"},
    ],
    "revision": [
        {"title": "Read through the full draft", "task_type": "checklist"},
        {"title": "Identify structural changes needed", "task_type": "checklist"},
        {"title": "Revise and restructure", "task_type": "milestone"},
    ],
    "polish": [
        {"title": "Line edit for clarity and flow", "task_type": "checklist"},
        {"title": "Fix grammar and consistency", "task_type": "checklist"},
        {"title": "Final read-through", "task_type": "checklist"},
    ],
    "export_prep": [
        {"title": "Choose export format (DOCX, PDF, EPUB)", "task_type": "checklist"},
        {"title": "Add title page and metadata", "task_type": "checklist"},
        {"title": "Export your book", "task_type": "action"},
    ],
}


def generate_roadmap(book_type: str, writing_mode: str, genre_topic: str | None) -> dict[str, Any]:
    """Generate personalized roadmap from onboarding answers."""
    phases_data = []
    for phase_id, phase_name, phase_desc in PHASES:
        tasks = PHASE_TASKS.get(phase_id, [])
        phases_data.append({
            "id": phase_id,
            "name": phase_name,
            "description": phase_desc,
            "tasks": tasks,
        })
    return {
        "phases": phases_data,
        "book_type": book_type,
        "writing_mode": writing_mode,
        "genre_topic": genre_topic,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


async def get_or_create_journey(db: AsyncSession, user_id: str, onboarding: dict[str, Any]) -> UserJourney:
    """Create or update journey from onboarding answers."""
    from uuid import UUID

    uid = UUID(user_id)
    result = await db.execute(select(UserJourney).where(UserJourney.user_id == uid))
    journey = result.scalar_one_or_none()

    roadmap = generate_roadmap(
        onboarding.get("book_type", "fiction"),
        onboarding.get("writing_mode", "solo"),
        onboarding.get("genre_topic"),
    )

    if journey:
        journey.book_type = onboarding.get("book_type", journey.book_type)
        journey.writing_mode = onboarding.get("writing_mode", journey.writing_mode)
        journey.writing_goals = onboarding.get("writing_goals")
        journey.target_timeline = onboarding.get("target_timeline")
        journey.writing_schedule = onboarding.get("writing_schedule")
        journey.accountability_style = onboarding.get("accountability_style")
        journey.ai_comfort_level = onboarding.get("ai_comfort_level")
        journey.genre_topic = onboarding.get("genre_topic")
        journey.roadmap = roadmap
        journey.last_active_at = datetime.now(timezone.utc)
        await db.flush()
    else:
        journey = UserJourney(
            user_id=uid,
            book_type=onboarding.get("book_type", "fiction"),
            writing_mode=onboarding.get("writing_mode", "solo"),
            writing_goals=onboarding.get("writing_goals"),
            target_timeline=onboarding.get("target_timeline"),
            writing_schedule=onboarding.get("writing_schedule"),
            accountability_style=onboarding.get("accountability_style"),
            ai_comfort_level=onboarding.get("ai_comfort_level"),
            genre_topic=onboarding.get("genre_topic"),
            roadmap=roadmap,
            current_phase="idea",
            phase_started_at=datetime.now(timezone.utc),
            last_active_at=datetime.now(timezone.utc),
        )
        db.add(journey)
        await db.flush()
        await db.refresh(journey)
        await _seed_tasks(db, str(journey.id), "idea")

    await db.refresh(journey)
    return journey


async def _seed_tasks(db: AsyncSession, journey_id: str, phase: str) -> None:
    """Seed tasks for a phase."""
    from uuid import UUID

    jid = UUID(journey_id) if isinstance(journey_id, str) else journey_id
    tasks = PHASE_TASKS.get(phase, [])
    for i, t in enumerate(tasks):
        task = JourneyTask(
            journey_id=jid,
            phase=phase,
            sort_order=i,
            title=t["title"],
            task_type=t.get("task_type", "checklist"),
        )
        db.add(task)
    await db.flush()


async def get_next_step(db: AsyncSession, journey: UserJourney) -> dict[str, Any]:
    """Get the next recommended task for the user."""
    phase_id = journey.current_phase
    phase_idx = next((i for i, (pid, _, _) in enumerate(PHASES) if pid == phase_id), 0)
    phase_name = PHASES[phase_idx][1] if phase_idx < len(PHASES) else ""

    result = await db.execute(
        select(JourneyTask)
        .where(JourneyTask.journey_id == journey.id, JourneyTask.phase == phase_id)
        .order_by(JourneyTask.sort_order)
    )
    tasks = result.scalars().all()
    next_task = next((t for t in tasks if t.completed_at is None), None)

    if next_task:
        return {
            "phase": phase_id,
            "phase_name": phase_name,
            "task": {
                "id": str(next_task.id),
                "title": next_task.title,
                "description": next_task.description,
                "task_type": next_task.task_type,
            },
            "phase_progress": sum(1 for t in tasks if t.completed_at) / len(tasks) if tasks else 0,
            "total_phases": len(PHASES),
            "current_phase_index": phase_idx,
        }

    # All tasks in phase done - advance to next phase
    if phase_idx < len(PHASES) - 1:
        next_phase_id = PHASES[phase_idx + 1][0]
        next_phase_name = PHASES[phase_idx + 1][1]
        journey.current_phase = next_phase_id
        journey.phase_started_at = datetime.now(timezone.utc)
        journey.last_active_at = datetime.now(timezone.utc)
        await _seed_tasks(db, str(journey.id), next_phase_id)
        await db.flush()

        result = await db.execute(
            select(JourneyTask)
            .where(JourneyTask.journey_id == journey.id, JourneyTask.phase == next_phase_id)
            .order_by(JourneyTask.sort_order)
        )
        new_tasks = result.scalars().all()
        first_new = new_tasks[0] if new_tasks else None

        return {
            "phase": next_phase_id,
            "phase_name": next_phase_name,
            "task": {
                "id": str(first_new.id),
                "title": first_new.title,
                "description": first_new.description,
                "task_type": first_new.task_type,
            } if first_new else None,
            "phase_progress": 0,
            "total_phases": len(PHASES),
            "current_phase_index": phase_idx + 1,
            "phase_advanced": True,
        }

    # Journey complete
    journey.completed_at = datetime.now(timezone.utc)
    await db.flush()
    return {
        "phase": "complete",
        "phase_name": "Complete",
        "task": None,
        "phase_progress": 1,
        "total_phases": len(PHASES),
        "current_phase_index": len(PHASES),
        "journey_complete": True,
    }


async def complete_task(db: AsyncSession, task_id: str, user_id: str) -> JourneyTask | None:
    """Mark task complete and return updated task."""
    from uuid import UUID

    result = await db.execute(
        select(JourneyTask)
        .join(UserJourney)
        .where(JourneyTask.id == UUID(task_id), UserJourney.user_id == UUID(user_id))
    )
    task = result.scalar_one_or_none()
    if not task:
        return None
    task.completed_at = datetime.now(timezone.utc)
    journey = await db.get(UserJourney, task.journey_id)
    if journey:
        journey.last_active_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(task)
    return task


async def get_recovery_nudge(journey: UserJourney) -> dict[str, Any]:
    """Generate supportive nudge when user has been away."""
    if not journey.last_active_at:
        return {"type": "welcome_back", "message": "Welcome back! Ready to pick up where you left off?"}

    delta = datetime.now(timezone.utc) - journey.last_active_at
    days = delta.days

    if days == 0:
        return {"type": "momentum", "message": "You're on a roll. What's your next step?"}
    if days == 1:
        return {"type": "gentle", "message": "Good to see you again. No pressure—whenever you're ready."}
    if days < 7:
        return {"type": "supportive", "message": "Life gets busy. Your story is still here when you are."}
    if days < 30:
        return {"type": "warm", "message": "Welcome back! Your book is waiting. Let's find your next step."}
    return {"type": "fresh_start", "message": "It's never too late to continue. We'll help you find your way back."}
