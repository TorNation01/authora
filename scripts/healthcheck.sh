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
