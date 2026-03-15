#!/bin/bash
# AUTHORA one-command deployment script
# Usage: ./scripts/deploy.sh [dev|prod]
# Dev: starts infra + runs migrations, ready for npm run dev
# Prod: full stack with docker compose (requires .env)

set -e

MODE="${1:-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== AUTHORA Deployment ($MODE) ==="

if ! command -v docker &> /dev/null; then
  echo "Docker is required. Install Docker and try again."
  exit 1
fi

# Load env for validation
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

if [ "$MODE" = "prod" ]; then
  ./scripts/validate-env.sh production || exit 1
  echo "Starting production stack..."
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
else
  echo "Starting PostgreSQL and Redis..."
  docker compose up -d postgres redis

  echo "Waiting for PostgreSQL..."
  until docker compose exec -T postgres pg_isready -U authora 2>/dev/null; do
    sleep 2
  done

  echo "Running database migrations..."
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  cd apps/api
  pip install -e . -q 2>/dev/null || true
  alembic upgrade head
  cd "$ROOT_DIR"

  echo ""
  echo "=== Ready ==="
  echo "Start the app with:"
  echo "  npm run dev:api   # Backend on http://localhost:8000"
  echo "  npm run dev      # Frontend on http://localhost:3000"
  echo ""
  echo "Or run full stack with Docker:"
  echo "  docker compose up -d"
fi

echo ""
echo "Deployment complete."
