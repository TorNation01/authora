# AUTHORA Security Checklist

Use this checklist before production deployment and during security reviews.

---

## Pre-Deployment

### Secrets & Configuration

- [ ] `SECRET_KEY` set to strong value (`openssl rand -hex 32`)
- [ ] `CRON_SECRET` set when using reminder cron jobs
- [ ] `CORS_ORIGINS` restricted to production frontend origin(s)
- [ ] `DEBUG=false` in production
- [ ] Database credentials not in version control
- [ ] API keys (OpenAI, Anthropic, SMTP, SendGrid) in env/secrets only

### Authentication

- [ ] JWT `access_token_expire_minutes` appropriate (e.g. 60)
- [ ] Refresh token expiry configured
- [ ] First admin created via setup wizard or seed; default admin disabled
- [ ] SSO configured if `feature_sso_ready` enabled

### Network & Headers

- [ ] HTTPS enforced (TLS at load balancer/reverse proxy)
- [ ] HSTS header set at reverse proxy
- [ ] Security headers verified (X-Content-Type-Options, X-Frame-Options, etc.)
- [ ] API docs (`/api/docs`, `/api/redoc`) disabled or restricted in production

### Input & Output

- [ ] All API inputs validated via Pydantic
- [ ] File uploads: MIME, extension, size, path traversal checks
- [ ] No raw SQL with user input; parameterized queries only
- [ ] Error responses do not leak stack traces or internal paths

### Access Control

- [ ] Admin routes require `is_admin`
- [ ] Resource ownership enforced (`require_owner`) where applicable
- [ ] Cron endpoint protected by `CRON_SECRET` when used

---

## Ongoing

### Dependencies

- [ ] `npm run audit` run regularly; high/critical addressed
- [ ] `pip-audit` (or `safety check`) run for Python deps
- [ ] Dependencies updated on schedule

### Monitoring

- [ ] Failed auth attempts monitored
- [ ] Rate limit (429) spikes investigated
- [ ] Error rates and request_id correlation available
- [ ] Audit logs retained per compliance needs

### Operational

- [ ] Backups tested and restorable
- [ ] Session/refresh token cleanup for inactive users (if applicable)
- [ ] Password change invalidates other sessions (future enhancement)

---

## Quick Commands

```bash
# npm dependency audit
npm run audit

# Python dependency audit (from apps/api)
pip install pip-audit && pip-audit
```
