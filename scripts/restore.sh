#!/bin/bash
# PostgreSQL restore for AUTHORA
# Usage: ./scripts/restore.sh <backup_file.dump>
# WARNING: This overwrites the database. Stop API/worker first.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"
[ -f .env ] && set -a && source .env && set +a

BACKUP_FILE="$1"
if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
  echo "Usage: ./scripts/restore.sh <backup_file.dump>"
  echo "Example: ./scripts/restore.sh ./backups/authora_20250115_020000.dump"
  exit 1
fi

echo "Restoring from $BACKUP_FILE..."

if docker compose ps postgres 2>/dev/null | grep -q "Up"; then
  echo "Restoring via Docker..."
  docker compose exec -T postgres pg_restore -U authora -d authora --clean --if-exists < "$BACKUP_FILE" || true
else
  echo "Restoring via local pg_restore..."
  export DATABASE_URL="${DATABASE_URL:-postgresql://authora:authora@localhost:5432/authora}"
  pg_restore -d "$DATABASE_URL" --clean --if-exists "$BACKUP_FILE" || true
fi

echo "Restore complete. Restart API and run: npm run db:migrate"
