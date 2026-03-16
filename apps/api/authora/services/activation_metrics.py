"""Activation metrics aggregation for admin dashboards.

Queries analytics_events and related tables to compute activation rates,
time-to-value, template usage, and retention indicators.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import AnalyticsEvent, Project, ProjectTemplate, User
from authora.services.onboarding_analytics import (
    EVENT_FIRST_CHAPTER_CREATED,
    EVENT_FIRST_EXPORT_COMPLETED,
    EVENT_FIRST_PROJECT_CREATED,
    EVENT_ONBOARDING_COMPLETED,
    EVENT_ONBOARDING_STARTED,
    EVENT_PROJECT_WIZARD_COMPLETED,
    EVENT_PROJECT_WIZARD_STARTED,
)


async def get_activation_summary(
    db: AsyncSession,
    *,
    since: datetime | None = None,
) -> dict[str, Any]:
    """Aggregate activation metrics for admin dashboard."""
    if since is None:
        since = datetime.now(timezone.utc) - timedelta(days=30)

    # Count users who completed each activation event (ever)
    event_counts = {}
    for event_type in [
        EVENT_ONBOARDING_STARTED,
        EVENT_ONBOARDING_COMPLETED,
        EVENT_PROJECT_WIZARD_STARTED,
        EVENT_PROJECT_WIZARD_COMPLETED,
        EVENT_FIRST_PROJECT_CREATED,
        EVENT_FIRST_CHAPTER_CREATED,
        EVENT_FIRST_EXPORT_COMPLETED,
    ]:
        r = (
            await db.execute(
                select(func.count(func.distinct(AnalyticsEvent.user_id))).where(
                    AnalyticsEvent.event_type == event_type,
                    AnalyticsEvent.created_at >= since,
                )
            )
        ).scalar() or 0
        event_counts[event_type] = r

    # Total users (created since)
    total_users = (
        await db.execute(
            select(func.count(User.id)).where(User.created_at >= since)
        )
    ).scalar() or 0

    # Activation rate: users with first_project_created / total users
    first_project = event_counts.get(EVENT_FIRST_PROJECT_CREATED, 0)
    activation_rate = (first_project / total_users * 100) if total_users > 0 else 0

    # Onboarding completion rate
    onboarding_started = event_counts.get(EVENT_ONBOARDING_STARTED, 0)
    onboarding_completed = event_counts.get(EVENT_ONBOARDING_COMPLETED, 0)
    onboarding_completion_rate = (
        (onboarding_completed / onboarding_started * 100) if onboarding_started > 0 else 0
    )

    return {
        "period": {"since": since.isoformat(), "days": 30},
        "total_users": total_users,
        "activation_rate_pct": round(activation_rate, 1),
        "event_counts": event_counts,
        "onboarding_completion_rate_pct": round(onboarding_completion_rate, 1),
    }


async def get_time_to_first_project(db: AsyncSession, since_days: int = 30) -> list[dict[str, Any]]:
    """Time from registration to first project created (in hours)."""
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    subq = (
        select(
            AnalyticsEvent.user_id,
            func.min(AnalyticsEvent.created_at).label("first_project_at"),
        )
        .where(
            AnalyticsEvent.event_type == EVENT_FIRST_PROJECT_CREATED,
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.user_id)
    )
    result = await db.execute(
        select(User.id, User.created_at, subq.c.first_project_at)
        .join(subq, User.id == subq.c.user_id)
        .limit(500)
    )
    rows = result.all()
    deltas: list[float] = []
    for user_id, created_at, first_at in rows:
        if created_at and first_at:
            delta = (first_at - created_at).total_seconds() / 3600
            deltas.append(delta)
    deltas.sort()
    n = len(deltas)
    return [
        {"metric": "time_to_first_project_hours", "count": n},
        {"metric": "median_hours", "value": deltas[n // 2] if n else 0},
        {"metric": "p90_hours", "value": deltas[int(n * 0.9)] if n >= 10 else 0},
    ]


async def get_time_to_first_chapter(db: AsyncSession, since_days: int = 30) -> dict[str, Any]:
    """Time from first project to first chapter (approximation from events)."""
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    project_rows = (
        await db.execute(
            select(AnalyticsEvent.user_id, AnalyticsEvent.created_at).where(
                AnalyticsEvent.event_type == EVENT_FIRST_PROJECT_CREATED,
                AnalyticsEvent.created_at >= since,
            )
        )
    ).all()
    chapter_rows = (
        await db.execute(
            select(
                AnalyticsEvent.user_id,
                func.min(AnalyticsEvent.created_at).label("chapter_at"),
            )
            .where(
                AnalyticsEvent.event_type == EVENT_FIRST_CHAPTER_CREATED,
                AnalyticsEvent.created_at >= since,
            )
            .group_by(AnalyticsEvent.user_id)
        )
    ).all()
    project_by_user: dict[Any, datetime] = {}
    for uid, created in project_rows:
        if uid not in project_by_user or created < project_by_user[uid]:
            project_by_user[uid] = created
    deltas: list[float] = []
    for uid, chapter_at in chapter_rows:
        if uid in project_by_user and chapter_at and chapter_at >= project_by_user[uid]:
            delta = (chapter_at - project_by_user[uid]).total_seconds() / 3600
            deltas.append(delta)
    deltas.sort()
    n = len(deltas)
    return {
        "count": n,
        "median_hours": round(deltas[n // 2], 1) if n else 0,
        "p90_hours": round(deltas[int(n * 0.9)], 1) if n >= 10 else 0,
    }


async def get_template_usage(db: AsyncSession, since_days: int = 30) -> list[dict[str, Any]]:
    """Template usage from project_wizard_completed and projects."""
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    slug_col = func.coalesce(
        func.jsonb_extract_path_text(AnalyticsEvent.properties, "template_slug"), ""
    )
    r = (
        await db.execute(
            select(slug_col.label("slug"), func.count(AnalyticsEvent.id).label("cnt"))
            .where(
                AnalyticsEvent.event_type == EVENT_PROJECT_WIZARD_COMPLETED,
                AnalyticsEvent.created_at >= since,
                func.jsonb_extract_path_text(AnalyticsEvent.properties, "template_slug") != "",
            )
            .group_by(slug_col)
        )
    )
    by_slug = {row[0]: row[1] for row in r.all() if row[0]}

    # Also from projects.template_id
    templates = (
        await db.execute(
            select(ProjectTemplate.slug, func.count(Project.id).label("cnt"))
            .join(Project, Project.template_id == ProjectTemplate.id)
            .where(Project.created_at >= since)
            .group_by(ProjectTemplate.slug)
        )
    ).all()
    for slug, cnt in templates:
        by_slug[slug] = by_slug.get(slug, 0) + cnt

    return [{"template_slug": k, "count": v} for k, v in sorted(by_slug.items(), key=lambda x: -x[1])]


async def get_mode_selection_rates(db: AsyncSession, since_days: int = 30) -> list[dict[str, Any]]:
    """Guidance mode selection from project_wizard_completed."""
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    mode_col = func.coalesce(
        func.jsonb_extract_path_text(AnalyticsEvent.properties, "guidance_mode"), "unknown"
    )
    r = (
        await db.execute(
            select(mode_col.label("mode"), func.count(AnalyticsEvent.id).label("cnt"))
            .where(
                AnalyticsEvent.event_type == EVENT_PROJECT_WIZARD_COMPLETED,
                AnalyticsEvent.created_at >= since,
            )
            .group_by(mode_col)
        )
    )
    return [{"mode": row[0] or "unknown", "count": row[1]} for row in r.all()]


async def get_starter_path_usage(db: AsyncSession, since_days: int = 30) -> list[dict[str, Any]]:
    """Starter path usage from project_wizard_completed (starter_slug in properties)."""
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    slug_col = func.jsonb_extract_path_text(AnalyticsEvent.properties, "starter_slug")
    r = (
        await db.execute(
            select(slug_col.label("slug"), func.count(AnalyticsEvent.id).label("cnt"))
            .where(
                AnalyticsEvent.event_type == EVENT_PROJECT_WIZARD_COMPLETED,
                AnalyticsEvent.created_at >= since,
                func.jsonb_extract_path_text(AnalyticsEvent.properties, "starter_slug") != "",
            )
            .group_by(slug_col)
        )
    )
    return [{"starter_slug": row[0] or "", "count": row[1]} for row in r.all()]


async def get_first_week_retention(db: AsyncSession, since_days: int = 30) -> dict[str, Any]:
    """Users who returned within 7 days of registration (approximation via first_chapter or first_export)."""
    since = datetime.now(timezone.utc) - timedelta(days=since_days)
    first_project_users = (
        await db.execute(
            select(AnalyticsEvent.user_id).where(
                AnalyticsEvent.event_type == EVENT_FIRST_PROJECT_CREATED,
                AnalyticsEvent.created_at >= since,
            )
        )
    ).scalars().all()
    user_ids = [r[0] for r in first_project_users]
    if not user_ids:
        return {"total": 0, "returned_within_7_days": 0, "retention_pct": 0}

    # Count users with any project last_accessed_at within 7 days of first project
    # Simplified: users with first_chapter or first_export within 7 days of first_project
    first_project_at = (
        select(
            AnalyticsEvent.user_id,
            func.min(AnalyticsEvent.created_at).label("at"),
        )
        .where(
            AnalyticsEvent.event_type == EVENT_FIRST_PROJECT_CREATED,
            AnalyticsEvent.user_id.in_(user_ids),
        )
        .group_by(AnalyticsEvent.user_id)
    )
    # Users with first_chapter within 7 days
    result = await db.execute(
        select(AnalyticsEvent.user_id)
        .where(
            AnalyticsEvent.event_type.in_([EVENT_FIRST_CHAPTER_CREATED, EVENT_FIRST_EXPORT_COMPLETED]),
            AnalyticsEvent.user_id.in_(user_ids),
        )
    )
    returned_ids = set(r[0] for r in result.all())
    return {
        "total": len(user_ids),
        "returned_within_7_days": len(returned_ids),
        "retention_pct": round(len(returned_ids) / len(user_ids) * 100, 1) if user_ids else 0,
    }
