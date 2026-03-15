# AUTHORA Go-Live Checklist

Final verification before production launch.

---

## Environment

- [ ] `SECRET_KEY` set (openssl rand -hex 32)
- [ ] `CRON_SECRET` set if using reminders
- [ ] `DATABASE_URL` production DB
- [ ] `REDIS_URL` production Redis
- [ ] `CORS_ORIGINS` = production frontend URL
- [ ] `NEXT_PUBLIC_API_URL` = production API URL
- [ ] `DEBUG=false`

## Infrastructure

- [ ] Database migrations applied
- [ ] Redis available
- [ ] Storage (local/S3/R2) configured
- [ ] Backups scheduled
- [ ] SSL/TLS enabled

## Services

- [ ] API health: GET /health → 200
- [ ] Readiness: GET /health/ready → 200
- [ ] Frontend loads
- [ ] API reachable from frontend

## Auth & Data

- [ ] First admin created (setup wizard or seed)
- [ ] Test user can register and login
- [ ] Session persistence works

## Monitoring

- [ ] Log aggregation configured
- [ ] Error alerting set up
- [ ] Uptime monitoring
- [ ] Request ID in logs for support

## Rollback Plan

- [ ] Previous version tagged
- [ ] Database rollback procedure documented
- [ ] Rollback tested in staging

## Communication

- [ ] Stakeholders notified
- [ ] Support team briefed
- [ ] Known issues communicated
