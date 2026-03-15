#!/bin/bash
# Run database migrations
# Usage: ./scripts/db-migrate.sh [--docker]
# With --docker: runs inside api container

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if [ "$1" = "--docker" ]; then
  echo "Running migrations via Docker..."
  docker compose exec api alembic upgrade head
else
  echo "Running migrations locally..."
  [ -f .env ] && set -a && source .env && set +a
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  cd apps/api
  alembic upgrade head
  cd "$ROOT_DIR"
fi
echo "Migrations complete."
