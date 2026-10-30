#!/usr/bin/env python3
"""Authora Next RCE patch — acceptance check.

Fails while the installed Next line still carries an RCE or high advisory.
Passes only when:
  1. the installed next version is at or above the patched backport (15.5.28), and
  2. `npm audit` reports no critical/high advisory against next itself.

Run:  python3 scripts/check/next_advisory_check.py      (exit 0 = pass)
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MIN = (15, 5, 28)


def installed_next() -> str:
    p = ROOT / "node_modules/next/package.json"
    if not p.exists():
        p = ROOT / "apps/web/node_modules/next/package.json"
    return json.loads(p.read_text())["version"]


def vt(v: str) -> tuple:
    core = v.split("-")[0]
    parts = [int(x) for x in core.split(".")[:3]]
    return tuple(parts + [0] * (3 - len(parts)))


def audit_next() -> dict:
    out = subprocess.run(
        ["npm", "audit", "--json"], cwd=ROOT, capture_output=True, text=True, timeout=300
    ).stdout
    try:
        data = json.loads(out or "{}")
    except json.JSONDecodeError:
        return {"error": "npm audit did not return JSON (registry unreachable?)"}
    n = (data.get("vulnerabilities") or {}).get("next") or {}
    bad = []
    for via in n.get("via") or []:
        if isinstance(via, dict) and via.get("severity") in ("critical", "high"):
            bad.append({"severity": via["severity"], "title": via.get("title"), "url": via.get("url")})
    return {"count": len(bad), "advisories": bad}


def main() -> int:
    ver = installed_next()
    problems = []
    if vt(ver) < MIN:
        problems.append(f"next {ver} is below the patched backport {'.'.join(map(str, MIN))}")
    a = audit_next()
    if a.get("error"):
        problems.append(a["error"])
    elif a["count"]:
        problems.append(f"{a['count']} critical/high advisory(ies) still reported against next")

    print(f"next installed: {ver}")
    print(f"required      : >= {'.'.join(map(str, MIN))}")
    if a.get("advisories"):
        for x in a["advisories"]:
            print(f"  - [{x['severity']}] {x['title']}  {x['url']}")

    if problems:
        print("\nFAIL")
        for p in problems:
            print(f"  ! {p}")
        return 1
    print("\nPASS — next is on a patched line with no critical/high advisories")
    return 0


if __name__ == "__main__":
    sys.exit(main())
