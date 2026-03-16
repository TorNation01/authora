# AUTHORA Backup/Restore Drill

Validation procedure for backup and restore. Run periodically (e.g. monthly).

## Backup

```bash
cd /path/to/authora
./scripts/backup.sh
```

Verify:
- File created in `./backups/` (or specified dir)
- File size > 0
- `ls -la backups/`

## Restore (Drill)

1. **Note current state**: User count, project count (optional)

2. **Create test backup**
   ```bash
   ./scripts/backup.sh ./backups/drill-test
   ```

3. **Restore to test DB** (use separate DB or staging)
   ```bash
   ./scripts/restore.sh ./backups/drill-test/authora_YYYYMMDD_HHMMSS.dump
   ```

4. **Verify**
   - API health
   - Login works
   - Projects visible

5. **Cleanup** test DB if used

## Rollback (Production)

```bash
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
```

See [UPDATE_AND_ROLLBACK](UPDATE_AND_ROLLBACK.md) for full rollback procedure.
