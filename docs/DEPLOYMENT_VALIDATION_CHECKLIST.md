# AUTHORA Deployment Validation Checklist

Pre- and post-deployment validation for production readiness.

## Pre-Deploy

- [ ] `./scripts/validate-env.sh production` passes
- [ ] `./scripts/validate-all.sh` passes (or API running)
- [ ] `caddy/Caddyfile` exists (run `./scripts/generate-caddyfile.sh`)
- [ ] DNS A records for API, app, marketing domains
- [ ] Firewall allows 22, 80, 443

## Deploy

```bash
./scripts/deploy.sh prod
```

## Post-Deploy

- [ ] `./scripts/healthcheck.sh https://api.your-domain.com` passes
- [ ] `./scripts/verify-go-live.sh https://api.your-domain.com https://your-domain.com` passes
- [ ] Login works
- [ ] Create project works
- [ ] Export works

## Backup/Restore Drill

- [ ] `./scripts/backup.sh` succeeds
- [ ] Restore from backup (see [BACKUP_RESTORE_DRILL](BACKUP_RESTORE_DRILL.md))
