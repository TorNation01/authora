# Backup & Restore Strategy

For operational commands and cron setup, see [BACKUP_AND_RESTORE.md](./BACKUP_AND_RESTORE.md).

## Database (PostgreSQL)

### Backup
- **Full backup**: Daily at 02:00 UTC
- **WAL archiving**: Continuous (production)
- **Retention**: 7 daily, 4 weekly, 12 monthly
- **Storage**: Same region; encrypted
- **Tool**: `pg_dump` or managed service (RDS, Cloud SQL)

### Restore
1. Stop API and worker
2. Restore DB from backup (or PITR)
3. Verify schema version (Alembic)
4. Restart services
5. Run smoke tests

### Runbook
```bash
# Restore from dump
pg_restore -d authora backup.dump

# Verify
psql -d authora -c "SELECT COUNT(*) FROM users;"
```

## File Storage

- **Exports, uploads**: Stored in S3/R2 or local path
- **Backup**: Versioning enabled on bucket; or daily sync to backup bucket
- **Retention**: Align with data retention (e.g. 1 year)

## Redis

- **Persistence**: RDB snapshots hourly (if enabled)
- **Use**: Session/cache recovery
- **Queues**: Ephemeral; jobs re-queued on failure

## Configuration Backup

- `.env` (redacted) in secure store
- Alembic migrations in git
