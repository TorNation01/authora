#!/bin/bash
# AUTHORA local development bootstrap
# Usage: ./scripts/bootstrap-dev.sh
# Prerequisites: Node 18+, Python 3.11+, Docker (optional for postgres/redis)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "=== AUTHORA Development Bootstrap ==="

# Check Node
if ! command -v node &> /dev/null; then
  echo "ERROR: Node.js 18+ required. Install from https://nodejs.org"
  exit 1
fi
echo "Node: $(node -v)"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
  echo "ERROR: Python 3.11+ required"
  exit 1
fi
PYTHON_CMD=$(command -v python3 || command -v python)
echo "Python: $($PYTHON_CMD --version)"

# Create .env if missing
if [ ! -f .env ]; then
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo "Edit .env with your configuration."
  echo ""
fi

# Install dependencies
echo ""
echo "Installing Node dependencies..."
npm install

echo ""
echo "Installing API dependencies..."
pip install -e apps/api 2>/dev/null || pip install -e ./apps/api

# Start infra if Docker available
if command -v docker &> /dev/null; then
  echo ""
  echo "Starting PostgreSQL and Redis via Docker..."
  docker compose up -d postgres redis 2>/dev/null || true
  
  if docker compose ps postgres 2>/dev/null | grep -q "Up"; then
    echo "Waiting for PostgreSQL..."
    until docker compose exec -T postgres pg_isready -U authora 2>/dev/null; do
      sleep 2
    done
  fi
fi

# Run migrations
echo ""
echo "Running database migrations..."
export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
cd apps/api
alembic upgrade head 2>/dev/null || echo "WARN: Migrations failed. Ensure PostgreSQL is running."
cd "$ROOT_DIR"

echo ""
echo "=== Bootstrap complete ==="
echo ""
echo "Start the app:"
echo "  npm run dev:api   # Backend on http://localhost:8000"
echo "  npm run dev       # Frontend on http://localhost:3000"
echo ""
echo "Or run full stack with Docker:"
echo "  docker compose up -d"
echo ""
