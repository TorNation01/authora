#!/usr/bin/env bash
# Deploy the Authora web app on this host (systemd, not Docker).
#
# scripts/deploy.sh is the upstream Docker/Caddy installer for a fresh clone.
# This host runs systemd units (authora-v2-web / authora-v2-api), so production
# deploys go through here.
#
# The advisory gate runs BEFORE the build: a build that would put a known RCE
# back on the live host never reaches the restart.
#
# Usage:  scripts/deploy-web.sh [--skip-build]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say() { printf '\n== %s ==\n' "$*"; }

say "gate: next version + advisories"
python3 scripts/check/next_advisory_check.py

if [[ "${1:-}" != "--skip-build" ]]; then
  say "build"
  npm run build --workspace=apps/web
fi

say "restart"
systemctl restart authora-v2-web
sleep 8

if ! systemctl is-active --quiet authora-v2-web; then
  echo "FAIL: authora-v2-web did not stay up" >&2
  journalctl -u authora-v2-web -n 30 --no-pager >&2
  exit 1
fi

say "smoke"
fail=0
for url in https://authora.studio/ https://authora.studio/login https://v2.authora.studio/ https://api.authora.studio/health; do
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$url" || echo 000)"
  printf '%-38s %s\n' "$url" "$code"
  [[ "$code" == "200" ]] || fail=1
done

if [[ "$fail" -ne 0 ]]; then
  echo "FAIL: smoke test saw a non-200" >&2
  exit 1
fi

say "live build $(cat apps/web/.next/BUILD_ID 2>/dev/null || echo unknown)"
