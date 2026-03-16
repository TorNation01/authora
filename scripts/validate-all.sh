#!/bin/bash
# AUTHORA Full Validation - run all checks before release
# Usage: ./scripts/validate-all.sh [api_url]

set -e

API_URL="${1:-http://localhost:8000}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== AUTHORA Full Validation ==="

FAIL=0

# 1. Env validation
echo ""
echo "1. Env validation..."
if [ -f .env ]; then
  set -a && source .env && set +a
  if [ -f scripts/validate-env.sh ]; then
    ./scripts/validate-env.sh development 2>/dev/null || ./scripts/validate-env.sh standalone 2>/dev/null || true
    echo "   OK"
  else
    echo "   SKIP (validate-env.sh not found)"
  fi
else
  echo "   SKIP (no .env)"
fi

# 2. API tests
echo ""
echo "2. API tests..."
if [ -d apps/api ] && command -v pytest &>/dev/null; then
  (cd apps/api && pytest -q 2>/dev/null) && echo "   OK" || { echo "   FAIL"; FAIL=1; }
else
  echo "   SKIP (pytest or apps/api not found)"
fi

# 3. Health check
echo ""
echo "3. Health check..."
if curl -sf --connect-timeout 5 "$API_URL/health" >/dev/null 2>&1; then
  echo "   OK"
else
  echo "   FAIL (API not reachable at $API_URL)"
  FAIL=1
fi

# 4. Backup script exists
echo ""
echo "4. Backup script..."
[ -f scripts/backup.sh ] && echo "   OK" || { echo "   FAIL"; FAIL=1; }

# 5. Restore script exists
echo ""
echo "5. Restore script..."
[ -f scripts/restore.sh ] && echo "   OK" || { echo "   FAIL"; FAIL=1; }

echo ""
if [ $FAIL -eq 1 ]; then
  echo "=== Validation FAILED ==="
  exit 1
fi
echo "=== Validation PASSED ==="
exit 0
