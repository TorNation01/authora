# AUTHORA Incident Response Runbook

Operational runbook for critical incidents.

## Severity Levels

| Level | Description | Response |
|-------|-------------|----------|
| P1 | Complete outage, data loss | Immediate rollback, all-hands |
| P2 | Major feature broken | Fix or rollback within hours |
| P3 | Degraded experience | Fix within 24h |

## Rollback Procedure

1. **Stop stack**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod down
   ```

2. **Restore database**
   ```bash
   ./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
   ```

3. **Revert code** (if needed)
   ```bash
   git checkout <previous-tag>
   ./scripts/update.sh prod
   ```

4. **Verify** health and smoke tests

## Critical Bug Triage Flow

1. Reproduce
2. Assess severity (P1/P2/P3)
3. If P1: Rollback first, then investigate
4. If P2: Fix forward or rollback
5. Document in incident log

## Support/Admin Emergency Actions

- **Lock user**: Set `is_active=false` in DB
- **Revoke session**: Delete from sessions table (if applicable)
- **Disable feature**: Use feature flag or env override
