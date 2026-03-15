#!/bin/bash
# Seed database with starter data (admin user, templates)
# Usage: ./scripts/db-seed.sh [--docker] [--prod]
# --docker: runs inside api container
# --prod: use production compose (with --docker)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

COMPOSE_FILES="-f docker-compose.yml"
[[ " $* " =~ " --prod " ]] && COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"

if [[ " $* " =~ " --docker " ]]; then
  echo "Seeding via Docker..."
  [ -f .env ] && set -a && source .env && set +a
  docker compose $COMPOSE_FILES run --rm -e DATABASE_URL="${DATABASE_URL}" -e REDIS_URL="${REDIS_URL}" -e SECRET_KEY="${SECRET_KEY}" api python -m authora.scripts.seed
else
  echo "Seeding locally..."
  [ -f .env ] && set -a && source .env && set +a
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  cd apps/api
  python -m authora.scripts.seed
  cd "$ROOT_DIR"
fi
echo "Seed complete."
