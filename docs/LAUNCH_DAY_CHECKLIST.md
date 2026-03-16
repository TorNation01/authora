# AUTHORA Launch Day Checklist

Operational checklist for launch day and post-launch validation.

> **See also:** [LAUNCH_GATE_SYSTEM](LAUNCH_GATE_SYSTEM.md) – Full launch gate checklist, blocker list, post-launch 24h, rollback decision, and operator quick-response.

## Pre-Launch (T-24h)

- [ ] All release gates passed (see [RELEASE_GATES](RELEASE_GATES.md))
- [ ] DNS propagated
- [ ] SSL certificates obtained (Caddy/Let's Encrypt)
- [ ] Backup cron configured
- [ ] Monitoring/alerting configured (if any)
- [ ] Support contact ready

## Launch (T-0)

1. **Deploy**
   ```bash
   ./scripts/deploy.sh prod
   ```

2. **Verify health**
   ```bash
   ./scripts/healthcheck.sh https://api.your-domain.com
   ./scripts/verify-go-live.sh https://api.your-domain.com https://your-domain.com
   ```

3. **First admin**
   ```bash
   ./scripts/first-admin.sh --docker --prod
   ```
   Change default password immediately.

4. **Smoke tests**
   - Login
   - Create project
   - Write chapter
   - Export DOCX

## Post-Launch (T+1h)

- [ ] Run [POST_DEPLOY_SMOKE_TESTS](POST_DEPLOY_SMOKE_TESTS.md)
- [ ] Check logs for errors
- [ ] Verify backup ran (if cron already triggered)

## Post-Launch (T+24h)

- [ ] Review audit logs
- [ ] Verify backup/restore drill
- [ ] User feedback triage
