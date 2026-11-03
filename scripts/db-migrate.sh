#!/bin/bash
# Run database migrations.
#
# Usage: ./scripts/db-migrate.sh [--docker] [--prod]
#
# Three things this script has to get right, because a fresh deploy silently
# fails without them:
#
#  1. pgvector. Migration 021 runs `CREATE EXTENSION IF NOT EXISTS vector`, and
#     the application role is not a superuser, so on a brand-new database that
#     statement dies with InsufficientPrivilege unless the extension already
#     exists. It is created here, by the superuser, before Alembic runs.
#  2. Loading .env without corrupting it. `set -a; source .env` strips the
#     quotes from JSON-list values, so CORS_ORIGINS arrives as
#     `[https://a,https://b]` and pydantic-settings aborts the whole run with
#     SettingsError. .env is parsed with python-dotenv and re-exported
#     shell-quoted instead.
#  3. The working directory and interpreter. alembic.ini lives in apps/api, and
#     settings look for `.env` relative to the working directory, so the file is
#     loaded from the repo root first and the system alembic is not trusted to
#     be the venv one the app runs on.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

PYTHON="python3"
[[ -x /opt/authora-v2-venv/bin/python ]] && PYTHON=/opt/authora-v2-venv/bin/python

if [[ -f .env ]]; then
  # shellcheck disable=SC2046
  eval "$("$PYTHON" - <<'PY'
import shlex
try:
    from dotenv import dotenv_values
except ImportError:  # pragma: no cover - dotenv ships with pydantic-settings
    raise SystemExit(0)
for key, value in (dotenv_values(".env") or {}).items():
    if value is None:
        continue
    print(f"export {key}={shlex.quote(value)}")
PY
)"
fi

# An explicitly exported DATABASE_URL_OVERRIDE wins over .env, so this can be
# pointed at a scratch database without editing the production file.
if [[ -n "${DATABASE_URL_OVERRIDE:-}" ]]; then
  DATABASE_URL="$DATABASE_URL_OVERRIDE"
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL is not set (checked environment and .env)." >&2
  exit 1
fi

DB_NAME="${DATABASE_URL##*/}"
DB_NAME="${DB_NAME%%\?*}"

if [[ " $* " =~ " --docker " ]]; then
  echo "Running migrations via Docker..."
  COMPOSE_FILES="-f docker-compose.yml"
  [[ " $* " =~ " --prod " ]] && COMPOSE_FILES="-f docker-compose.yml -f docker-compose.prod.yml"
  # shellcheck disable=SC2086
  docker compose $COMPOSE_FILES run --rm -e DATABASE_URL="$DATABASE_URL" api alembic upgrade head
else
  echo "Running migrations for database '$DB_NAME'..."

  # Pre-create pgvector as the superuser (idempotent). Skipped when we cannot
  # use the postgres account - then the extension must already exist.
  if command -v psql >/dev/null 2>&1 && [[ "$(id -u)" == "0" ]]; then
    su - postgres -c "psql -q -d '$DB_NAME' -c 'CREATE EXTENSION IF NOT EXISTS vector'" \
      >/dev/null 2>&1 || echo "  note: could not pre-create pgvector as postgres; assuming it exists"
  fi

  cd apps/api
  "$PYTHON" -m alembic upgrade head
  "$PYTHON" -m alembic current
  cd "$ROOT_DIR"
fi

echo "Migrations complete."
