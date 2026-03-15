#!/bin/bash
# AUTHORA Repo Install Flow
# Usage: ./scripts/install.sh [repo_url]
# Run from an empty directory or pass repo URL. Creates .env, validates, optionally runs setup wizard.
# Idempotent: safe to re-run.

set -e

REPO_URL="${1:-https://github.com/TorNation01/authora.git}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# If we're in scripts/, we're already in a clone
if [ -f "$ROOT_DIR/package.json" ] && [ -f "$ROOT_DIR/docker-compose.yml" ]; then
  echo "=== AUTHORA Install (existing clone) ==="
  cd "$ROOT_DIR"
else
  echo "=== AUTHORA Install (clone) ==="
  PARENT="$(cd "$SCRIPT_DIR/../.." && pwd)"
  if [ ! -d "$PARENT/authora" ] || [ ! -f "$PARENT/authora/package.json" ]; then
    echo "Cloning from $REPO_URL..."
    git clone "$REPO_URL" "$PARENT/authora" 2>/dev/null || {
      echo "Clone failed. Ensure git is installed and URL is correct."
      exit 1
    }
  fi
  cd "$PARENT/authora"
  ROOT_DIR="$(pwd)"
fi

echo "Root: $ROOT_DIR"

# Create .env from example if missing
if [ ! -f .env ]; then
  echo ""
  echo "Creating .env from .env.example..."
  cp .env.example .env
  echo "Edit .env with your configuration before deploy."
  echo ""
else
  echo ".env exists"
fi

# Remind to change SECRET_KEY if default
if grep -q "change-me-in-production\|dev-secret" .env 2>/dev/null; then
  echo "WARN: SECRET_KEY is default. For production, run: openssl rand -hex 32"
  echo "      Then set SECRET_KEY=... in .env"
fi

# Install Node deps
echo ""
echo "Installing Node dependencies..."
npm install

# Install Python API (for local dev / migrations)
echo ""
echo "Installing API dependencies..."
pip install -e apps/api 2>/dev/null || pip install -e ./apps/api || {
  echo "WARN: pip install failed. Use Docker for API."
}

# Create directories
mkdir -p backups storage caddy

# Create Caddyfile placeholder if missing
if [ ! -f caddy/Caddyfile ] && [ -f scripts/generate-caddyfile.sh ]; then
  ./scripts/generate-caddyfile.sh 2>/dev/null || cp caddy/Caddyfile.example caddy/Caddyfile 2>/dev/null || true
fi

echo ""
echo "=== Install complete ==="
echo ""
echo "Next steps:"
echo "  1. Edit .env: DATABASE_URL, REDIS_URL, SECRET_KEY (and NEXT_PUBLIC_API_URL for prod)"
echo "  2. Run setup wizard (optional): npm run setup"
echo "  3. Start infra: docker compose up -d postgres redis"
echo "  4. Migrate: npm run db:migrate"
echo "  5. Seed: npm run db:seed"
echo "  6. Dev: npm run dev:api & npm run dev"
echo "  Or prod: ./scripts/deploy.sh prod"
echo ""
