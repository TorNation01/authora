"""Profitability maths: MRR, churn, CAC.

Pure functions only — no database, no clock. The monthly proof script
(`scripts/profitability.py`) feeds them rows and stores the result; the tests
prove the maths without touching production data.

Definitions used here, stated so nobody has to guess later:

* MRR counts recurring plans only. Monthly at face value, yearly divided by
  twelve, Lifetime Access at **zero** — a lifetime sale is revenue booked in
  the month it happens, never recurring revenue. Rolling it into MRR inflates
  the one number that decides whether this product is working.
* Churn is logo churn in basis points of the opening base (100 bps = 1%),
  so 5% is 500 bps and there is no float drift between months.
* CAC is cash marketing spend over paying customers won in the month. With no
  recorded spend it is 0 (organic), and with spend but no customers it is
  unknown — reported as null, not as an infinite or invented number.
"""

from __future__ import annotations

from typing import Any, Iterable

# --- The target (Nathan's decision, 2026-10-30: build to profitability) -------
# $2,000 MRR/month. At the $22.35 blended ARPU used for planning that is ~89
# paying subscribers. 5% monthly logo churn caps the leak; $67 CAC keeps
# payback inside three months at that ARPU.
MRR_TARGET_CENTS = 200_000
CHURN_TARGET_BPS = 500
CAC_TARGET_CENTS = 6_700
ARPU_BENCHMARK_CENTS = 2_235

TARGETS = {
    "mrr_target_cents": MRR_TARGET_CENTS,
    "churn_target_bps": CHURN_TARGET_BPS,
    "cac_target_cents": CAC_TARGET_CENTS,
    "arpu_benchmark_cents": ARPU_BENCHMARK_CENTS,
}

ACTIVE_STATUSES = frozenset({"active", "trialing"})
CHURNED_STATUSES = frozenset({"canceled", "unpaid", "incomplete_expired"})


def subscription_mrr_cents(sub: Any) -> int:
    """Recurring cents per month for one subscription row (dict or object)."""
    def get(key: str) -> Any:
        if isinstance(sub, dict):
            return sub.get(key)
        return getattr(sub, key, None)

    if get("is_lifetime"):
        return 0
    if (get("status") or "active") not in ACTIVE_STATUSES:
        return 0

    interval = get("billing_interval")
    monthly = get("price_monthly_cents")
    yearly = get("price_yearly_cents")
    if interval == "yearly" and yearly:
        return int(round(yearly / 12))
    if monthly:
        return int(monthly)
    return 0


def compute_mrr_cents(subs: Iterable[Any]) -> int:
    return sum(subscription_mrr_cents(s) for s in subs)


def compute_churn_bps(churned: int, active_at_start: int) -> int:
    """Logo churn in basis points; 0 when there was no base to lose."""
    if active_at_start <= 0:
        return 0
    return int(round(churned * 10_000 / active_at_start))


def compute_cac_cents(spend_cents: int, new_paid: int) -> int | None:
    """Cash CAC. None = spend with no customers won: unknown, not infinite."""
    if new_paid <= 0:
        return None if spend_cents > 0 else 0
    return int(round(spend_cents / new_paid))


def compute_arpu_cents(mrr_cents: int, paying_subs: int) -> int | None:
    if paying_subs <= 0:
        return None
    return int(round(mrr_cents / paying_subs))


def payback_months(cac_cents: int | None, arpu_cents: int = ARPU_BENCHMARK_CENTS) -> float | None:
    if cac_cents is None or arpu_cents <= 0:
        return None
    return round(cac_cents / arpu_cents, 2)


def subscribers_for_target(mrr_target_cents: int = MRR_TARGET_CENTS) -> int:
    import math

    return math.ceil(mrr_target_cents / ARPU_BENCHMARK_CENTS)
