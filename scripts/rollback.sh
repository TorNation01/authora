#!/bin/bash
# AUTHORA rollback script - restore from backup and restart
# Usage: ./scripts/rollback.sh <backup_file.dump> [dev|prod]

set -e

BACKUP_FILE="$1"
MODE="${2:-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
  echo "Usage: ./scripts/rollback.sh <backup_file.dump> [dev|prod]"
  echo "Example: ./scripts/rollback.sh ./backups/authora_20250115_020000.dump prod"
  exit 1
fi

echo "=== AUTHORA Rollback ==="
echo "Backup: $BACKUP_FILE"
echo "Mode: $MODE"
echo ""

# Stop app services (keep postgres running)
if [ "$MODE" = "prod" ]; then
  docker compose -f docker-compose.yml -f docker-compose.prod.yml stop api web caddy 2>/dev/null || true
else
  docker compose stop api web 2>/dev/null || true
fi

# Restore
./scripts/restore.sh "$BACKUP_FILE"

# Restart
if [ "$MODE" = "prod" ]; then
  docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
else
  docker compose up -d
fi

echo "Rollback complete. Services restarted."
