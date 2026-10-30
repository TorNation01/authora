#!/usr/bin/env python3
"""Authora Next RCE patch — 5xx check.

Health checks pinged /health and /health/ready and called it healthy while real
routes were returning 500/502/503 in the access log. Reachability is not health.

Two modes:

  probe (default)  Discover every GET route from /openapi.json, hit each one, and
                   fail if any answers 5xx. 4xx is fine — that is auth/shape, not a
                   broken handler. Add --token to exercise authenticated handlers
                   with a real Bearer token instead of only their auth guard.

  --journal        Scan the API unit's access log for 5xx that actually happened
                   between checks (POSTs, webhooks, cron — routes a probe cannot
                   safely exercise). Watermark means each 5xx is reported once.

Exit 0 = no 5xx. Exit 1 = 5xx or unreachable. Exit 2 = usage/config error.

Run:  python3 scripts/check/http_5xx_check.py --base-url http://127.0.0.1:8004
      python3 scripts/check/http_5xx_check.py --journal --since "-1h"
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

DEFAULT_BASE = "http://127.0.0.1:8004"
ALWAYS = ("/health", "/health/ready", "/openapi.json")
# GET routes that mutate or fan out: never probed from a monitor.
DENY = (
    "/cron/",
    "/notifications/test",
    "/logout",
    "/delete",
    "/purge",
    "/rotate",
    "/seed",
    "/resend",
    "/cancel",
)
STATE_DIR = "/var/lib/authora-http-check"
UA = "authora-5xx-check/1.0"
AWST = timezone(timedelta(hours=8))


def now_iso() -> str:
    return datetime.now(AWST).isoformat(timespec="seconds")


def http_code(url: str, token: str | None, timeout: float) -> tuple[int | None, str]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": UA})
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # connection refused, DNS, timeout, TLS
        return None, f"{type(e).__name__}: {e}"


def discover(base: str, timeout: float) -> list[str]:
    """Every GET route without a path placeholder, from the live OpenAPI schema."""
    req = urllib.request.Request(base + "/openapi.json", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        spec = json.load(r)
    out = []
    for path, ops in (spec.get("paths") or {}).items():
        if "get" not in ops or "{" in path:
            continue
        if any(d in path for d in DENY):
            continue
        out.append(path)
    return sorted(out)


def probe(base: str, paths: list[str], token: str | None, timeout: float, workers: int) -> dict:
    base = base.rstrip("/")

    def one(p: str) -> tuple[str, int | None, str]:
        code, err = http_code(base + p, token, timeout)
        return p, code, err

    results, failures, unreachable = [], [], []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for path, code, err in pool.map(one, paths):
            results.append({"path": path, "status": code, "error": err})
            if code is None:
                unreachable.append({"path": path, "error": err})
            elif code >= 500:
                failures.append({"path": path, "status": code})

    hist: dict[str, int] = {}
    for r in results:
        k = "unreachable" if r["status"] is None else str(r["status"])
        hist[k] = hist.get(k, 0) + 1
    return {
        "mode": "probe",
        "base_url": base,
        "authenticated": bool(token),
        "probed": len(results),
        "seconds": round(time.time() - t0, 2),
        "histogram": dict(sorted(hist.items(), key=lambda kv: (kv[0] != "200", kv[0]))),
        "failures": failures,
        "unreachable": unreachable,
        "ok": not failures and not unreachable,
    }


ACCESS_RE = re.compile(r'"(?P<method>[A-Z]+)\s+(?P<path>\S+)\s+HTTP/[\d.]+"\s+(?P<status>\d{3})')


def parse_5xx(raw: str) -> dict[tuple[str, str, int], int]:
    """Group access-log lines into (method, path, status) -> count, 5xx only."""
    hits: dict[tuple[str, str, int], int] = {}
    for line in raw.splitlines():
        m = ACCESS_RE.search(line)
        if not m:
            continue
        status = int(m.group("status"))
        if status >= 500:
            key = (m.group("method"), m.group("path"), status)
            hits[key] = hits.get(key, 0) + 1
    return hits



def journal(since: str, state_file: str, unit: str, suppress_hours: float) -> dict:
    """Scan the access log since the watermark.

    The watermark always advances, so each window is disjoint and an old 5xx is
    not re-discovered forever. Repeats of the same method+path+status inside
    `suppress_hours` are still counted but do not fail the check — a monitor that
    shouts every 30 minutes about one broken webhook gets muted, and a muted
    monitor is the bug we are fixing.
    """
    cmd = ["journalctl", "-u", unit, "--since", since, "--no-pager", "-o", "cat"]
    raw = subprocess.run(cmd, capture_output=True, text=True).stdout
    hits = parse_5xx(raw)

    try:
        state = json.load(open(state_file))
    except Exception:
        state = {}
    alerted: dict[str, str] = state.get("alerted") or {}
    now = datetime.now(AWST)

    entries, cutoff = [], now - timedelta(hours=suppress_hours)
    for (method, path, status), count in sorted(hits.items(), key=lambda kv: -kv[1]):
        fp = f"{status} {method} {path}"
        try:
            seen = datetime.fromisoformat(alerted[fp])
        except Exception:
            seen = None
        repeat = bool(seen and seen > cutoff)
        entries.append(
            {"method": method, "path": path, "status": status, "count": count,
             "repeat": repeat, "last_alerted": alerted.get(fp)}
        )
        if not repeat:
            alerted[fp] = now.isoformat(timespec="seconds")

    # Prune alert memory so the state file cannot grow without bound.
    alerted = {
        k: v for k, v in alerted.items()
        if (datetime.fromisoformat(v) if _iso(v) else now) > now - timedelta(days=7)
    }
    new_total = sum(e["count"] for e in entries if not e["repeat"])
    total = sum(e["count"] for e in entries)
    try:
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        with open(state_file, "w") as fh:
            json.dump({"last_scan": now.isoformat(timespec="seconds"), "since": since,
                       "alerted": alerted}, fh, indent=1)
    except OSError:
        pass
    return {
        "mode": "journal",
        "unit": unit,
        "since": since,
        "lines_scanned": len(raw.splitlines()),
        "total_5xx": total,
        "new_5xx": new_total,
        "suppress_hours": suppress_hours,
        "entries": entries,
        "ok": new_total == 0,
    }


def _iso(v: str) -> bool:
    try:
        datetime.fromisoformat(v)
        return True
    except Exception:
        return False



def render(rep: dict) -> str:
    out = []
    if rep["mode"] == "probe":
        out.append(
            f"5xx check {rep['base_url']}  probed={rep['probed']}  "
            f"auth={'yes' if rep['authenticated'] else 'no'}  {rep['seconds']}s"
        )
        out.append("  statuses: " + "  ".join(f"{k}x{v}" for k, v in rep["histogram"].items()))
        for f in rep["failures"]:
            out.append(f"  ! {f['status']} {f['path']}")
        for f in rep["unreachable"]:
            out.append(f"  ! UNREACHABLE {f['path']} ({f['error']})")
    else:
        out.append(
            f"5xx journal {rep['unit']} since {rep['since']}  scanned={rep['lines_scanned']} lines"
        )
        for e in rep["entries"]:
            tag = " (repeat, already alerted)" if e["repeat"] else ""
            out.append(f"  ! {e['status']} {e['method']} {e['path']}  x{e['count']}{tag}")
    out.append("PASS — no 5xx" if rep["ok"] else f"FAIL — {_count(rep)} 5xx/unreachable")
    return "\n".join(out)


def _count(rep: dict) -> int:
    if rep["mode"] == "probe":
        return len(rep["failures"]) + len(rep["unreachable"])
    return rep.get("new_5xx", rep["total_5xx"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fail on 5xx, not just unreachability.")
    ap.add_argument("--base-url", default=os.environ.get("AUTHORA_BASE_URL", DEFAULT_BASE))
    ap.add_argument("--token", default=os.environ.get("AUTHORA_CHECK_TOKEN"))
    ap.add_argument("--path", action="append", default=[], help="extra/only path to probe")
    ap.add_argument("--no-discovery", action="store_true", help="probe only --path + health")
    ap.add_argument("--max-paths", type=int, default=0)
    ap.add_argument("--timeout", type=float, default=8.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--journal", action="store_true", help="scan access log instead of probing")
    ap.add_argument("--since", default=None, help="journal window, e.g. '-1h' (default: watermark)")
    ap.add_argument("--suppress-repeat-hours", type=float, default=0.0,
                    help="journal: do not re-fail on the same route+status seen within N hours")
    ap.add_argument("--unit", default="authora-v2-api")
    ap.add_argument("--state-file", default=os.path.join(STATE_DIR, "journal.json"))
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    if a.journal:
        since = a.since
        if not since:
            since = "-24h"
            try:
                since = json.load(open(a.state_file))["last_scan"]
            except Exception:
                pass
        rep = journal(since, a.state_file, a.unit, a.suppress_repeat_hours)
    else:
        paths = list(dict.fromkeys([*ALWAYS, *a.path]))
        discovery_error = ""
        if not a.no_discovery:
            try:
                found = discover(a.base_url, a.timeout)
                paths += [p for p in found if p not in paths]
            except Exception as e:
                # Cannot enumerate does not excuse silence: probe what we know,
                # and fail — an API whose schema we cannot read is not healthy.
                discovery_error = f"{type(e).__name__}: {e}"
        if a.max_paths:
            paths = paths[: a.max_paths]
        rep = probe(a.base_url, paths, a.token, a.timeout, a.workers)
        if discovery_error:
            rep["discovery_error"] = discovery_error
            rep["unreachable"].append({"path": "/openapi.json", "error": discovery_error})
            rep["ok"] = False

    if a.json:
        print(json.dumps(rep, indent=1))
    elif not a.quiet:
        print(render(rep))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
