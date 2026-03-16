#!/bin/bash
# PostgreSQL backup for AUTHORA
# Usage: ./scripts/backup.sh [output_dir]
# With Docker: uses postgres container. Otherwise: pg_dump with DATABASE_URL from .env

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"
[ -f .env ] && set -a && source .env && set +a

OUTPUT_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$OUTPUT_DIR/authora_$TIMESTAMP.dump"

mkdir -p "$OUTPUT_DIR"

# Prefer prod compose if .env suggests production
COMPOSE_FILES="-f docker-compose.yml"
[ -f docker-compose.prod.yml ] && COMPOSE_FILES="$COMPOSE_FILES -f docker-compose.prod.yml"

if docker compose $COMPOSE_FILES ps postgres 2>/dev/null | grep -q "Up"; then
  echo "Backing up via Docker..."
  docker compose $COMPOSE_FILES exec -T postgres pg_dump -U authora -Fc authora > "$BACKUP_FILE"
elif docker compose ps postgres 2>/dev/null | grep -q "Up"; then
  echo "Backing up via Docker (dev)..."
  docker compose exec -T postgres pg_dump -U authora -Fc authora > "$BACKUP_FILE"
else
  echo "Backing up via local pg_dump..."
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  pg_dump -Fc -f "$BACKUP_FILE" "$DATABASE_URL"
fi

echo "Backup saved: $BACKUP_FILE"
ls -la "$BACKUP_FILE"
