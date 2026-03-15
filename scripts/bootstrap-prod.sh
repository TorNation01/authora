#!/bin/bash
# AUTHORA production bootstrap
# Usage: ./scripts/bootstrap-prod.sh
# Run on a fresh server before first deploy. Requires Docker.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== AUTHORA Production Bootstrap ==="

# Require Docker
if ! command -v docker &> /dev/null; then
  echo "ERROR: Docker required for production. Install Docker and Docker Compose."
  exit 1
fi
echo "Docker: $(docker --version)"

# Require .env
if [ ! -f .env ]; then
  echo "ERROR: .env required. Copy .env.example and configure."
  echo "  cp .env.example .env"
  echo "  # Edit .env with SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL"
  exit 1
fi

# Load and validate
set -a
source .env
set +a
./scripts/validate-env.sh production || exit 1

# Create directories
mkdir -p backups storage caddy/data caddy/config

# Create Caddyfile from template if missing
if [ ! -f caddy/Caddyfile ]; then
  if [ -f caddy/Caddyfile.example ]; then
    cp caddy/Caddyfile.example caddy/Caddyfile
    echo "Created caddy/Caddyfile from example. Edit with your domains before deploy."
  else
    echo "ERROR: caddy/Caddyfile required. Create from caddy/Caddyfile.example"
    exit 1
  fi
fi

# Pull images and build
echo ""
echo "Building images..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start infra first (postgres, redis)
echo ""
echo "Starting database and Redis..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres redis

echo "Waiting for PostgreSQL..."
until docker compose exec -T postgres pg_isready -U authora 2>/dev/null; do
  sleep 2
done

# Run migrations (api container has /app as workdir with alembic)
echo ""
echo "Running migrations..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm \
  -e DATABASE_URL="${DATABASE_URL}" api \
  alembic upgrade head || echo "WARN: Migrations failed. Run manually: docker compose run --rm api alembic upgrade head"

# Start full stack
echo ""
echo "Starting full stack..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

echo ""
echo "=== Production bootstrap complete ==="
echo ""
echo "Next steps:"
echo "  1. Visit https://your-domain to complete setup wizard"
echo "  2. Create first admin account"
echo "  3. Configure backup cron: 0 2 * * * ./scripts/backup.sh"
echo ""
