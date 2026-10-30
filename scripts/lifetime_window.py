#!/usr/bin/env python3
"""Open or close the Lifetime Access window.

The lifetime offer is a window, not a product. Checkout refuses to sell it
outside the window, and the pricing API hides the price entirely while it is
closed — so this script is the only honest way to put it on sale.

Usage
-----
    lifetime_window.py status
    lifetime_window.py open --days 14
    lifetime_window.py open --until 2026-11-30T23:59:59+08:00
    lifetime_window.py close
    lifetime_window.py price --cents 49900     # optional, changes the price

Honest limits, stated on every run:
  * Closing the window stops NEW sales. It does not revoke anyone who already
    bought Lifetime Access — their entitlement is permanent, as promised.
  * A closed window is reported to the browser as "not on sale" and the price
    is removed from the plans payload. There is no cached price to leak.
  * Reopening does not resurrect an old Stripe price; it reuses the plan row's
    price_lifetime_cents. If you change the price, existing owners keep access.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG = "founder_lifetime"  # internal slug; display name is "Lifetime Access"


def database_url() -> str:
    candidates = [ROOT / ".env", ROOT / "apps" / "api" / ".env"]
    for path in candidates:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.startswith("DATABASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    env = os.environ.get("DATABASE_URL")
    if env:
        return env
    sys.exit("DATABASE_URL not found in .env or the environment.")


def sql(statement: str) -> str:
    result = subprocess.run(
        ["psql", database_url(), "-At", "-F", "|", "-c", statement],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"psql failed: {result.stderr.strip()}")
    return result.stdout.strip()


def show_status() -> int:
    row = sql(
        f"""
        select coalesce(to_char(lifetime_available_from at time zone 'Australia/Perth','YYYY-MM-DD HH24:MI'),'—'),
               coalesce(to_char(lifetime_available_to   at time zone 'Australia/Perth','YYYY-MM-DD HH24:MI'),'—'),
               coalesce(price_lifetime_cents,0)
        from plans where slug='{SLUG}';
        """
    )
    if not row:
        print(f"No plan with slug '{SLUG}' — nothing to open or close.")
        return 1
    start, end, cents = row.split("|")
    open_now = sql(
        f"""
        select case
          when lifetime_available_to is null then 'closed'
          when now() between coalesce(lifetime_available_from, now() - interval '100 years')
                          and lifetime_available_to then 'open'
          else 'closed' end
        from plans where slug='{SLUG}';
        """
    )
    print(f"Lifetime Access ({SLUG}) — AWST")
    print(f"  price          ${int(cents)/100:,.2f}")
    print(f"  window opens   {start}")
    print(f"  window closes  {end}")
    print(f"  state          {open_now.upper()}")
    if open_now == "open":
        print("  checkout       will accept a lifetime purchase")
    else:
        print("  checkout       refuses with 403 lifetime_offer_closed; price hidden from /billing/plans")
    print()
    print("Reminder: closing only stops new sales. Existing lifetime owners keep access forever.")
    return 0


def open_window(days: int | None, until: str | None) -> int:
    if until:
        end_expr = f"timestamptz '{until}'"
    elif days:
        end_expr = f"now() + interval '{int(days)} days'"
    else:
        sys.exit("Give --days N or --until <ISO timestamp>.")
    sql(
        f"""
        update plans
           set lifetime_available_from = now(),
               lifetime_available_to   = {end_expr}
         where slug='{SLUG}';
        """
    )
    print("Lifetime Access is ON SALE.")
    return show_status()


def close_window() -> int:
    sql(
        f"""
        update plans
           set lifetime_available_to = now()
         where slug='{SLUG}';
        """
    )
    print("Lifetime Access is CLOSED. No new lifetime purchases can be made.")
    return show_status()


def set_price(cents: int) -> int:
    sql(
        f"""
        update plans set price_lifetime_cents = {int(cents)}
         where slug='{SLUG}';
        """
    )
    print(f"Lifetime price set to ${int(cents)/100:,.2f}. Existing owners are unaffected.")
    return show_status()


def main() -> int:
    parser = argparse.ArgumentParser(description="Open or close the Authora Lifetime Access window.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show the current window and whether checkout accepts it")

    p_open = sub.add_parser("open", help="put Lifetime Access on sale")
    p_open.add_argument("--days", type=int, help="run the sale for this many days from now")
    p_open.add_argument("--until", help="run until this ISO timestamp, e.g. 2026-11-30T23:59:59+08:00")

    sub.add_parser("close", help="end the sale now")

    p_price = sub.add_parser("price", help="change the lifetime price in cents")
    p_price.add_argument("--cents", type=int, required=True)

    args = parser.parse_args()
    if args.command == "status":
        return show_status()
    if args.command == "open":
        return open_window(args.days, args.until)
    if args.command == "close":
        return close_window()
    if args.command == "price":
        return set_price(args.cents)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
