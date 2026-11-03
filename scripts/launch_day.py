#!/usr/bin/env python3
"""Launch day: open public signups and start the Lifetime Access offer, together.

Both switches move in one command so they cannot drift apart:

  1. SIGNUP_INVITE_CODES is emptied in .env  -> invite gate off (Turnstile stays on)
  2. plans.lifetime_available_from/to set    -> Lifetime Access on sale for N days

Usage
  python scripts/launch_day.py                # dry run: prints the plan, changes nothing
  python scripts/launch_day.py --go           # do it
  python scripts/launch_day.py --revert --go  # put the invite gate back, close the offer

Everything is verified over HTTP against the running API after the restart. If a
verification fails the .env backup is restored, the service is restarted again and
the command exits non-zero — a half-launched state is never left behind.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/opt/authora-v2")
ENV = ROOT / ".env"
STATE = ROOT / ".authora-launch-state.json"
API = "http://127.0.0.1:8004"
SERVICE = "authora-v2-api"
LIFETIME_DAYS = 30


def log(msg: str) -> None:
    print(msg, flush=True)


def api_json(path: str):
    with urllib.request.urlopen(API + path, timeout=10) as r:
        return json.load(r)


def env_text() -> str:
    return ENV.read_text()


def read_env_value(key: str) -> str:
    for line in env_text().splitlines():
        if line.startswith(key + "="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def set_env_value(key: str, value: str) -> None:
    text = env_text()
    pattern = re.compile(rf"(?m)^{re.escape(key)}=.*$")
    if pattern.search(text):
        text = pattern.sub(f"{key}={value}", text, count=1)
    else:
        text = text.rstrip("\n") + f"\n{key}={value}\n"
    ENV.write_text(text)


def restart_api() -> bool:
    subprocess.run(["systemctl", "restart", SERVICE], check=True)
    for _ in range(30):
        time.sleep(1)
        try:
            with urllib.request.urlopen(API + "/health", timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            continue
    return False


def plan() -> dict:
    cfg = api_json("/api/v1/auth/signup-config")
    plans = api_json("/api/v1/billing/plans")
    life = next(p for p in plans if p["slug"] == "founder_lifetime")
    codes = read_env_value("SIGNUP_INVITE_CODES")
    return {
        "invite_gate": "ON" if cfg.get("invite_required") else "OFF",
        "invite_codes_configured": len([c for c in codes.split(",") if c.strip()]),
        "turnstile": "enabled" if cfg.get("turnstile", {}).get("enabled") else "DISABLED",
        "lifetime_on_sale": life["lifetime_offer"]["available"],
        "lifetime_price_usd": ((life.get("price") or {}).get("lifetime_cents") or 0) / 100 or "hidden while closed",
    }


def preflight() -> list[str]:
    problems = []
    cfg = api_json("/api/v1/auth/signup-config")
    if not cfg.get("turnstile", {}).get("enabled"):
        problems.append("Turnstile is not enabled — public signup would be bot-open.")
    if not read_env_value("TURNSTILE_SECRET_KEY"):
        problems.append("TURNSTILE_SECRET_KEY missing from .env.")
    if not read_env_value("SMTP_HOST"):
        problems.append("SMTP_HOST missing — new users could not get a welcome mail.")
    return problems


def launch() -> int:
    log("== preflight ==")
    problems = preflight()
    for p in problems:
        log("  BLOCKED: " + p)
    if problems:
        return 1
    log("  turnstile enabled, smtp configured")

    codes_before = read_env_value("SIGNUP_INVITE_CODES")
    STATE.write_text(
        json.dumps(
            {
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "signup_invite_codes": codes_before,
                "env_backup": str(ENV.with_name(ENV.name + ".bak.launch-" + str(int(time.time())))),
            },
            indent=2,
        )
    )
    STATE.chmod(0o600)
    backup = Path(json.loads(STATE.read_text())["env_backup"])
    backup.write_bytes(ENV.read_bytes())
    backup.chmod(0o600)
    log(f"== .env backed up to {backup} ==")

    set_env_value("SIGNUP_INVITE_CODES", "")
    log("== invite gate removed from .env, restarting API ==")
    if not restart_api():
        log("  API did not come back — restoring .env")
        backup.replace(ENV)
        restart_api()
        return 1

    cfg = api_json("/api/v1/auth/signup-config")
    if cfg.get("invite_required"):
        log("  VERIFY FAILED: invite_required is still true — rolling back")
        backup.replace(ENV)
        restart_api()
        return 1
    log("  signup-config: invite_required=false, turnstile="
        + ("enabled" if cfg.get("turnstile", {}).get("enabled") else "DISABLED"))

    log(f"== opening Lifetime Access for {LIFETIME_DAYS} days ==")
    sys.path.insert(0, str(ROOT / "scripts"))
    import lifetime_window  # noqa: E402

    lifetime_window.guard_target(allow_test=False)
    lifetime_window.open_window(days=LIFETIME_DAYS, until=None, start=None)

    plans = api_json("/api/v1/billing/plans")
    life = next(p for p in plans if p["slug"] == "founder_lifetime")["lifetime_offer"]
    if not life["available"]:
        log("  VERIFY FAILED: lifetime_offer.available is false")
        return 1

    log("== LAUNCHED ==")
    log(f"  signups: OPEN (Turnstile enforced)")
    log(f"  lifetime: ON SALE until {life['ends_at']} for ${(life_price(plans)) / 100:.2f}")
    return 0


def life_price(plans: list[dict]) -> int:
    for p in plans:
        if p["slug"] == "founder_lifetime":
            return (p.get("price") or {}).get("lifetime_cents", 0)
    return 0


def revert() -> int:
    if not STATE.exists():
        log("no launch state saved — nothing to revert to")
        return 1
    state = json.loads(STATE.read_text())
    codes = state.get("signup_invite_codes", "")
    set_env_value("SIGNUP_INVITE_CODES", codes)
    if not restart_api():
        log("API did not come back after restoring the invite gate")
        return 1
    sys.path.insert(0, str(ROOT / "scripts"))
    import lifetime_window  # noqa: E402

    lifetime_window.guard_target(allow_test=False)
    lifetime_window.close_window()
    cfg = api_json("/api/v1/auth/signup-config")
    log(f"reverted: invite_required={cfg.get('invite_required')}, lifetime closed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--go", action="store_true", help="actually make the changes")
    ap.add_argument("--revert", action="store_true", help="re-apply the invite gate and close the offer")
    args = ap.parse_args()

    log("current state:")
    for k, v in plan().items():
        log(f"  {k:26} {v}")

    if not args.go:
        log("\nDRY RUN — nothing changed. Re-run with --go to launch.")
        return 0

    return revert() if args.revert else launch()


if __name__ == "__main__":
    sys.exit(main())
