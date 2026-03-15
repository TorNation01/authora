# AUTHORA Go-Live Recommendations

Pre-launch and post-launch guidance for production deployment.

---

## Pre-Launch (Must-Do)

### 1. Environment

```bash
# Generate and set
export SECRET_KEY=$(openssl rand -hex 32)
export CRON_SECRET=$(openssl rand -hex 32)   # if using reminder cron
export DEBUG=false
export CORS_ORIGINS="https://your-domain.com"
```

### 2. Database

- [ ] Migrations applied: `npm run db:migrate`
- [ ] Seed run if needed: `npm run db:seed`
- [ ] Connection pool sized for expected load
- [ ] Backups configured and tested

### 3. Redis

- [ ] Redis available for sessions/cache
- [ ] Readiness check passes: `GET /health/ready`

### 4. Secrets

- [ ] All API keys (AI, email) configured
- [ ] No secrets in code or logs
- [ ] `.env` not committed; use secrets manager in prod

### 5. Frontend

- [ ] `NEXT_PUBLIC_API_URL` points to production API
- [ ] Build succeeds: `npm run build`
- [ ] 404 and error pages render correctly

---

## Pre-Launch (Should-Do)

### 6. Observability

- [ ] Log aggregation (e.g. Loki, CloudWatch, Datadog)
- [ ] Alerting on 5xx, high 4xx, readiness failures
- [ ] Request ID used for support correlation

### 7. Rate Limiting

- [ ] Default 100 req/min per IP acceptable; tune if needed
- [ ] For multi-worker: plan Redis-backed rate limit

### 8. API Docs

- [ ] Disable `/api/docs` and `/api/redoc` in production, or restrict by IP/auth

### 9. Dependency Audit

```bash
npm run audit
cd apps/api && pip-audit
```

---

## Post-Launch

### Week 1

- [ ] Monitor error rates and latency
- [ ] Verify cron jobs (if used) run successfully
- [ ] Check storage usage and export job success
- [ ] Confirm no default SECRET_KEY warning in logs

### Ongoing

- [ ] Run `npm run audit` and `pip-audit` monthly
- [ ] Review audit logs for anomalies
- [ ] Test backup restore quarterly
- [ ] Update dependencies on schedule

---

## Rollback

- [ ] Database migrations reversible or have rollback plan
- [ ] Previous app version deployable
- [ ] Feature flags (if used) allow quick disable

---

## Support Readiness

- [ ] Request ID in all error responses for ticket correlation
- [ ] Admin panel accessible for support (user context, support notes)
- [ ] Health endpoints for ops: `/health`, `/health/ready`
