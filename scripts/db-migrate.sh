#!/bin/bash
# Run database migrations
# Usage: ./scripts/db-migrate.sh [--docker] [--prod]
# --docker: runs inside api container
# --prod: use production compose (with --docker)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILES="-f docker-compose.yml"
[[ " $* " =~ " --prod " ]] && COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"

if [[ " $* " =~ " --docker " ]]; then
  echo "Running migrations via Docker..."
  [ -f .env ] && set -a && source .env && set +a
  docker compose $COMPOSE_FILES run --rm -e DATABASE_URL="${DATABASE_URL}" api alembic upgrade head
else
  echo "Running migrations locally..."
  [ -f .env ] && set -a && source .env && set +a
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  cd apps/api
  alembic upgrade head
  cd "$ROOT_DIR"
fi
echo "Migrations complete."
