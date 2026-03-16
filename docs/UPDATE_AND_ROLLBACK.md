# Update and Rollback

## Updating AUTHORA

### Standard Update

```bash
./scripts/update.sh [dev|prod]
```

This will:

1. `git pull --rebase` (if in a git repo)
2. Ensure postgres and redis are running
3. Build images with `--no-cache`
4. Run migrations
5. Restart all services

### Manual Update

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm -e DATABASE_URL="${DATABASE_URL}" api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d
```

## Rollback

### Application Rollback

1. Checkout the previous version:
   ```bash
   git checkout <previous-tag-or-commit>
   ```

2. Rebuild and restart:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
   docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d
   ```

### Database Rollback

**Warning**: Migrations are designed to move forward. Rolling back migrations can cause data loss.

If you must roll back a migration:

```bash
cd apps/api
alembic downgrade -1   # One revision back
# or
alembic downgrade <revision_id>
```

Prefer fixing forward with a new migration when possible.

### Full Restore

To restore from a backup after a failed update:

1. Stop services
2. Restore database: `./scripts/restore.sh backups/authora_YYYYMMDD.dump`
3. Checkout previous code version
4. Rebuild and start

## Pre-Update Checklist

- [ ] Backup database: `./scripts/backup.sh`
- [ ] Note current git commit/tag
- [ ] Review migration files in `apps/api/alembic/versions/`
- [ ] Test update in staging first if available
