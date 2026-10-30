"""Profitability invariants — MRR, churn, CAC.

These tests encode the contract the monthly profitability proof must meet.
They are deliberately pure: no database, no clock, no network, so the maths
can be proven independently of whichever month the report runs for.
"""

from __future__ import annotations

from authora.services.profitability import (
    ARPU_BENCHMARK_CENTS,
    CAC_TARGET_CENTS,
    CHURN_TARGET_BPS,
    MRR_TARGET_CENTS,
    compute_cac_cents,
    compute_churn_bps,
    subscription_mrr_cents,
)


def _sub(monthly=None, yearly=None, interval=None, lifetime=False, status="active"):
    return {
        "price_monthly_cents": monthly,
        "price_yearly_cents": yearly,
        "billing_interval": interval,
        "is_lifetime": lifetime,
        "status": status,
    }


def test_monthly_subscription_counts_at_full_price():
    assert subscription_mrr_cents(_sub(monthly=2400, interval="monthly")) == 2400


def test_yearly_subscription_is_divided_by_twelve():
    assert subscription_mrr_cents(_sub(monthly=2400, yearly=21600, interval="yearly")) == 1800


def test_lifetime_is_revenue_not_mrr():
    assert subscription_mrr_cents(_sub(monthly=4900, lifetime=True, interval="lifetime")) == 0


def test_inactive_subscription_is_not_mrr():
    assert subscription_mrr_cents(_sub(monthly=2400, interval="monthly", status="canceled")) == 0


def test_churn_is_basis_points_of_the_opening_base():
    assert compute_churn_bps(churned=1, active_at_start=20) == 500  # 5.00%
    assert compute_churn_bps(churned=0, active_at_start=1) == 0


def test_churn_with_no_opening_base_is_zero_not_a_division_error():
    assert compute_churn_bps(churned=0, active_at_start=0) == 0


def test_cac_is_spend_over_new_paying_customers():
    assert compute_cac_cents(spend_cents=20000, new_paid=4) == 5000


def test_cac_is_unknown_when_no_one_paid():
    assert compute_cac_cents(spend_cents=20000, new_paid=0) is None


def test_cac_is_zero_when_spend_is_zero():
    assert compute_cac_cents(spend_cents=0, new_paid=3) == 0


def test_targets_are_set_and_payback_is_inside_three_months():
    assert MRR_TARGET_CENTS == 200_000, "target MRR is $2,000/month"
    assert 0 < CHURN_TARGET_BPS <= 1000, "monthly logo churn target must be 0-10%"
    assert CAC_TARGET_CENTS > 0
    payback_months = CAC_TARGET_CENTS / ARPU_BENCHMARK_CENTS
    assert payback_months <= 3.0, f"CAC payback {payback_months:.2f} months exceeds 3"
