"""Funnel instrumentation — anonymous visits and the five-stage ladder.

Why this exists: `analytics_events` only ever held authenticated product
events, so the first number anyone could read was "4 users". The drop between
a stranger landing on the marketing site and an account existing was invisible,
and acquisition was the bottleneck. This module closes both ends of the
ladder:

    POST /api/v1/analytics/visit        anonymous page-view beacon (public)
    GET  /api/v1/admin/funnel/ladder     visit -> signup -> first book ->
                                        first chapter -> paid, with conversion

Rules the beacon obeys:
  * best effort — it never raises into the caller, and never breaks a page;
  * no raw IP, no user agent, no email is stored: only a client cookie id,
    the path, the referrer host and the utm tags;
  * crawlers are dropped by user agent, so the visit count is people;
  * every field is length-capped; an oversized payload is a 422, not a row.

The ladder is read from ground-truth tables (users / projects / chapters /
subscriptions), not from the events, so it stays correct for accounts that
predate the instrumentation. Events are used only for attribution.
"""

import logging
import re
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import String, cast, distinct, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import AdminUser, get_db
from authora.models.analytics_event import AnalyticsEvent
from authora.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analytics", tags=["analytics"])
admin_router = APIRouter(prefix="/admin", tags=["analytics-admin"])

EVENT_PAGE_VIEW = "page_view"
EVENT_SIGNUP_COMPLETED = "signup_completed"

# Crawlers and synthetic clients. A visit metric that counts Googlebot is a
# vanity number; the whole point of the top of the funnel is real people.
_BOT_UA = re.compile(
    r"(bot|crawler|spider|crawling|slurp|bingpreview|googlebot|bingbot|yandex|baidu|"
    r"duckduckbot|semrush|ahrefs|mj12|python-requests|python-urllib|curl/|wget/|"
    r"headlesschrome|phantomjs|facebookexternalhit|preview)",
    re.IGNORECASE,
)


class VisitIn(BaseModel):
    """A single page view from the browser or the Next middleware."""

    path: str = Field(..., min_length=1, max_length=512)
    referrer: str | None = Field(None, max_length=512)
    visitor_id: str | None = Field(None, max_length=64)
    utm_source: str | None = Field(None, max_length=64)
    utm_medium: str | None = Field(None, max_length=64)
    utm_campaign: str | None = Field(None, max_length=64)


def _is_bot(user_agent: str | None) -> bool:
    return bool(user_agent and _BOT_UA.search(user_agent))


def _referrer_host(referrer: str | None) -> str | None:
    if not referrer:
        return None
    try:
        host = referrer.split("://", 1)[-1].split("/", 1)[0].lower()
    except Exception:  # pragma: no cover - defensive
        return None
    return host[:128] or None


@router.post("/visit", status_code=202)
async def record_visit(
    body: VisitIn,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Record one anonymous page view. Public, no auth, never raises.

    Returns 202 because the write is bookkeeping: the caller (a page load or
    the Next middleware) must never wait on, or fail because of, analytics.
    """
    try:
        if _is_bot(request.headers.get("user-agent")):
            return {"ok": True, "recorded": False, "reason": "crawler"}

        path = body.path.split("?", 1)[0][:512] or "/"
        props = {
            "path": path,
            "visitor_id": (body.visitor_id or "").strip()[:64] or None,
            "referrer_host": _referrer_host(body.referrer),
            "utm_source": body.utm_source,
            "utm_medium": body.utm_medium,
            "utm_campaign": body.utm_campaign,
        }
        db.add(
            AnalyticsEvent(
                user_id=None,
                event_type=EVENT_PAGE_VIEW,
                resource_type="page",
                resource_id=path[:100],
                properties={k: v for k, v in props.items() if v},
            )
        )
        await db.commit()
        return {"ok": True, "recorded": True}
    except Exception:
        # Analytics must never be the reason a page fails to load.
        logger.warning("page_view beacon failed", exc_info=True)
        try:
            await db.rollback()
        except Exception:  # pragma: no cover
            pass
        return {"ok": True, "recorded": False, "reason": "error"}


@admin_router.get("/funnel/ladder")
async def funnel_ladder(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    """The whole money ladder in one call: visit -> signup -> book -> chapter -> paid.

    Each stage counts *people who reached it* inside the window, read from the
    table that owns the fact, so the numbers survive a change in event naming:

      visit         distinct visitor ids on page_view events
      signup        rows in users
      first_book    users whose first project was created in the window
      first_chapter users whose first chapter was created in the window
      paid          users with an active subscription created in the window

    A stage's `conversion_pct` is against the stage above it; `overall_pct` is
    against visits. Fixture and probe accounts are in these rows — the shape is
    directional, and the endpoint says so rather than pretending otherwise.
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    page_views = (
        await db.execute(
            select(func.count(AnalyticsEvent.id)).where(
                AnalyticsEvent.event_type == EVENT_PAGE_VIEW,
                AnalyticsEvent.created_at >= since,
            )
        )
    ).scalar_one() or 0

    visitors = (
        await db.execute(
            select(
                func.count(
                    distinct(
                        func.coalesce(
                            func.jsonb_extract_path_text(AnalyticsEvent.properties, "visitor_id"),
                            cast(AnalyticsEvent.id, String),
                        )
                    )
                )
            ).where(
                AnalyticsEvent.event_type == EVENT_PAGE_VIEW,
                AnalyticsEvent.created_at >= since,
            )
        )
    ).scalar_one() or 0

    signups = (
        await db.execute(select(func.count(User.id)).where(User.created_at >= since))
    ).scalar_one() or 0

    first_book = (
        await db.execute(
            text(
                """
                SELECT count(*) FROM (
                    SELECT user_id FROM projects
                    WHERE deleted_at IS NULL
                    GROUP BY user_id
                    HAVING min(created_at) >= :since
                ) reached
                """
            ),
            {"since": since},
        )
    ).scalar_one() or 0

    first_chapter = (
        await db.execute(
            text(
                """
                SELECT count(*) FROM (
                    SELECT p.user_id FROM chapters c
                    JOIN books b ON b.id = c.book_id
                    JOIN projects p ON p.id = b.project_id
                    WHERE c.deleted_at IS NULL
                    GROUP BY p.user_id
                    HAVING min(c.created_at) >= :since
                ) reached
                """
            ),
            {"since": since},
        )
    ).scalar_one() or 0

    paid = (
        await db.execute(
            text(
                """
                SELECT count(DISTINCT user_id) FROM subscriptions
                WHERE status = 'active' AND created_at >= :since
                """
            ),
            {"since": since},
        )
    ).scalar_one() or 0

    attributed_signups = (
        await db.execute(
            select(func.count(AnalyticsEvent.id)).where(
                AnalyticsEvent.event_type == EVENT_SIGNUP_COMPLETED,
                AnalyticsEvent.created_at >= since,
            )
        )
    ).scalar_one() or 0

    sources = (
        await db.execute(
            select(
                func.coalesce(
                    func.jsonb_extract_path_text(AnalyticsEvent.properties, "utm_source"),
                    func.jsonb_extract_path_text(AnalyticsEvent.properties, "referrer_host"),
                    "direct",
                ).label("source"),
                func.count(AnalyticsEvent.id).label("visits"),
            )
            .where(
                AnalyticsEvent.event_type == EVENT_PAGE_VIEW,
                AnalyticsEvent.created_at >= since,
            )
            .group_by("source")
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(8)
        )
    ).all()

    paths = (
        await db.execute(
            select(
                func.coalesce(func.jsonb_extract_path_text(AnalyticsEvent.properties, "path"), "/").label("path"),
                func.count(AnalyticsEvent.id).label("views"),
            )
            .where(
                AnalyticsEvent.event_type == EVENT_PAGE_VIEW,
                AnalyticsEvent.created_at >= since,
            )
            .group_by("path")
            .order_by(func.count(AnalyticsEvent.id).desc())
            .limit(8)
        )
    ).all()

    raw = [
        ("visit", "Visited the site", visitors),
        ("signup", "Created an account", signups),
        ("first_book", "Started a book", first_book),
        ("first_chapter", "Wrote a first chapter", first_chapter),
        ("paid", "Paid", paid),
    ]
    stages = []
    previous = None
    for key, label, count in raw:
        stages.append(
            {
                "key": key,
                "label": label,
                "count": int(count or 0),
                "conversion_pct": (
                    None if previous in (None, 0) else round((count or 0) / previous * 100, 1)
                ),
                "overall_pct": round((count or 0) / visitors * 100, 2) if visitors else None,
            }
        )
        previous = count or 0

    return {
        "period_days": days,
        "since": since.isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stages": stages,
        "page_views": int(page_views),
        "attributed_signups": int(attributed_signups),
        "visits_by_source": [{"source": s, "visits": int(v)} for s, v in sources],
        "visits_by_path": [{"path": p, "views": int(v)} for p, v in paths],
        "caveat": (
            "Fixture and probe accounts are included; visits count distinct "
            "browser cookie ids and exclude known crawlers."
        ),
    }
