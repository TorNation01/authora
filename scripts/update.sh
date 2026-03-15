#!/bin/bash
# AUTHORA update script - pull, rebuild, migrate, restart
# Usage: ./scripts/update.sh [dev|prod]

set -e

MODE="${1:-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== AUTHORA Update ($MODE) ==="

# Pull latest (if git repo)
if [ -d .git ]; then
  git pull --rebase || true
fi

# Ensure infra is running
if [ "$MODE" = "prod" ]; then
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres redis 2>/dev/null || true
  sleep 3
else
  docker compose up -d postgres redis 2>/dev/null || true
  sleep 3
fi

if [ "$MODE" = "prod" ]; then
  [ -f .env ] && set -a && source .env && set +a
  docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
  docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm \
    -e DATABASE_URL="${DATABASE_URL}" api alembic upgrade head
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else
  docker compose build --no-cache
  docker compose run --rm -e DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}" api alembic upgrade head
  docker compose up -d
fi

echo "Update complete."
