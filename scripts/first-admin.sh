#!/bin/bash
# AUTHORA First Admin Creation
# Usage: ./scripts/first-admin.sh [--docker] [--prod]
# Creates admin@authora.local / admin123 if no users exist.
# Change password immediately after first login.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

[ -f .env ] && set -a && source .env && set +a

COMPOSE_FILES="-f docker-compose.yml"
[[ " $* " =~ " --prod " ]] && COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"

echo "=== AUTHORA First Admin ==="

if [[ " $* " =~ " --docker " ]]; then
  echo "Seeding via Docker..."
  docker compose $COMPOSE_FILES run --rm \
    -e DATABASE_URL="${DATABASE_URL}" \
    -e REDIS_URL="${REDIS_URL:-redis://redis:6379/0}" \
    -e SECRET_KEY="${SECRET_KEY}" \
    api python -m authora.scripts.seed
else
  echo "Seeding locally..."
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  cd apps/api
  python -m authora.scripts.seed
  cd "$ROOT_DIR"
fi

echo ""
echo "Default admin: admin@authora.local / admin123"
echo "Change password immediately after first login."
echo ""
