# Backups and Restore

## PostgreSQL Backup

### Manual Backup

```bash
./scripts/backup.sh [output_dir]
```

Default output: `./backups/authora_YYYYMMDD_HHMMSS.dump`

Uses `pg_dump -Fc` (custom format) for efficient backups.

### Automated Backups (Cron)

Add to crontab for daily backups at 2 AM:

```bash
0 2 * * * cd /path/to/authora && ./scripts/backup.sh ./backups
```

### Backup Retention

Configure in the setup wizard or `.env`:

```
BACKUP_ENABLED=true
BACKUP_RETENTION_DAYS=7
```

Use a separate cron job or script to prune old backups based on retention.

## Restore

### From Backup File

```bash
./scripts/restore.sh backups/authora_20240101_020000.dump
```

Or manually:

```bash
# With Docker
docker compose exec -T postgres pg_restore -U authora -d authora -c < backup.dump

# Local
pg_restore -d "$DATABASE_URL" -c backup.dump
```

### Precautions

- Stop the application or put it in maintenance mode before restore
- Restore overwrites existing data
- Test restores in a staging environment first

## Storage Backups

For local storage (`STORAGE_LOCAL_PATH`), include the storage directory in your backup strategy:

```bash
tar -czvf storage_backup_$(date +%Y%m%d).tar.gz ./storage
```

For S3/R2, use the provider's backup/replication features.
