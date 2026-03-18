"""Network effect service: template usage, creator attribution, sharing triggers, referral loops."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    AnalyticsEvent,
    CreatorProfile,
    Project,
    ProjectTemplate,
    Referral,
    TemplatePurchase,
    User,
)

# Event types for network effects
EVENT_TEMPLATE_USAGE_STARTED = "template_usage_started"
EVENT_CREATOR_SIGNUP_ATTRIBUTED = "creator_signup_attributed"
EVENT_SHARE_TRIGGER_SHOWN = "share_trigger_shown"
EVENT_SHARE_COMPLETED = "share_completed"
EVENT_REFERRAL_SIGNUP = "referral_signup"


async def record_template_usage_started(
    db: AsyncSession,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    template_id: uuid.UUID,
    *,
    template_slug: str | None = None,
    creator_id: uuid.UUID | None = None,
) -> None:
    """Record that a user started using a template (project created with template)."""
    props: dict[str, Any] = {
        "template_id": str(template_id),
        "project_id": str(project_id),
    }
    if template_slug:
        props["template_slug"] = template_slug
    if creator_id:
        props["creator_id"] = str(creator_id)
    event = AnalyticsEvent(
        user_id=user_id,
        event_type=EVENT_TEMPLATE_USAGE_STARTED,
        resource_type="template",
        resource_id=str(template_id),
        properties=props,
    )
    db.add(event)
    await db.flush()


async def record_creator_signup_attributed(
    db: AsyncSession,
    creator_id: uuid.UUID,
    referred_user_id: uuid.UUID,
    *,
    referral_id: uuid.UUID | None = None,
    source: str = "referral",
) -> None:
    """Record that a creator drove a signup (creator attribution)."""
    props: dict[str, Any] = {
        "creator_id": str(creator_id),
        "referred_user_id": str(referred_user_id),
        "source": source,
    }
    if referral_id:
        props["referral_id"] = str(referral_id)
    event = AnalyticsEvent(
        user_id=referred_user_id,
        event_type=EVENT_CREATOR_SIGNUP_ATTRIBUTED,
        resource_type="creator",
        resource_id=str(creator_id),
        properties=props,
    )
    db.add(event)
    await db.flush()


async def record_share_trigger_shown(
    db: AsyncSession,
    user_id: uuid.UUID,
    trigger_type: str,
    *,
    resource_id: str | None = None,
    properties: dict[str, Any] | None = None,
) -> None:
    """Record that a share trigger was shown to the user."""
    props = dict(properties or {})
    props["trigger_type"] = trigger_type
    if resource_id:
        props["resource_id"] = resource_id
    event = AnalyticsEvent(
        user_id=user_id,
        event_type=EVENT_SHARE_TRIGGER_SHOWN,
        resource_type="share",
        resource_id=resource_id,
        properties=props,
    )
    db.add(event)
    await db.flush()


async def record_share_completed(
    db: AsyncSession,
    user_id: uuid.UUID,
    share_type: str,
    *,
    share_link_id: uuid.UUID | None = None,
    properties: dict[str, Any] | None = None,
) -> None:
    """Record that user completed a share."""
    props = dict(properties or {})
    props["share_type"] = share_type
    if share_link_id:
        props["share_link_id"] = str(share_link_id)
    event = AnalyticsEvent(
        user_id=user_id,
        event_type=EVENT_SHARE_COMPLETED,
        resource_type="share",
        properties=props,
    )
    db.add(event)
    await db.flush()


# --- Queries: which templates drive usage ---


async def get_templates_driving_usage(
    db: AsyncSession,
    *,
    days: int = 30,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Templates ranked by usage (projects + purchases) in last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    r_proj = await db.execute(
        select(Project.template_id, func.count(Project.id).label("cnt"))
        .where(
            Project.template_id.isnot(None),
            Project.created_at >= since,
        )
        .group_by(Project.template_id)
    )
    by_template: dict[uuid.UUID, int] = {tid: c for tid, c in r_proj.all()}

    r_purch = await db.execute(
        select(TemplatePurchase.template_id, func.count(TemplatePurchase.id).label("cnt"))
        .where(TemplatePurchase.created_at >= since)
        .group_by(TemplatePurchase.template_id)
    )
    for tid, c in r_purch.all():
        by_template[tid] = by_template.get(tid, 0) + c

    if not by_template:
        return []

    template_ids = sorted(by_template.keys(), key=lambda x: -by_template[x])[:limit]
    r_t = await db.execute(
        select(ProjectTemplate.id, ProjectTemplate.slug, ProjectTemplate.name, ProjectTemplate.creator_id)
        .where(ProjectTemplate.id.in_(template_ids), ProjectTemplate.is_disabled.is_(False))
    )
    rows = {r[0]: r for r in r_t.all()}

    creator_ids = {r[3] for r in rows.values() if r[3]}
    creator_names: dict[uuid.UUID, str] = {}
    if creator_ids:
        r_u = await db.execute(
            select(User.id, User.display_name, User.email).where(User.id.in_(creator_ids))
        )
        creator_names = {r[0]: (r[1] or r[2] or "Creator") for r in r_u.all()}

    return [
        {
            "template_id": str(tid),
            "slug": rows[tid][1],
            "name": rows[tid][2],
            "creator_id": str(rows[tid][3]) if rows[tid][3] else None,
            "creator_name": creator_names.get(rows[tid][3]) if rows[tid][3] else None,
            "usage_count": by_template[tid],
        }
        for tid in template_ids
        if tid in rows
    ]


# --- Queries: which creators drive signups ---


async def get_creators_driving_signups(
    db: AsyncSession,
    *,
    days: int = 90,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Creators ranked by attributed signups in last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    r = await db.execute(
        select(
            func.jsonb_extract_path_text(AnalyticsEvent.properties, "creator_id").label("creator_id"),
            func.count(AnalyticsEvent.id).label("cnt"),
        )
        .where(
            AnalyticsEvent.event_type == EVENT_CREATOR_SIGNUP_ATTRIBUTED,
            AnalyticsEvent.created_at >= since,
            func.jsonb_extract_path_text(AnalyticsEvent.properties, "creator_id") != "",
        )
        .group_by(func.jsonb_extract_path_text(AnalyticsEvent.properties, "creator_id"))
        .order_by(func.count(AnalyticsEvent.id).desc())
        .limit(limit)
    )
    rows = r.all()
    if not rows:
        return []

    creator_ids = [uuid.UUID(cid) for cid, _ in rows if cid]
    r_u = await db.execute(
        select(User.id, User.display_name, User.email).where(User.id.in_(creator_ids))
    )
    creator_map = {r[0]: (r[1] or r[2] or "Creator") for r in r_u.all()}

    return [
        {
            "creator_id": str(cid),
            "creator_name": creator_map.get(uuid.UUID(cid)),
            "signups": cnt,
        }
        for cid, cnt in rows
        if cid
    ]


# --- Queries: which features drive retention ---


async def get_features_driving_retention(
    db: AsyncSession,
    *,
    days: int = 30,
) -> dict[str, Any]:
    """Feature usage that correlates with retention (first_* events)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    retention_events = [
        "first_project_created",
        "first_chapter_created",
        "first_writing_session_started",
        "first_milestone_completed",
        "first_export_completed",
        "first_ai_assist_used",
        "first_idea_captured",
        "first_streak_started",
    ]

    r = await db.execute(
        select(AnalyticsEvent.event_type, func.count(AnalyticsEvent.id).label("cnt"))
        .where(
            AnalyticsEvent.event_type.in_(retention_events),
            AnalyticsEvent.created_at >= since,
        )
        .group_by(AnalyticsEvent.event_type)
    )
    by_event = {row[0]: row[1] for row in r.all()}

    return {
        "period_days": days,
        "events": {e: by_event.get(e, 0) for e in retention_events},
    }


# --- Sharing trigger suggestions ---


async def get_share_trigger_suggestions(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[dict[str, Any]]:
    """Suggest moments when user should share (based on recent activity)."""
    from authora.models import Book, Chapter, Milestone

    suggestions: list[dict[str, Any]] = []

    # Check: first chapter completed
    r_ch = await db.execute(
        select(func.count(Chapter.id))
        .join(Book, Book.id == Chapter.book_id)
        .join(Project, Project.id == Book.project_id)
        .where(Project.user_id == user_id)
    )
    chapter_count = r_ch.scalar() or 0
    if chapter_count >= 1:
        r_shown = await db.execute(
            select(AnalyticsEvent.id).where(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.event_type == EVENT_SHARE_TRIGGER_SHOWN,
                func.jsonb_extract_path_text(AnalyticsEvent.properties, "trigger_type") == "first_chapter",
            ).limit(1)
        )
        if not r_shown.scalar_one_or_none():
            suggestions.append({
                "trigger_type": "first_chapter",
                "message": "You wrote your first chapter! Share your progress.",
                "share_type": "progress",
            })

    # Check: milestone completed (Milestone has user_id)
    r_mil = await db.execute(
        select(func.count(Milestone.id)).where(
            Milestone.user_id == user_id,
            Milestone.completed_at.isnot(None),
        )
    )
    if (r_mil.scalar() or 0) >= 1:
        r_shown = await db.execute(
            select(AnalyticsEvent.id).where(
                AnalyticsEvent.user_id == user_id,
                AnalyticsEvent.event_type == EVENT_SHARE_TRIGGER_SHOWN,
                func.jsonb_extract_path_text(AnalyticsEvent.properties, "trigger_type") == "milestone",
            ).limit(1)
        )
        if not r_shown.scalar_one_or_none():
            suggestions.append({
                "trigger_type": "milestone",
                "message": "You hit a milestone! Share with friends.",
                "share_type": "milestone",
            })

    return suggestions[:3]


# --- Referral loop: ensure Referral exists when user gets code ---


async def ensure_referral_record(
    db: AsyncSession,
    user_id: uuid.UUID,
    referral_code: str,
) -> None:
    """Ensure a Referral record exists for this inviter's code (for resolve on signup)."""
    r = await db.execute(
        select(Referral.id).where(Referral.referral_code == referral_code).limit(1)
    )
    if r.scalar_one_or_none():
        return
    ref = Referral(
        inviter_id=user_id,
        referral_code=referral_code,
        status="pending",
    )
    db.add(ref)
    await db.flush()


async def is_creator(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Check if user is an approved creator."""
    r = await db.execute(
        select(CreatorProfile.id).where(
            CreatorProfile.user_id == user_id,
            CreatorProfile.status == "approved",
        ).limit(1)
    )
    return r.scalar_one_or_none() is not None
