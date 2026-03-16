#!/bin/bash
# AUTHORA One-Command Deploy
# Usage: ./scripts/deploy.sh [dev|prod] [repo_url]
#
# Flow: clone (if needed) → copy env → preflight → validate → docker → migrate → seed → verify
# Idempotent: safe to re-run.
#
# Quickstart (dev):
#   git clone https://github.com/TorNation01/authora.git && cd authora && cp .env.example .env && ./scripts/deploy.sh
#
# Production:
#   git clone ... && cd authora && cp .env.production.example .env && # edit SECRET_KEY, domains # && ./scripts/deploy.sh prod

set -e

MODE="${1:-dev}"
REPO_URL="${2:-https://github.com/TorNation01/authora.git}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
fail() {
  echo ""
  echo "❌ $1"
  echo ""
  [ -n "$2" ] && echo "   Fix: $2"
  echo ""
  exit 1
}

warn() {
  echo "⚠️  $1"
}

ok() {
  echo "✓ $1"
}

section() {
  echo ""
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "  $1"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# -----------------------------------------------------------------------------
# Step 0: Ensure we're in a clone
# -----------------------------------------------------------------------------
section "Step 0: Repository"

if [ -f "$ROOT_DIR/package.json" ] && [ -f "$ROOT_DIR/docker-compose.yml" ]; then
  ok "Using existing clone: $ROOT_DIR"
  cd "$ROOT_DIR"
else
  echo "Not in a valid AUTHORA repo. Cloning from $REPO_URL..."
  PARENT="$(cd "$SCRIPT_DIR/../.." && pwd)"
  if git clone "$REPO_URL" "$PARENT/authora" 2>/dev/null; then
    ok "Cloned to $PARENT/authora"
    cd "$PARENT/authora"
    ROOT_DIR="$(pwd)"
  else
    fail "Clone failed." \
      "Ensure git is installed (apt install git) and the URL is correct. Or clone manually: git clone $REPO_URL authora && cd authora"
  fi
fi

# -----------------------------------------------------------------------------
# Step 1: Preflight checks
# -----------------------------------------------------------------------------
section "Step 1: Preflight"

MISSING=""

if ! command -v docker &> /dev/null; then
  MISSING="${MISSING}docker "
fi

if ! docker compose version &> /dev/null 2>&1; then
  if ! command -v docker-compose &> /dev/null; then
    MISSING="${MISSING}docker-compose "
  fi
fi

if ! command -v git &> /dev/null; then
  MISSING="${MISSING}git "
fi

if [ -n "$MISSING" ]; then
  fail "Missing required tools: $MISSING" \
    "Install them first. On Ubuntu: sudo apt update && sudo apt install -y git docker.io docker-compose-plugin. Or run ./scripts/bootstrap.sh for full server setup."
fi

ok "Docker: $(docker --version)"
ok "Docker Compose: $(docker compose version 2>/dev/null || docker-compose --version)"
ok "Git: $(git --version)"

# Docker daemon reachable?
if ! docker info &> /dev/null; then
  fail "Docker daemon not reachable." \
    "Start Docker (systemctl start docker) or add your user to the docker group: sudo usermod -aG docker \$USER, then log out and back in."
fi

ok "Docker daemon is running"

# -----------------------------------------------------------------------------
# Step 2: Environment file
# -----------------------------------------------------------------------------
section "Step 2: Environment"

if [ ! -f .env ]; then
  if [ "$MODE" = "prod" ] && [ -f .env.production.example ]; then
    cp .env.production.example .env
    ok "Created .env from .env.production.example"
    echo ""
    fail "Production requires configuration before deploy." \
      "Edit .env: set SECRET_KEY (openssl rand -hex 32), DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL, and domain vars. Then run ./scripts/deploy.sh prod again."
  elif [ -f .env.example ]; then
    cp .env.example .env
    ok "Created .env from .env.example (dev defaults)"
    warn "For production: cp .env.production.example .env and configure SECRET_KEY, domains, etc."
  else
    fail ".env not found and no .env.example available." \
      "Create .env with DATABASE_URL, REDIS_URL, SECRET_KEY. See docs for reference."
  fi
else
  ok ".env exists"
fi

# Load for validation
set -a
[ -f .env ] && source .env
set +a

# -----------------------------------------------------------------------------
# Step 3: Validate environment
# -----------------------------------------------------------------------------
section "Step 3: Validate environment"

VALIDATE_MODE="development"
[ "$MODE" = "prod" ] && VALIDATE_MODE="production"

if [ -f scripts/validate-env.sh ]; then
  if ./scripts/validate-env.sh "$VALIDATE_MODE" 2>/dev/null; then
    ok "Environment validation passed"
  else
    if [ "$MODE" = "prod" ]; then
      fail "Environment validation failed." \
        "Fix the errors above. See .env.production.example for required variables. Common: SECRET_KEY (openssl rand -hex 32), NEXT_PUBLIC_API_URL, DATABASE_URL, REDIS_URL."
    else
      warn "Validation had warnings. Fix .env before deploying to production."
    fi
  fi
else
  warn "validate-env.sh not found, skipping validation"
fi

# -----------------------------------------------------------------------------
# Step 4: Directories and Caddyfile (prod)
# -----------------------------------------------------------------------------
section "Step 4: Prepare"

mkdir -p backups storage caddy/data caddy/config 2>/dev/null || true
ok "Directories ready"

if [ "$MODE" = "prod" ]; then
  if [ ! -f caddy/Caddyfile ]; then
    if [ -f scripts/generate-caddyfile.sh ]; then
      ./scripts/generate-caddyfile.sh
      ok "Generated caddy/Caddyfile from .env"
    elif [ -f caddy/Caddyfile.example ]; then
      cp caddy/Caddyfile.example caddy/Caddyfile
      ok "Copied caddy/Caddyfile.example. Edit DOMAIN_* and ACME_EMAIL in .env before going live."
    else
      warn "No Caddyfile. Create caddy/Caddyfile for SSL. See docs/DOMAIN_AND_SSL.md"
    fi
  else
    ok "Caddyfile exists"
  fi
fi

# -----------------------------------------------------------------------------
# Step 5: Docker build and up (infra first)
# -----------------------------------------------------------------------------
section "Step 5: Docker"

COMPOSE_FILES="-f docker-compose.yml"
[ "$MODE" = "prod" ] && COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"

echo "Starting PostgreSQL and Redis..."
docker compose $COMPOSE_FILES up -d postgres redis 2>/dev/null || docker-compose $COMPOSE_FILES up -d postgres redis

echo "Waiting for PostgreSQL (up to 60s)..."
WAIT=0
until docker compose $COMPOSE_FILES exec -T postgres pg_isready -U authora 2>/dev/null; do
  sleep 2
  WAIT=$((WAIT + 2))
  if [ $WAIT -ge 60 ]; then
    fail "PostgreSQL did not become ready in time." \
      "Check logs: docker compose logs postgres"
  fi
done
ok "PostgreSQL is ready"

# -----------------------------------------------------------------------------
# Step 6: Migrations
# -----------------------------------------------------------------------------
section "Step 6: Migrations"

DB_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
DB_URL="${DB_URL/localhost:5432/postgres:5432}"
DB_URL="${DB_URL/127.0.0.1:5432/postgres:5432}"

if docker compose $COMPOSE_FILES run --rm -e DATABASE_URL="${DB_URL}" api alembic upgrade head 2>/dev/null; then
  ok "Migrations applied"
else
  fail "Migrations failed." \
    "Run manually: docker compose run --rm -e DATABASE_URL=\"\$DATABASE_URL\" api alembic upgrade head. Check apps/api/alembic/ for migration issues."
fi

# -----------------------------------------------------------------------------
# Step 7: Seed (idempotent - skips if users exist)
# -----------------------------------------------------------------------------
section "Step 7: Seed"

REDIS_URL_DOCKER="${REDIS_URL:-redis://redis:6379/0}"
REDIS_URL_DOCKER="${REDIS_URL_DOCKER/localhost:6379/redis:6379}"
REDIS_URL_DOCKER="${REDIS_URL_DOCKER/127.0.0.1:6379/redis:6379}"

if docker compose $COMPOSE_FILES run --rm \
  -e DATABASE_URL="${DB_URL}" \
  -e REDIS_URL="${REDIS_URL_DOCKER}" \
  -e SECRET_KEY="${SECRET_KEY:-dev-secret-change-in-production}" \
  api python -m authora.scripts.seed 2>/dev/null; then
  ok "Seed completed (or skipped - data already exists)"
else
  warn "Seed failed or skipped. You can create an admin manually or run: docker compose run --rm api python -m authora.scripts.seed"
fi

# -----------------------------------------------------------------------------
# Step 8: Start full stack
# -----------------------------------------------------------------------------
section "Step 8: Start services"

if [ "$MODE" = "prod" ]; then
  echo "Building production images..."
  docker compose $COMPOSE_FILES build
  echo "Starting full stack (including Caddy)..."
  docker compose $COMPOSE_FILES --profile prod up -d
else
  echo "Starting API and Web..."
  docker compose $COMPOSE_FILES up -d
fi

ok "Stack is starting"

# -----------------------------------------------------------------------------
# Step 9: Post-deploy verification
# -----------------------------------------------------------------------------
section "Step 9: Verify"

echo "Waiting for services to be ready (15s)..."
sleep 15

API_URL="${NEXT_PUBLIC_API_URL:-http://localhost:8000}"
[ -z "$API_URL" ] && API_URL="http://localhost:8000"
# For dev, API might be on localhost:8000
[ "$MODE" = "dev" ] && API_URL="http://localhost:8000"

VERIFY_FAIL=0
if curl -sf --connect-timeout 10 "$API_URL/health" > /dev/null 2>&1; then
  ok "API /health: OK"
else
  echo "❌ API /health: FAIL"
  VERIFY_FAIL=1
fi

if curl -sf --connect-timeout 10 "$API_URL/health/ready" > /dev/null 2>&1; then
  ok "API /health/ready: OK"
else
  echo "❌ API /health/ready: FAIL"
  VERIFY_FAIL=1
fi

if [ $VERIFY_FAIL -eq 1 ]; then
  echo ""
  fail "Health check failed. Services may still be starting." \
    "Wait 30s and run: ./scripts/healthcheck.sh $API_URL. Or check logs: docker compose logs api"
fi

# -----------------------------------------------------------------------------
# Step 10: Admin bootstrap handoff & next actions
# -----------------------------------------------------------------------------
section "Deploy complete"

WEB_URL="http://localhost:3000"
[ "$MODE" = "prod" ] && WEB_URL="${NEXT_PUBLIC_APP_URL:-https://app.authora.studio}"
[ -z "$WEB_URL" ] || [ "$WEB_URL" = "http://localhost:3000" ] && WEB_URL="http://localhost:3000"

echo ""
echo "  AUTHORA is running."
echo ""
echo "  Web:  $WEB_URL"
echo "  API:  $API_URL"
echo ""
echo "  Next actions:"
echo "    1. Complete setup wizard: $WEB_URL/setup"
echo "    2. Create your first admin account"
echo "    3. Sign in at $WEB_URL/login"
echo ""
if [ "$MODE" = "prod" ]; then
  echo "  Production tips:"
  echo "    • Ensure DNS points to this server (A records for your domains)"
  echo "    • Caddy will obtain SSL certificates automatically"
  echo "    • Add backup cron: 0 2 * * * $(pwd)/scripts/backup.sh"
  echo "    • Update: ./scripts/update.sh prod"
  echo ""
else
  echo "  Dev tips:"
  echo "    • For production: cp .env.production.example .env, configure, then ./scripts/deploy.sh prod"
  echo "    • Health check: ./scripts/healthcheck.sh $API_URL"
  echo ""
fi

echo "  You can re-run this script safely (idempotent)."
echo ""
