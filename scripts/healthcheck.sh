#!/bin/bash
# AUTHORA Health Check
# Usage: ./scripts/healthcheck.sh [base_url]
# base_url: http://localhost:8000 (default) or https://api.authora.studio (prod)
# Exit 0 if healthy, 1 otherwise.

set -e

BASE_URL="${1:-http://localhost:8000}"
FAIL=0

echo "=== AUTHORA Health Check ($BASE_URL) ==="

# Liveness
if curl -sf --connect-timeout 5 "$BASE_URL/health" > /dev/null; then
  echo "  /health: OK"
else
  echo "  /health: FAIL"
  FAIL=1
fi

# Readiness (DB + Redis)
if curl -sf --connect-timeout 5 "$BASE_URL/health/ready" > /dev/null; then
  echo "  /health/ready: OK"
else
  echo "  /health/ready: FAIL"
  FAIL=1
fi

# Real routes. Liveness says the process is up; it says nothing about whether a
# handler works. A route can 500 all day while /health answers 200 — that is how
# billing webhooks, checkout and publish failed silently. Every GET route from
# the OpenAPI schema is probed and any 5xx fails this check.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHECK="$SCRIPT_DIR/check/http_5xx_check.py"
if command -v python3 > /dev/null 2>&1 && [ -f "$CHECK" ]; then
  rc=0
  out=$(python3 "$CHECK" --base-url "$BASE_URL" ${AUTHORA_CHECK_TOKEN:+--token "$AUTHORA_CHECK_TOKEN"} 2>&1) || rc=$?
  if [ $rc -eq 0 ]; then
    echo "  5xx sweep: OK"
    echo "$out" | sed -n 's/^  statuses: /    /p'
  else
    echo "  5xx sweep: FAIL"
    echo "$out" | sed 's/^/    /'
    FAIL=1
  fi
  # 5xx that already happened (POSTs, webhooks, cron): opt-in, watermark-backed.
  if [ "${AUTHORA_CHECK_JOURNAL:-0}" = "1" ]; then
    rc=0
    jout=$(python3 "$CHECK" --journal --since "${AUTHORA_CHECK_JOURNAL_SINCE:--1h}" 2>&1) || rc=$?
    if [ $rc -eq 0 ]; then
      echo "  journal 5xx: none"
    else
      echo "  journal 5xx: FAIL"
      echo "$jout" | sed 's/^/    /'
      FAIL=1
    fi
  fi
else
  echo "  5xx sweep: SKIP (checker missing)"
fi

# Root (optional)
if curl -sf --connect-timeout 3 "$BASE_URL/" | grep -q "app"; then
  echo "  /: OK"
else
  echo "  /: (skip)"
fi

if [ $FAIL -eq 1 ]; then
  echo ""
  echo "Health check FAILED. Check API logs and database/Redis connectivity."
  exit 1
fi

echo ""
echo "All health checks passed."
exit 0
