# AUTHORA Release Gates

Mandatory gates for production release. All must pass before go-live.

> **See also:** [LAUNCH_GATE_SYSTEM](LAUNCH_GATE_SYSTEM.md) – Final go/no-go checklist, blocker list, post-launch, rollback, and operator quick-reference.
> **CI/Release:** [CI_PIPELINE](CI_PIPELINE.md), [TEST_MATRIX](TEST_MATRIX.md), [RELEASE_WORKFLOW](RELEASE_WORKFLOW.md), [QUALITY_GATES](QUALITY_GATES.md).

## Pre-Release Gates

| Gate | Command / Check | Required |
|------|-----------------|----------|
| Unit tests | `cd apps/api && pytest` | ✓ |
| Integration tests | Same as above | ✓ |
| E2E smoke | `cd apps/web && npm run test:e2e -- smoke.spec.ts` | ✓ |
| Migrations | `alembic upgrade head` (dry run) | ✓ |
| Env validation | `./scripts/validate-env.sh production` | ✓ |
| Health checks | `./scripts/healthcheck.sh $API_URL` | ✓ |
| Billing health | `GET /api/v1/billing/admin/health` (admin) | If billing enabled |
| Backup script | `./scripts/backup.sh` runs successfully | ✓ |
| Restore drill | Restore from backup, verify | ✓ |

## Go/No-Go Checklist

- [ ] All tests passing
- [ ] Migrations validated
- [ ] Env validation passing
- [ ] Health checks green
- [ ] Core E2E flows green (auth, project, export)
- [ ] Billing/webhook validation complete (if enabled)
- [ ] AI providers configured or degraded mode accepted
- [ ] Export validation complete
- [ ] Backup script validated
- [ ] Restore instructions confirmed
- [ ] Domain/SSL ready
- [ ] Admin bootstrap complete

## Post-Launch Smoke Checks

Run within 1 hour of launch:

1. `curl -sf https://api.your-domain/health`
2. `curl -sf https://api.your-domain/health/ready`
3. Login at web URL
4. Create project
5. Export manuscript

## Rollback Trigger Checklist

Trigger rollback if:

- Health checks fail repeatedly
- Critical auth/login broken
- Data corruption detected
- Security incident

See [INCIDENT_RESPONSE_RUNBOOK](INCIDENT_RESPONSE_RUNBOOK.md).
