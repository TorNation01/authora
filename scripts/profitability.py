#!/usr/bin/env python3
"""Authora profitability proof — MRR, churn and CAC, monthly.

The target lives in `profitability_targets` (seeded by migration 073); this
script measures the business against it and stores one row per month in
`profitability_snapshots`, so the number Nathan is held to has a series behind
it instead of a memory.

    profitability.py targets                 # show the target and what it implies
    profitability.py set-targets --mrr 2000 --churn 5 --cac 67
    profitability.py snapshot                # write the current month's row
    profitability.py snapshot --previous     # the month that just ended (timer)
    profitability.py snapshot --spend 250    # record $250 marketing spend
    profitability.py report                  # every stored month vs target
    profitability.py check                   # CI/cron gate: fails on drift

Honest limits, stated in the output too:
  * Lifetime Access is revenue, never MRR. It is reported separately.
  * Historic months are reconstructed from current subscription rows, so they
    are directional; only the live month reconciles exactly (and `check` says so).
  * With no recorded spend CAC reads 0 (organic). Spend with no customers won
    reads "unknown" — never an invented number.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

from authora.services.profitability import (  # noqa: E402
    ARPU_BENCHMARK_CENTS,
    CHURNED_STATUSES,
    CHURN_TARGET_BPS,
    CAC_TARGET_CENTS,
    MRR_TARGET_CENTS,
    compute_arpu_cents,
    compute_cac_cents,
    compute_churn_bps,
    compute_mrr_cents,
    payback_months,
    subscribers_for_target,
)

SUBS_SQL = """
SELECT s.id::text, p.slug, p.price_monthly_cents, p.price_yearly_cents,
       p.price_lifetime_cents, s.billing_interval, s.is_lifetime, s.status,
       s.created_at::text, s.updated_at::text
FROM subscriptions s JOIN plans p ON p.id = s.plan_id
ORDER BY s.created_at
"""


def database_url() -> str:
    for path in (ROOT / ".env", ROOT / "apps" / "api" / ".env"):
        if path.exists():
            for line in path.read_text().splitlines():
                if line.startswith("DATABASE_URL="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    env = os.environ.get("DATABASE_URL")
    if env:
        return env
    sys.exit("DATABASE_URL not found in .env or the environment.")


def q(sql: str) -> list[list[str]]:
    result = subprocess.run(
        ["psql", database_url(), "-At", "-F", "\x1f", "-c", sql],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"psql failed: {result.stderr.strip()}")
    return [line.split("\x1f") for line in result.stdout.splitlines() if line]


def scalar(sql: str) -> str | None:
    rows = q(sql)
    return rows[0][0] if rows else None


def to_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


def subscriptions() -> list[dict]:
    out = []
    for r in q(SUBS_SQL):
        out.append(
            {
                "id": r[0],
                "plan_slug": r[1],
                "price_monthly_cents": int(r[2]) if r[2] else None,
                "price_yearly_cents": int(r[3]) if r[3] else None,
                "price_lifetime_cents": int(r[4]) if r[4] else None,
                "billing_interval": r[5] or None,
                "is_lifetime": r[6] == "t",
                "status": r[7],
                "created_at": to_dt(r[8]),
                "updated_at": to_dt(r[9]),
            }
        )
    return out


def month_window(month: str | None, previous: bool) -> tuple[date, date, str]:
    today = date.today()
    if month:
        year, mon = (int(x) for x in month.split("-", 1))
        start = date(year, mon, 1)
    elif previous:
        start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    else:
        start = today.replace(day=1)
    end = (start.replace(day=28) + timedelta(days=4)).replace(day=1)
    return start, end, start.strftime("%Y-%m")


def measure(start: date, end: date, spend_cents: int) -> dict:
    subs = subscriptions()
    now = datetime.now(timezone.utc)
    cutoff = min(now, datetime(end.year, end.month, end.day, tzinfo=timezone.utc))
    start_dt = datetime(start.year, start.month, start.day, tzinfo=timezone.utc)
    end_dt = datetime(end.year, end.month, end.day, tzinfo=timezone.utc)

    active_now = [s for s in subs if s["status"] == "active"]
    active_at_start = [
        s
        for s in subs
        if s["created_at"] and s["created_at"] < start_dt
        and (s["status"] == "active" or (s["updated_at"] and s["updated_at"] >= start_dt))
    ]
    churned = [
        s
        for s in subs
        if s["status"] in CHURNED_STATUSES and s["updated_at"] and start_dt <= s["updated_at"] < end_dt
    ]
    new_paid = [
        s
        for s in subs
        if s["created_at"] and start_dt <= s["created_at"] < cutoff
        and (s["is_lifetime"] or (s["price_monthly_cents"] or 0) > 0 or (s["price_yearly_cents"] or 0) > 0)
    ]

    recurring = [s for s in active_now if not s["is_lifetime"]]
    mrr = compute_mrr_cents(recurring)
    churn_bps = compute_churn_bps(len(churned), len(active_at_start))
    cac = compute_cac_cents(spend_cents, len(new_paid))

    return {
        "month": start.isoformat(),
        "mrr_cents": mrr,
        "active_recurring_subs": len(recurring),
        "active_lifetime_subs": len([s for s in active_now if s["is_lifetime"]]),
        "new_paid_subs": len(new_paid),
        "churned_subs": len(churned),
        "churn_bps": churn_bps,
        "arpu_cents": compute_arpu_cents(mrr, len(recurring)),
        "marketing_spend_cents": spend_cents,
        "cac_cents": cac,
        "source": "live",
    }


def targets() -> dict | None:
    rows = q(
        "SELECT mrr_target_cents, churn_target_bps, cac_target_cents, arpu_benchmark_cents, notes "
        "FROM profitability_targets ORDER BY created_at LIMIT 1"
    )
    if not rows:
        return None
    r = rows[0]
    return {
        "mrr_target_cents": int(r[0]),
        "churn_target_bps": int(r[1]),
        "cac_target_cents": int(r[2]),
        "arpu_benchmark_cents": int(r[3]),
        "notes": r[4],
    }


def money(cents: int | None) -> str:
    if cents is None:
        return "unknown"
    return f"${cents / 100:,.2f}"


def cmd_targets(_: argparse.Namespace) -> int:
    t = targets()
    if not t:
        print("NOT SET — no row in profitability_targets")
        return 1
    print(f"Target MRR        {money(t['mrr_target_cents'])}/mo")
    print(f"  = subscribers   {subscribers_for_target(t['mrr_target_cents'])} at {money(t['arpu_benchmark_cents'])} ARPU")
    print(f"Churn ceiling     {t['churn_target_bps'] / 100:.2f}% / month")
    print(f"CAC ceiling       {money(t['cac_target_cents'])} (payback {payback_months(t['cac_target_cents'], t['arpu_benchmark_cents'])} months)")
    print(f"Notes             {t['notes']}")
    return 0


def cmd_set_targets(args: argparse.Namespace) -> int:
    mrr = args.mrr if args.mrr is not None else MRR_TARGET_CENTS // 100
    churn_bps = int(round((args.churn if args.churn is not None else CHURN_TARGET_BPS / 100) * 100))
    cac = args.cac if args.cac is not None else CAC_TARGET_CENTS // 100
    existing = scalar("SELECT id::text FROM profitability_targets ORDER BY created_at LIMIT 1")
    if existing:
        q(
            "UPDATE profitability_targets SET "
            f"mrr_target_cents={int(mrr) * 100}, churn_target_bps={churn_bps}, "
            f"cac_target_cents={int(cac) * 100}, updated_at=now() WHERE id='{existing}'"
        )
        print(f"updated target: ${mrr}/mo MRR, {churn_bps / 100:.2f}% churn, ${cac} CAC")
    else:
        q(
            "INSERT INTO profitability_targets (id, mrr_target_cents, churn_target_bps, "
            f"cac_target_cents) VALUES (gen_random_uuid(), {int(mrr) * 100}, {churn_bps}, {int(cac) * 100})"
        )
        print(f"set target: ${mrr}/mo MRR, {churn_bps / 100:.2f}% churn, ${cac} CAC")
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    start, end, label = month_window(args.month, args.previous)
    spend = int(round(args.spend * 100)) if args.spend is not None else 0
    row = measure(start, end, spend)
    q(
        "INSERT INTO profitability_snapshots "
        "(month, mrr_cents, active_recurring_subs, active_lifetime_subs, new_paid_subs, "
        " churned_subs, churn_bps, arpu_cents, marketing_spend_cents, cac_cents, source) VALUES "
        f"('{row['month']}', {row['mrr_cents']}, {row['active_recurring_subs']}, "
        f"{row['active_lifetime_subs']}, {row['new_paid_subs']}, {row['churned_subs']}, "
        f"{row['churn_bps']}, {row['arpu_cents'] if row['arpu_cents'] is not None else 'NULL'}, "
        f"{row['marketing_spend_cents']}, {row['cac_cents'] if row['cac_cents'] is not None else 'NULL'}, "
        f"'{row['source']}') "
        "ON CONFLICT (month) DO UPDATE SET "
        "mrr_cents=EXCLUDED.mrr_cents, active_recurring_subs=EXCLUDED.active_recurring_subs, "
        "active_lifetime_subs=EXCLUDED.active_lifetime_subs, new_paid_subs=EXCLUDED.new_paid_subs, "
        "churned_subs=EXCLUDED.churned_subs, churn_bps=EXCLUDED.churn_bps, arpu_cents=EXCLUDED.arpu_cents, "
        "marketing_spend_cents=EXCLUDED.marketing_spend_cents, cac_cents=EXCLUDED.cac_cents, "
        "source=EXCLUDED.source, computed_at=now()"
    )
    print(
        f"{label}: MRR {money(row['mrr_cents'])} · {row['active_recurring_subs']} recurring "
        f"+ {row['active_lifetime_subs']} lifetime · new paid {row['new_paid_subs']} · "
        f"churn {row['churn_bps'] / 100:.2f}% · CAC {money(row['cac_cents'])}"
    )
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    t = targets()
    rows = q(
        "SELECT month::text, mrr_cents, active_recurring_subs, active_lifetime_subs, new_paid_subs, "
        "churned_subs, churn_bps, arpu_cents, marketing_spend_cents, cac_cents "
        "FROM profitability_snapshots ORDER BY month"
    )
    if not rows:
        print("no snapshots — run `profitability.py snapshot`")
        return 1
    tgt_mrr = t["mrr_target_cents"] if t else MRR_TARGET_CENTS
    print(f"month     MRR          /target   progress  subs  churn    CAC")
    for r in rows:
        mrr = int(r[1])
        pct = (mrr / tgt_mrr * 100) if tgt_mrr else 0
        print(
            f"{r[0]}  {money(mrr):<12} {money(tgt_mrr):<9} {pct:5.1f}%   {r[2]:>3}   "
            f"{int(r[6]) / 100:5.2f}%  {money(int(r[9]) if r[9] else None)}"
        )
    if args.json:
        print(json.dumps([dict(zip(
            ["month", "mrr_cents", "active_recurring_subs", "active_lifetime_subs", "new_paid_subs",
             "churned_subs", "churn_bps", "arpu_cents", "marketing_spend_cents", "cac_cents"], r))
            for r in rows], indent=1, default=str))
    return 0


def cmd_check(_: argparse.Namespace) -> int:
    failures: list[str] = []
    stored: dict | None = None
    t = targets()
    if not t:
        failures.append("no target row in profitability_targets")
    elif t["mrr_target_cents"] <= 0:
        failures.append("mrr_target_cents is not positive")

    today_start, today_end, label = month_window(None, False)
    rows = q(
        "SELECT mrr_cents, active_recurring_subs, active_lifetime_subs, new_paid_subs, churned_subs, churn_bps "
        f"FROM profitability_snapshots WHERE month='{today_start.isoformat()}'"
    )
    if not rows:
        failures.append(f"no snapshot for {label} — the monthly proof has not run")
    else:
        live = measure(today_start, today_end, 0)
        stored = {
            "mrr_cents": int(rows[0][0]),
            "active_recurring_subs": int(rows[0][1]),
            "active_lifetime_subs": int(rows[0][2]),
            "new_paid_subs": int(rows[0][3]),
            "churned_subs": int(rows[0][4]),
            "churn_bps": int(rows[0][5]),
        }
        for key in ("mrr_cents", "active_recurring_subs", "active_lifetime_subs", "new_paid_subs", "churn_bps"):
            if stored[key] != live[key]:
                failures.append(f"{label} {key}: stored {stored[key]} != live {live[key]}")

    if failures or stored is None:
        print("PROFITABILITY CHECK FAILED")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(
        f"PROFITABILITY CHECK PASSED — {label} snapshot reconciles: "
        f"MRR {money(stored['mrr_cents'])}, {stored['active_recurring_subs']} recurring, "
        f"churn {stored['churn_bps'] / 100:.2f}%, target {money(t['mrr_target_cents'])}/mo"
    )
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Authora monthly profitability proof")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("targets").set_defaults(func=cmd_targets)

    st = sub.add_parser("set-targets")
    st.add_argument("--mrr", type=float, help="target MRR in dollars")
    st.add_argument("--churn", type=float, help="monthly logo churn ceiling in percent")
    st.add_argument("--cac", type=float, help="CAC ceiling in dollars")
    st.set_defaults(func=cmd_set_targets)

    sn = sub.add_parser("snapshot")
    sn.add_argument("--month", help="YYYY-MM (default: current month)")
    sn.add_argument("--previous", action="store_true", help="the month that just ended")
    sn.add_argument("--spend", type=float, help="marketing spend for the month, in dollars")
    sn.set_defaults(func=cmd_snapshot)

    rp = sub.add_parser("report")
    rp.add_argument("--json", action="store_true")
    rp.set_defaults(func=cmd_report)

    sub.add_parser("check").set_defaults(func=cmd_check)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
