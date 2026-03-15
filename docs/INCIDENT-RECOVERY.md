# AUTHORA Incident Recovery

## Quick Recovery Checklist

1. **Assess**: Check logs, health endpoints, resource usage
2. **Contain**: Stop affected services if needed
3. **Restore**: Recover from backup if data loss
4. **Verify**: Run health checks, smoke test
5. **Communicate**: Notify users if downtime occurred

## Common Incidents

### API returns 503

**Cause**: DB or Redis unreachable

**Actions**:
1. `docker compose ps` – check service status
2. `docker compose logs api` – check errors
3. Restart: `docker compose restart api`
4. If DB: `docker compose restart postgres` – wait for healthy, then restart api

### Database corruption or bad migration

**Actions**:
1. Stop API: `docker compose stop api web`
2. Restore: `./scripts/restore.sh ./backups/authora_YYYYMMDD.dump`
3. If migration issue: `alembic downgrade -1` then fix, then `alembic upgrade head`
4. Restart: `docker compose start api web`

### Out of disk space

**Actions**:
1. `df -h` – identify full partition
2. Clean logs: `docker system prune -f`
3. Clean old backups: `find ./backups -mtime +30 -delete`
4. Expand disk or migrate if needed

### Secret key rotated

**Actions**:
1. Update `.env` with new `SECRET_KEY`
2. Restart API: `docker compose restart api`
3. All users must re-login (sessions invalidated)

### Rollback to previous version

```bash
./scripts/rollback.sh ./backups/authora_YYYYMMDD.dump prod
# Or: git checkout <previous-tag> && ./scripts/update.sh prod
```

## Backup Verification

Run monthly:

```bash
# Create test restore in separate DB
createdb authora_restore_test
pg_restore -d authora_restore_test ./backups/authora_latest.dump
# Verify row counts, etc.
dropdb authora_restore_test
```

## Post-Incident

1. Document timeline and root cause
2. Update runbooks or scripts
3. Add monitoring/alerting if gap was found
4. Schedule backup verification if data was involved
