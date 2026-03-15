#!/bin/bash
# Seed database with starter data (admin user, templates)
# Usage: ./scripts/db-seed.sh [--docker]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if [ "$1" = "--docker" ]; then
  echo "Seeding via Docker..."
  docker compose exec api python -m authora.scripts.seed
else
  echo "Seeding locally..."
  [ -f .env ] && set -a && source .env && set +a
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  cd apps/api
  python -m authora.scripts.seed
  cd "$ROOT_DIR"
fi
echo "Seed complete."
