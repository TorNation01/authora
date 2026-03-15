#!/bin/bash
# PostgreSQL backup for AUTHORA
# Usage: ./scripts/backup.sh [output_dir]
# With Docker: docker compose exec -T postgres pg_dump ... (run from host with exec)

set -e

OUTPUT_DIR="${1:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$OUTPUT_DIR/authora_$TIMESTAMP.dump"

mkdir -p "$OUTPUT_DIR"

if docker compose ps postgres 2>/dev/null | grep -q "Up"; then
  echo "Backing up via Docker..."
  docker compose exec -T postgres pg_dump -U authora -Fc authora > "$BACKUP_FILE"
else
  echo "Backing up via local pg_dump..."
  pg_dump -Fc -f "$BACKUP_FILE" "${DATABASE_URL}"
fi

echo "Backup saved: $BACKUP_FILE"
ls -la "$BACKUP_FILE"
