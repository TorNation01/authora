"""Creator growth service: featured creators, trending templates, top sellers, analytics."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import (
    AnalyticsEvent,
    CreatorEarning,
    CreatorProfile,
    Project,
    ProjectTemplate,
    TemplatePurchase,
    User,
)

EVENT_TEMPLATE_VIEWED = "template_viewed"


async def record_template_view(
    db: AsyncSession,
    template_id: uuid.UUID,
    user_id: uuid.UUID | None,
) -> None:
    """Record a template view (preview opened)."""
    event = AnalyticsEvent(
        user_id=user_id,
        event_type=EVENT_TEMPLATE_VIEWED,
        resource_type="template",
        resource_id=str(template_id),
        properties={"template_id": str(template_id)},
    )
    db.add(event)
    await db.flush()


async def get_template_views(db: AsyncSession, template_id: uuid.UUID) -> int:
    """Count template views from analytics_events."""
    r = await db.execute(
        select(func.count(AnalyticsEvent.id)).where(
            AnalyticsEvent.event_type == EVENT_TEMPLATE_VIEWED,
            AnalyticsEvent.resource_id == str(template_id),
        )
    )
    return r.scalar() or 0


async def get_template_analytics(
    db: AsyncSession,
    template_id: uuid.UUID,
) -> dict[str, Any]:
    """Get analytics for a template: views, conversions (purchases + projects), earnings (if creator template)."""
    views = await get_template_views(db, template_id)

    r_purchases = await db.execute(
        select(func.count(TemplatePurchase.id)).where(
            TemplatePurchase.template_id == template_id
        )
    )
    purchases = r_purchases.scalar() or 0

    r_projects = await db.execute(
        select(func.count(Project.id)).where(Project.template_id == template_id)
    )
    projects = r_projects.scalar() or 0

    conversions = purchases + projects

    r_template = await db.execute(
        select(ProjectTemplate).where(ProjectTemplate.id == template_id)
    )
    template = r_template.scalar_one_or_none()
    earnings_cents = 0
    if template and template.creator_id:
        r_earnings = await db.execute(
            select(func.coalesce(func.sum(CreatorEarning.amount_cents), 0)).where(
                CreatorEarning.creator_id == template.creator_id,
                CreatorEarning.template_purchase_id.in_(
                    select(TemplatePurchase.id).where(
                        TemplatePurchase.template_id == template_id
                    )
                ),
            )
        )
        earnings_cents = r_earnings.scalar() or 0

    return {
        "template_id": str(template_id),
        "views": views,
        "conversions": conversions,
        "purchases": purchases,
        "projects_started": projects,
        "earnings_cents": earnings_cents,
    }


async def get_featured_creators(
    db: AsyncSession,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """List featured creators with display name."""
    r = await db.execute(
        select(CreatorProfile, User.display_name, User.email)
        .join(User, CreatorProfile.user_id == User.id)
        .where(
            CreatorProfile.status == "approved",
            CreatorProfile.is_featured.is_(True),
        )
        .limit(limit)
    )
    rows = r.all()
    return [
        {
            "creator_id": str(p.user_id),
            "display_name": dn or email or "Creator",
            "email": email,
        }
        for p, dn, email in rows
    ]


async def get_trending_templates(
    db: AsyncSession,
    *,
    days: int = 7,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Templates with highest recent activity (projects + purchases in last N days)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # Projects created with template
    r_proj = await db.execute(
        select(Project.template_id, func.count(Project.id).label("cnt"))
        .where(
            Project.template_id.isnot(None),
            Project.created_at >= since,
        )
        .group_by(Project.template_id)
    )
    by_template: dict[uuid.UUID, int] = {tid: c for tid, c in r_proj.all()}

    # Purchases
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
    r_templates = await db.execute(
        select(ProjectTemplate.id, ProjectTemplate.slug, ProjectTemplate.name, ProjectTemplate.creator_id)
        .where(ProjectTemplate.id.in_(template_ids), ProjectTemplate.is_disabled.is_(False))
    )
    template_rows = {row[0]: row for row in r_templates.all()}

    creator_ids = {row[3] for row in template_rows.values() if row[3]}
    creator_names: dict[uuid.UUID, str] = {}
    if creator_ids:
        r_users = await db.execute(
            select(User.id, User.display_name, User.email).where(User.id.in_(creator_ids))
        )
        creator_names = {
            row[0]: (row[1] or row[2] or "Creator")
            for row in r_users.all()
        }

    return [
        {
            "template_id": str(tid),
            "slug": template_rows[tid][1],
            "name": template_rows[tid][2],
            "creator_name": creator_names.get(template_rows[tid][3]) if template_rows[tid][3] else None,
            "activity_count": by_template[tid],
        }
        for tid in template_ids
        if tid in template_rows
    ]


async def get_top_sellers(
    db: AsyncSession,
    *,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Templates by total sales count (TemplatePurchase)."""
    r = await db.execute(
        select(
            TemplatePurchase.template_id,
            func.count(TemplatePurchase.id).label("sales"),
            func.coalesce(func.sum(TemplatePurchase.amount_cents), 0).label("revenue_cents"),
        )
        .group_by(TemplatePurchase.template_id)
        .order_by(func.count(TemplatePurchase.id).desc())
        .limit(limit)
    )
    rows = r.all()
    if not rows:
        return []

    template_ids = [tid for tid, _, _ in rows]
    r_templates = await db.execute(
        select(ProjectTemplate.id, ProjectTemplate.slug, ProjectTemplate.name, ProjectTemplate.creator_id)
        .where(ProjectTemplate.id.in_(template_ids), ProjectTemplate.is_disabled.is_(False))
    )
    template_rows = {row[0]: row for row in r_templates.all()}

    creator_ids = {row[3] for row in template_rows.values() if row[3]}
    creator_names: dict[uuid.UUID, str] = {}
    if creator_ids:
        r_users = await db.execute(
            select(User.id, User.display_name, User.email).where(User.id.in_(creator_ids))
        )
        creator_names = {
            row[0]: (row[1] or row[2] or "Creator")
            for row in r_users.all()
        }

    return [
        {
            "template_id": str(tid),
            "slug": template_rows[tid][1],
            "name": template_rows[tid][2],
            "creator_name": creator_names.get(template_rows[tid][3]) if template_rows[tid][3] else None,
            "sales": sales,
            "revenue_cents": rev,
        }
        for tid, sales, rev in rows
        if tid in template_rows
    ]
