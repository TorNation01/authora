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
  [ -f .env ] || { echo "ERROR: .env required for production. Copy .env.example and configure."; exit 1; }
  set -a && source .env && set +a
  ./scripts/validate-env.sh production || exit 1

  # Ensure Caddyfile exists
  if [ ! -f caddy/Caddyfile ]; then
    [ -f scripts/generate-caddyfile.sh ] && ./scripts/generate-caddyfile.sh || cp caddy/Caddyfile.example caddy/Caddyfile 2>/dev/null || true
  fi

  echo "Starting PostgreSQL and Redis..."
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres redis
  echo "Waiting for PostgreSQL..."
  until docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T postgres pg_isready -U authora 2>/dev/null; do sleep 2; done

  echo "Building and starting production stack..."
  docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
  docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm -e DATABASE_URL="${DATABASE_URL}" api alembic upgrade head
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

  echo ""
  echo "Production deploy complete. Verify: ./scripts/healthcheck.sh https://api.yourdomain.com"
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
