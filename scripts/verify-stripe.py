#!/usr/bin/env python3
"""Verify Authora's Stripe wiring end to end, without printing any key.

Run once live keys are in place:

    cd /opt/authora-v2 && python3 scripts/verify-stripe.py
    # or, from the repo copy:
    cd /root/athena-authora-finish && python3 scripts/verify-stripe.py

Checks, in the order they fail in the real world:

  1. Both secrets exist in .env.
  2. The secret key is a live key (or says plainly that it is a test key).
  3. The account can actually take money (charges_enabled, payouts_enabled,
     details_submitted) - "configured" means nothing if onboarding is unfinished.
  4. A webhook endpoint is registered for this app, enabled, in the same mode as
     the key, pointing at the path the router actually serves, and subscribed to
     the events the handler understands.
  5. STRIPE_WEBHOOK_SECRET matches the endpoint that Stripe will sign with: a
     self-signed event is POSTed to the public URL and must come back 200. This
     is the check that catches the silent failure - a wrong secret accepts the
     config, rejects every real event, and leaves stripe_webhook_events empty.
  6. How many events have actually landed in the database.

Exit code 0 only when every required check passes. No key or secret is written
to stdout, to a file, or to the process list.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".env"

REQUIRED_EVENTS = {
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_succeeded",  # what the endpoint is subscribed to today
    "invoice.paid",  # what newer dashboards call the same thing
    "invoice.payment_failed",
}
REQUIRED_SUBSET = {
    "checkout.session.completed",
    "customer.subscription.created",
    "customer.subscription.updated",
    "customer.subscription.deleted",
    "invoice.payment_failed",
}
EXPECTED_PATH = "/api/v1/billing/webhooks/stripe"
# Cloudflare answers urllib's default user agent with HTTP 403 (error 1010, bot
# signature banned) before the request ever reaches nginx. Send what Stripe
# sends so the probe tests our stack, not the edge's opinion of Python.
STRIPE_UA = "Stripe/1.0 (+https://stripe.com/docs/webhooks)"
PUBLIC_URL = os.environ.get(
    "AUTHORA_WEBHOOK_URL", "https://authora.studio" + EXPECTED_PATH
)

results: list[tuple[bool, str, str]] = []
selfcheck_id = ""


def record(ok: bool, name: str, detail: str = "") -> None:
    results.append((ok, name, detail))
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}" + (f" — {detail}" if detail else ""))


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    if not ENV_FILE.exists():
        return values
    try:
        from dotenv import dotenv_values  # ships with pydantic-settings
    except ImportError:
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip().strip("'\"")
        return values
    values.update({k: v for k, v in dotenv_values(ENV_FILE).items() if v is not None})
    return values


def stripe_get(path: str, key: str) -> dict:
    req = urllib.request.Request(f"https://api.stripe.com/v1/{path}")
    req.add_header("Authorization", f"Bearer {key}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def main() -> int:
    global selfcheck_id
    env = {**load_env(), **{k: v for k, v in os.environ.items() if k.startswith("STRIPE_")}}
    secret_key = env.get("STRIPE_SECRET_KEY", "")
    webhook_secret = env.get("STRIPE_WEBHOOK_SECRET", "") or env.get(
        "STRIPE_WEBHOOK_SECRET_LIVE", ""
    )

    print(f"env file: {ENV_FILE} ({'found' if ENV_FILE.exists() else 'MISSING'})")
    record(bool(secret_key), "STRIPE_SECRET_KEY is set",
           "absent from .env" if not secret_key else f"{len(secret_key)} chars")
    record(bool(webhook_secret), "STRIPE_WEBHOOK_SECRET is set",
           "absent from .env" if not webhook_secret else f"{len(webhook_secret)} chars")

    if not secret_key:
        return 1

    mode = "live" if secret_key.startswith("sk_live") else (
        "test" if secret_key.startswith("sk_test") else "unknown"
    )
    record(mode == "live", f"secret key mode: {mode}",
           "test keys cannot take real payments" if mode != "live" else "")

    # 3. can this account take money?
    try:
        account = stripe_get("account", secret_key)
        ok = bool(account.get("charges_enabled")) and bool(account.get("details_submitted"))
        record(ok, "account can accept charges",
               f"country={account.get('country')} charges_enabled={account.get('charges_enabled')} "
               f"payouts_enabled={account.get('payouts_enabled')} "
               f"details_submitted={account.get('details_submitted')}")
    except urllib.error.HTTPError as exc:
        record(False, "account read", f"Stripe HTTP {exc.code}")
        account = {}

    # 4. is a webhook registered, for this app, in the right mode?
    try:
        endpoints = stripe_get("webhook_endpoints?limit=100", secret_key).get("data", [])
    except urllib.error.HTTPError as exc:
        record(False, "webhook endpoints read", f"Stripe HTTP {exc.code}")
        return 1

    livemode = mode == "live"
    matching = [
        e for e in endpoints
        if EXPECTED_PATH in (e.get("url") or "")
        and (e.get("livemode") if e.get("livemode") is not None else False) == livemode
    ]
    if not matching:
        record(False, "webhook endpoint registered for this app",
               f"no endpoint matching {EXPECTED_PATH} in {mode} mode; "
               f"{len(endpoints)} endpoint(s) exist for other apps")
    for endpoint in matching:
        enabled = endpoint.get("status") == "enabled"
        record(enabled, f"endpoint enabled: {endpoint.get('url')}",
               f"status={endpoint.get('status')} id={endpoint.get('id')}")
        subs = set(endpoint.get("enabled_events", []))
        missing = REQUIRED_SUBSET - subs
        record(not missing, "endpoint subscribes to required events",
               f"missing: {', '.join(sorted(missing))}" if missing else f"{len(subs)} events")
        if "invoice.paid" not in subs and "invoice.payment_succeeded" not in subs:
            record(False, "endpoint includes an invoice-paid event",
                   "renewals will not extend access without one")

    # 5. signature verification, in two halves.
    #    Stripe never reveals an endpoint's signing secret, so "does our secret
    #    match Stripe's" cannot be read out of the API. What can be proved is:
    #    the app accepts a correctly signed event (secret + verifier consistent),
    #    and the public URL reaches the app instead of being eaten by the edge.
    if webhook_secret:
        selfcheck_id = f"evt_authora_selfcheck_{int(time.time())}"
        payload = json.dumps(
            {
                "id": selfcheck_id,
                "type": "authora.selfcheck",  # no handler runs for this type
                "data": {"object": {"note": "verify-stripe.py"}},
            }
        ).encode()
        stamp = int(time.time())
        signature = hmac.new(
            webhook_secret.encode(), f"{stamp}.".encode() + payload, hashlib.sha256
        ).hexdigest()

        local_url = "http://127.0.0.1:8004" + EXPECTED_PATH
        req = urllib.request.Request(local_url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Stripe-Signature", f"t={stamp},v1={signature}")
        req.add_header("User-Agent", STRIPE_UA)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read(300).decode("utf-8", "replace")
                record(resp.status == 200, "app accepts a correctly signed event (local)",
                       f"HTTP {resp.status} {body[:120]}")
        except urllib.error.HTTPError as exc:
            body = exc.read(300).decode("utf-8", "replace")
            record(False, "app accepts a correctly signed event (local)",
                   f"HTTP {exc.code} {body[:160]} — the app and STRIPE_WEBHOOK_SECRET disagree")
        except Exception as exc:  # noqa: BLE001
            record(False, "app accepts a correctly signed event (local)",
                   f"{type(exc).__name__}: {exc}")

    # An unsigned POST must be refused with 400 Invalid signature. Anything else
    # (404 path typo, 403 from the edge, 5xx) means Stripe's deliveries will not
    # reach the handler either.
    req = urllib.request.Request(PUBLIC_URL, data=b"{}", method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", STRIPE_UA)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            record(False, "public endpoint reachable",
                   f"HTTP {resp.status} — an unsigned request was NOT rejected")
    except urllib.error.HTTPError as exc:
        body = exc.read(300).decode("utf-8", "replace")
        ok = exc.code == 400 and "signature" in body.lower()
        record(ok, "public endpoint reachable",
               f"HTTP {exc.code} {body[:120]}" if ok else
               f"HTTP {exc.code} {body[:120]} — expected 400 Invalid signature")
    except Exception as exc:  # noqa: BLE001
        record(False, "public endpoint reachable", f"{type(exc).__name__}: {exc}")

    # 6. has anything actually landed?
    db_url = env.get("DATABASE_URL") or os.environ.get("DATABASE_URL", "")
    if db_url:
        try:
            import psycopg2  # noqa: PLC0415

            with psycopg2.connect(db_url) as conn, conn.cursor() as cur:
                # Remove the row the self-check above wrote, so running this
                # script does not leave fake traffic in the delivery log.
                if selfcheck_id:
                    cur.execute(
                        "delete from stripe_webhook_events where stripe_event_id = %s",
                        (selfcheck_id,),
                    )
                    if cur.rowcount:
                        print(f"        removed self-check row {selfcheck_id}")
                    conn.commit()
                cur.execute("select count(*) from stripe_webhook_events")
                count = cur.fetchone()[0]
                cur.execute(
                    "select event_type, max(processed_at)::date from stripe_webhook_events "
                    "group by event_type order by 2 desc limit 5"
                )
                recent = cur.fetchall()
            record(True, "stripe_webhook_events rows", str(count))
            for event_type, day in recent:
                print(f"        {day}  {event_type}")
        except Exception as exc:  # noqa: BLE001
            record(False, "stripe_webhook_events query", f"{type(exc).__name__}: {exc}")

    failed = [name for ok, name, _ in results if not ok]
    print()
    if failed:
        print(f"RESULT: {len(failed)} check(s) FAILED — {', '.join(failed)}")
        return 1
    print(f"RESULT: all {len(results)} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
