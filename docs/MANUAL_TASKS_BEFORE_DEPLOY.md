# Unavoidable Manual Tasks Before Deployment

**Required before going live.** These cannot be automated.

---

## 1. Environment Configuration

| Task | Required | Notes |
|------|----------|-------|
| Set `SECRET_KEY` | **Yes** | `openssl rand -hex 32` |
| Set `CRON_SECRET` | **Yes** (when reminders enabled) | `openssl rand -hex 32`; cron must send `X-Cron-Secret` header |
| Set `DATABASE_URL` | **Yes** | Production PostgreSQL connection string |
| Set `REDIS_URL` | **Yes** | Production Redis URL |
| Set `NEXT_PUBLIC_API_URL` | **Yes** | Public API URL (e.g. https://api.authora.studio) |
| Set `CORS_ORIGINS` | **Yes** | Include your web origin (e.g. https://authora.studio) |
| Set AI keys | **Optional** | `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for AI features |
| Set `DEBUG=false` | **Yes** | Production mode |

---

## 2. Cron Setup

Add to crontab (or equivalent):

```bash
# Reminders (every hour; daily/weekly fire at appropriate times)
0 * * * * curl -X POST -H "X-Cron-Secret: YOUR_CRON_SECRET" https://api.authora.studio/api/v1/accountability/cron/reminders

# Backup (daily 2am)
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

---

## 3. First Admin

After first deploy:

```bash
# Local
./scripts/first-admin.sh

# Production (Docker)
./scripts/first-admin.sh --docker --prod

# Or: create admin via setup wizard at /setup
```

---

## 4. SSL / Domain

- Use Caddy (included in docker-compose.prod.yml) or reverse proxy
- Set `DOMAIN_API`, `DOMAIN_WEB`, `ACME_EMAIL` in Caddyfile (e.g. api.authora.studio, authora.studio) or run `./scripts/generate-caddyfile.sh`
- Run `./scripts/generate-caddyfile.sh` if using Caddy

---

## 5. Storage Volume Backup

- Database backup: `./scripts/backup.sh`
- Storage volume (`authora_storage`): Back up manually or via sync to S3/R2 if using file uploads

---

## 6. Optional: Sentry

- Add `SENTRY_DSN` for error monitoring
- Admin errors page will show persisted errors when integrated

---

## 7. Optional: SSO

- When `FEATURE_SSO_READY=true`, configure `SSO_ISSUER_URL`, `SSO_CLIENT_ID`, `SSO_METADATA_URL`
- Implement OAuth/OIDC flow in `apps/web/src/app/(auth)/sso/page.tsx`
- Until then, SSO page shows "not yet configured" and links to login

---

## 8. Optional: Anakatech

- Set `APP_MODE=anakatech` and integration toggles
- Configure `API_GATEWAY_URL`, SSO URLs
- See `docs/ANAKATECH_INTEGRATION.md`

---

## Checklist (Required)

- [ ] SECRET_KEY set
- [ ] CRON_SECRET set (if reminders enabled)
- [ ] DATABASE_URL set
- [ ] REDIS_URL set
- [ ] NEXT_PUBLIC_API_URL set
- [ ] CORS_ORIGINS set
- [ ] DEBUG=false
- [ ] Cron job for reminders
- [ ] Cron job for backup
- [ ] First admin created
- [ ] SSL/domain configured
