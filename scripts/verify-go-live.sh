#!/bin/bash
# AUTHORA Go-Live Verification
# Usage: ./scripts/verify-go-live.sh [base_url]
# Runs comprehensive checks before/after go-live.
# base_url: http://localhost:8000 or https://api.yourdomain.com

set -e

BASE_URL="${1:-http://localhost:8000}"
WEB_URL="${2:-}"
FAIL=0

echo "=== AUTHORA Go-Live Verification ==="
echo "API: $BASE_URL"
echo ""

# 1. API health
echo "1. API health"
if curl -sf --connect-timeout 10 "$BASE_URL/health" | grep -q "ok"; then
  echo "   PASS"
else
  echo "   FAIL"
  FAIL=1
fi

# 2. Readiness (DB + Redis)
echo "2. Read readiness"
READY=$(curl -sf --connect-timeout 10 "$BASE_URL/health/ready" 2>/dev/null || echo "{}")
if echo "$READY" | grep -q "ready"; then
  echo "   PASS"
else
  echo "   FAIL (response: $READY)"
  FAIL=1
fi

# 3. API docs reachable
echo "3. API docs"
if curl -sf --connect-timeout 5 "$BASE_URL/api/docs" -o /dev/null 2>&1; then
  echo "   PASS"
else
  echo "   WARN (docs may be disabled)"
fi

# 4. CORS / OPTIONS (if web URL provided)
if [ -n "$WEB_URL" ]; then
  echo "4. CORS"
  if curl -sf -X OPTIONS "$BASE_URL/api/v1/health" -H "Origin: $WEB_URL" -H "Access-Control-Request-Method: GET" -I 2>/dev/null | grep -q "Access-Control"; then
    echo "   PASS"
  else
    echo "   WARN (check CORS_ORIGINS)"
  fi
else
  echo "4. CORS (skip - no web URL)"
fi

# 5. SECRET_KEY not default
echo "5. SECRET_KEY"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -f "$ROOT_DIR/.env" ]; then
  set -a && source "$ROOT_DIR/.env" 2>/dev/null && set +a || true
  if [ "$SECRET_KEY" = "change-me-in-production-use-openssl-rand-hex-32" ] || [ "$SECRET_KEY" = "dev-secret-change-in-production" ]; then
    echo "   FAIL - SECRET_KEY must be changed in production"
    FAIL=1
  else
    echo "   PASS"
  fi
else
  echo "   SKIP (no .env)"
fi

echo ""
if [ $FAIL -eq 1 ]; then
  echo "Verification FAILED. Fix issues before go-live."
  exit 1
fi

echo "All go-live checks passed."
exit 0
