# AUTHORA Backup and Restore

Exact commands for backing up and restoring the AUTHORA database.

## Backup

### One-Command Backup

```bash
cd /path/to/authora
./scripts/backup.sh
```

Output: `./backups/authora_YYYYMMDD_HHMMSS.dump`

### Custom Output Directory

```bash
./scripts/backup.sh /path/to/backups
```

### How It Works

- **With Docker:** Uses `pg_dump` inside the postgres container
- **Without Docker:** Uses local `pg_dump` with `DATABASE_URL` from `.env`

### Cron (Daily 2am)

```bash
crontab -e
# Add:
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

### Snapshot Recommendations

- **Before major updates:** `./scripts/backup.sh` before `./scripts/update.sh prod`
- **Retention:** Keep at least 7 daily backups; consider off-site copy (S3, rsync)
- **Storage volume:** Back up `authora_storage` volume if using file uploads

## Restore

### Restore from Backup

```bash
cd /path/to/authora
./scripts/restore.sh ./backups/authora_20250315_020000.dump
```

**Warning:** Overwrites the database. Stop API/web first, or use rollback script.

### With Rollback (Stop → Restore → Start)

```bash
./scripts/rollback.sh ./backups/authora_20250315_020000.dump prod
```

### After Restore

```bash
# Restart services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Or for dev
docker compose up -d
```

## Data Operations Summary

| Operation | Command |
|-----------|---------|
| Backup | `./scripts/backup.sh [output_dir]` |
| Restore | `./scripts/restore.sh <file.dump>` |
| Rollback | `./scripts/rollback.sh <file.dump> [dev\|prod]` |

## Rollback-Safe Notes

- Always backup before `update.sh prod`
- Test restore on a staging copy before production restore
- `pg_restore --clean --if-exists` drops objects before restore; ensure no critical connections
