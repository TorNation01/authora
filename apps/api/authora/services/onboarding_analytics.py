"""Onboarding and activation analytics service.

Records events to analytics_events for measuring user activation,
drop-off, and retention. Production-ready for dashboards and reporting.
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import AnalyticsEvent, Book, Chapter, ExportJob, Goal, Project, User, UserPreference

# ─── Event type constants ────────────────────────────────────────────────────

# Activation events (positive signals)
EVENT_ONBOARDING_STARTED = "onboarding_started"
EVENT_ONBOARDING_COMPLETED = "onboarding_completed"
EVENT_PROJECT_WIZARD_STARTED = "project_wizard_started"
EVENT_PROJECT_WIZARD_COMPLETED = "project_wizard_completed"
EVENT_FIRST_PROJECT_CREATED = "first_project_created"
EVENT_FIRST_CHAPTER_CREATED = "first_chapter_created"
EVENT_FIRST_WRITING_SESSION_STARTED = "first_writing_session_started"
EVENT_FIRST_MILESTONE_COMPLETED = "first_milestone_completed"
EVENT_FIRST_EXPORT_COMPLETED = "first_export_completed"
EVENT_FIRST_AI_ASSIST_USED = "first_ai_assist_used"
EVENT_FIRST_IDEA_CAPTURED = "first_idea_captured"
EVENT_FIRST_STREAK_STARTED = "first_streak_started"

# Drop-off / abandonment events
EVENT_ONBOARDING_ABANDONMENT = "onboarding_abandonment"
EVENT_TEMPLATE_SELECTION_ABANDONMENT = "template_selection_abandonment"
EVENT_ACCOUNTABILITY_SETUP_ABANDONMENT = "accountability_setup_abandonment"
EVENT_FIRST_CHAPTER_NOT_CREATED = "first_chapter_not_created"
EVENT_NO_WRITING_WITHIN_3_DAYS = "no_writing_within_3_days"
EVENT_NO_RETURN_WITHIN_7_DAYS = "no_return_within_7_days"


async def record_event(
    db: AsyncSession,
    user_id: uuid.UUID,
    event_type: str,
    *,
    resource_type: str | None = None,
    resource_id: str | None = None,
    properties: dict[str, Any] | None = None,
) -> None:
    """Record an analytics event. Idempotent for first-* events (checks if already recorded)."""
    # For first-* events, only record if user hasn't already triggered this event
    if event_type.startswith("first_") and event_type in (
        EVENT_FIRST_PROJECT_CREATED,
        EVENT_FIRST_CHAPTER_CREATED,
        EVENT_FIRST_WRITING_SESSION_STARTED,
        EVENT_FIRST_MILESTONE_COMPLETED,
        EVENT_FIRST_EXPORT_COMPLETED,
        EVENT_FIRST_AI_ASSIST_USED,
        EVENT_FIRST_IDEA_CAPTURED,
        EVENT_FIRST_STREAK_STARTED,
    ):
        existing = (
            await db.execute(
                select(AnalyticsEvent.id).where(
                    AnalyticsEvent.user_id == user_id,
                    AnalyticsEvent.event_type == event_type,
                ).limit(1)
            )
        ).scalar_one_or_none()
        if existing:
            return

    event = AnalyticsEvent(
        user_id=user_id,
        event_type=event_type,
        resource_type=resource_type,
        resource_id=resource_id,
        properties=properties or {},
    )
    db.add(event)
    await db.flush()


async def record_onboarding_started(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Record that user started onboarding. Idempotent (once per user)."""
    existing = (
        await db.execute(
            select(AnalyticsEvent.id).where(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.event_type == EVENT_ONBOARDING_STARTED,
            ).limit(1)
        )
    ).scalar_one_or_none()
    if existing:
        return
    await record_event(db, user_id, EVENT_ONBOARDING_STARTED)


async def record_onboarding_completed(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Record that user completed onboarding. Idempotent (once per user)."""
    existing = (
        await db.execute(
            select(AnalyticsEvent.id).where(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.event_type == EVENT_ONBOARDING_COMPLETED,
            ).limit(1)
        )
    ).scalar_one_or_none()
    if existing:
        return
    await record_event(db, user_id, EVENT_ONBOARDING_COMPLETED)


async def record_project_wizard_started(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Record that user started project creation wizard."""
    await record_event(db, user_id, EVENT_PROJECT_WIZARD_STARTED)


async def record_project_wizard_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    *,
    template_id: uuid.UUID | None = None,
    template_slug: str | None = None,
    guidance_mode: str | None = None,
    starter_slug: str | None = None,
) -> None:
    """Record that user completed project creation wizard."""
    props: dict[str, Any] = {}
    if template_id:
        props["template_id"] = str(template_id)
    if template_slug:
        props["template_slug"] = template_slug
    if guidance_mode:
        props["guidance_mode"] = guidance_mode
    if starter_slug:
        props["starter_slug"] = starter_slug
    await record_event(
        db,
        user_id,
        EVENT_PROJECT_WIZARD_COMPLETED,
        resource_type="project",
        properties=props if props else None,
    )


async def record_first_project_created(
    db: AsyncSession,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    template_slug: str | None = None,
    from_wizard: bool = False,
) -> None:
    """Record first project created (activation milestone)."""
    await record_event(
        db,
        user_id,
        EVENT_FIRST_PROJECT_CREATED,
        resource_type="project",
        resource_id=str(project_id),
        properties={
            "template_slug": template_slug,
            "from_wizard": from_wizard,
        },
    )


async def record_first_chapter_created(
    db: AsyncSession,
    user_id: uuid.UUID,
    chapter_id: uuid.UUID,
    book_id: uuid.UUID,
) -> None:
    """Record first chapter created (activation milestone)."""
    await record_event(
        db,
        user_id,
        EVENT_FIRST_CHAPTER_CREATED,
        resource_type="chapter",
        resource_id=str(chapter_id),
        properties={"book_id": str(book_id)},
    )


async def record_first_export_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    book_id: uuid.UUID,
    format: str,
) -> None:
    """Record first export completed (activation milestone)."""
    await record_event(
        db,
        user_id,
        EVENT_FIRST_EXPORT_COMPLETED,
        resource_type="book",
        resource_id=str(book_id),
        properties={"format": format},
    )


async def record_first_ai_assist_used(
    db: AsyncSession,
    user_id: uuid.UUID,
    action_slug: str,
) -> None:
    """Record first AI assist used (activation milestone)."""
    await record_event(
        db,
        user_id,
        EVENT_FIRST_AI_ASSIST_USED,
        properties={"action_slug": action_slug},
    )


async def record_first_idea_captured(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Record first idea captured in vault (activation milestone)."""
    await record_event(db, user_id, EVENT_FIRST_IDEA_CAPTURED)


async def record_first_streak_started(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Record first streak started (activation milestone)."""
    await record_event(db, user_id, EVENT_FIRST_STREAK_STARTED)


async def record_first_milestone_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    milestone_id: str,
) -> None:
    """Record first milestone completed (activation milestone)."""
    await record_event(
        db,
        user_id,
        EVENT_FIRST_MILESTONE_COMPLETED,
        properties={"milestone_id": milestone_id},
    )


async def record_first_writing_session_started(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Record first writing session (e.g. focus mode or first chapter edit)."""
    await record_event(db, user_id, EVENT_FIRST_WRITING_SESSION_STARTED)


async def record_abandonment(
    db: AsyncSession,
    user_id: uuid.UUID,
    event_type: str,
    *,
    step_index: int | None = None,
    properties: dict[str, Any] | None = None,
) -> None:
    """Record drop-off/abandonment event."""
    props = dict(properties or {})
    if step_index is not None:
        props["step_index"] = step_index
    await record_event(
        db,
        user_id,
        event_type,
        properties=props if props else None,
    )
