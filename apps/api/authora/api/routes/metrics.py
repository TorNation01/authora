"""Growth metrics — the four numbers that decide whether Authora is a business.

    GET /api/v1/admin/metrics/growth?days=30

Every figure is read from the table that owns the fact (users / projects /
books / chapters / subscriptions / plans), never from an event stream that
can drift or miss accounts created before instrumentation. Fixture and probe
rows are included — this is an operator page, not a prospectus — and each
number carries its definition so nobody has to guess what "completed" means.

Definitions (also returned in `definitions` so the page can print them):

  signup               a row in `users` created inside the window
  trial_started        `users.trial_started_at` inside the window; the trial is
                       stamped at registration, before any card exists
  first_book_completed the user's earliest *complete draft* finished inside the
                       window. A complete draft = a book with at least one
                       chapter and every non-deleted chapter carrying words
                       (word_count > 0). Completion time is the last chapter edit.
  conversion           a user who trialled in the window and holds a paying
                       subscription at any status other than canceled/expired
  churn                a subscription that moved to canceled/unpaid/
                       incomplete_expired inside the window, over the paying
                       base that existed at the window's start. There is no
                       canceled_at column, so `updated_at` at the cancel status
                       is the timestamp — documented, not hidden.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from authora.api.dependencies import (
    AdminUser,
    get_db,
)

router = APIRouter(prefix="/admin/metrics", tags=["admin-metrics"])

PAYING_STATUSES = ("active", "trialing", "past_due")
CHURNED_STATUSES = ("canceled", "unpaid", "incomplete_expired")


async def _scalar(db: AsyncSession, sql: str, params: dict) -> int:
    value = (await db.execute(text(sql), params)).scalar()
    return int(value or 0)


@router.get("/growth")
async def growth_metrics(
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
):
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=days)
    params = {"since": since, "now": now, "days": days}

    # ---------------------------------------------------------------- funnel
    signups = await _scalar(
        db, "SELECT count(*) FROM users WHERE created_at >= :since", params
    )
    trials_started = await _scalar(
        db,
        "SELECT count(*) FROM users WHERE trial_started_at >= :since",
        params,
    )
    trials_active_now = await _scalar(
        db,
        """SELECT count(*) FROM users
            WHERE trial_ends_at IS NOT NULL AND trial_ends_at > :now""",
        params,
    )

    # Earliest complete draft per user; the completion timestamp is the last
    # chapter edit belonging to that book.
    book_rows = (
        await db.execute(
            text(
                """
                WITH per_book AS (
                    SELECT b.id                AS book_id,
                           p.user_id           AS user_id,
                           b.created_at        AS book_created_at,
                           count(c.id)         AS chapters,
                           count(c.id) FILTER (WHERE c.word_count > 0) AS written,
                           sum(c.word_count)   AS words,
                           max(c.updated_at)   AS finished_at
                      FROM books b
                      JOIN projects p ON p.id = b.project_id
                      LEFT JOIN chapters c
                             ON c.book_id = b.id AND c.deleted_at IS NULL
                     WHERE b.deleted_at IS NULL AND p.deleted_at IS NULL
                     GROUP BY b.id, p.user_id, b.created_at
                )
                SELECT user_id, book_id, chapters, written, words, finished_at
                  FROM per_book
                 WHERE chapters > 0 AND written = chapters
                 ORDER BY user_id, finished_at
                """
            )
        )
    ).all()
    first_complete: dict[str, dict] = {}
    for row in book_rows:
        uid = str(row.user_id)
        if uid not in first_complete:
            first_complete[uid] = {
                "book_id": str(row.book_id),
                "chapters": int(row.chapters),
                "words": int(row.words or 0),
                "finished_at": row.finished_at,
            }
    first_book_completed = sum(
        1
        for v in first_complete.values()
        if v["finished_at"] is not None and v["finished_at"] >= since
    )
    completed_total = len(first_complete)

    conversions = await _scalar(
        db,
        """SELECT count(DISTINCT user_id) FROM subscriptions
            WHERE created_at >= :since AND status = ANY(:statuses)""",
        {**params, "statuses": list(PAYING_STATUSES)},
    )
    converted_from_window_trials = await _scalar(
        db,
        """
        SELECT count(*) FROM users u
         WHERE u.trial_started_at >= :since
           AND EXISTS (
               SELECT 1 FROM subscriptions s
                WHERE s.user_id = u.id
                  AND s.status = ANY(:statuses)
                  AND s.created_at >= u.trial_started_at
           )
        """,
        {**params, "statuses": list(PAYING_STATUSES)},
    )
    signed_up_and_paid = await _scalar(
        db,
        """SELECT count(DISTINCT u.id) FROM users u
             JOIN subscriptions s ON s.user_id = u.id
            WHERE u.created_at >= :since AND s.status = ANY(:statuses)""",
        {**params, "statuses": list(PAYING_STATUSES)},
    )

    # ---------------------------------------------------------------- churn
    paying_at_start = await _scalar(
        db,
        """SELECT count(*) FROM subscriptions
            WHERE created_at < :since AND status = ANY(:statuses)""",
        {**params, "statuses": list(PAYING_STATUSES)},
    )
    churned = await _scalar(
        db,
        """SELECT count(*) FROM subscriptions
            WHERE updated_at >= :since AND status = ANY(:churn)""",
        {**params, "churn": list(CHURNED_STATUSES)},
    )
    pending_cancellations = await _scalar(
        db,
        """SELECT count(*) FROM subscriptions
            WHERE cancel_at_period_end = true AND status = ANY(:statuses)""",
        {**params, "statuses": list(PAYING_STATUSES)},
    )
    paying_now = await _scalar(
        db,
        """SELECT count(*) FROM subscriptions WHERE status = ANY(:statuses)""",
        {**params, "statuses": list(PAYING_STATUSES)},
    )

    # -------------------------------------------------------------- revenue
    mrr = (
        await db.execute(
            text(
                """
                SELECT coalesce(sum(
                         CASE s.billing_interval
                              WHEN 'monthly' THEN coalesce(pl.price_monthly_cents, 0)
                              WHEN 'yearly'  THEN coalesce(pl.price_yearly_cents, 0) / 12
                              WHEN 'lifetime' THEN 0
                              ELSE coalesce(pl.price_monthly_cents, 0)
                         END), 0)
                  FROM subscriptions s
                  JOIN plans pl ON pl.id = s.plan_id
                 WHERE s.status = ANY(:statuses)
                """
            ),
            {"statuses": list(PAYING_STATUSES)},
        )
    ).scalar() or 0
    mrr_cents = int(round(float(mrr)))

    # --------------------------------------------------------------- series
    series_rows = (
        await db.execute(
            text(
                """
                WITH d AS (
                    SELECT generate_series(
                        date_trunc('day', CAST(:since AS timestamptz)),
                        date_trunc('day', CAST(:now AS timestamptz)),
                        interval '1 day'
                    )::date AS day
                )
                SELECT d.day,
                       (SELECT count(*) FROM users u
                         WHERE u.created_at::date = d.day)              AS signups,
                       (SELECT count(*) FROM users u
                         WHERE u.trial_started_at::date = d.day)        AS trials,
                       (SELECT count(*) FROM subscriptions s
                         WHERE s.created_at::date = d.day
                           AND s.status = ANY(:statuses))               AS conversions
                  FROM d ORDER BY d.day
                """
            ),
            {**params, "statuses": list(PAYING_STATUSES)},
        )
    ).all()

    def pct(num: int, den: int) -> float | None:
        return round(num / den * 100, 1) if den else None

    return {
        "period_days": days,
        "since": since.isoformat(),
        "generated_at": now.isoformat(),
        "funnel": {
            "signups": signups,
            "trials_started": trials_started,
            "first_book_completed": first_book_completed,
            "conversions": conversions,
        },
        "conversion": {
            "signup_to_paid_pct": pct(signed_up_and_paid, signups),
            "trial_to_paid_pct": pct(converted_from_window_trials, trials_started),
            "trials_active_now": trials_active_now,
            "converted_from_window_trials": converted_from_window_trials,
        },
        "churn": {
            "paying_at_period_start": paying_at_start,
            "paying_now": paying_now,
            "churned_in_window": churned,
            "churn_pct": pct(churned, paying_at_start),
            "pending_cancellations": pending_cancellations,
        },
        "revenue": {
            "mrr_cents": mrr_cents,
            "paying_customers": paying_now,
            "arpu_cents": int(round(mrr_cents / paying_now)) if paying_now else None,
        },
        "books": {
            "first_book_completed_total": completed_total,
            "completed_book_ids": [v["book_id"] for v in first_complete.values()],
        },
        "series": [
            {
                "day": r.day.isoformat(),
                "signups": int(r.signups or 0),
                "trials": int(r.trials or 0),
                "conversions": int(r.conversions or 0),
            }
            for r in series_rows
        ],
        "definitions": {
            "signup": "a row in users created inside the window",
            "trial_started": "users.trial_started_at inside the window (stamped at registration)",
            "first_book_completed": (
                "the user's earliest book with >=1 chapter where every non-deleted "
                "chapter has word_count > 0, finished inside the window"
            ),
            "conversion": "a user who trialled in the window and holds an active/trialing/past_due subscription",
            "churn": "subscriptions moved to canceled/unpaid/incomplete_expired in the window, over the paying base at window start (updated_at is the cancel timestamp)",
            "mrr": "monthly plan price + yearly/12 for active subscriptions; lifetime counted as 0 recurring",
        },
    }
