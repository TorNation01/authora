# AUTHORA SSL & Go-Live Checklist (Option 2)

Pre- and post-deployment validation for production with **authora.studio**, **app.authora.studio**, **api.authora.studio**.

## Pre-Deploy Checklist

- [ ] **SECRET_KEY** — Changed from default (`openssl rand -hex 32`)
- [ ] **CRON_SECRET** — Set if reminders enabled (`openssl rand -hex 32`)
- [ ] **DATABASE_URL** — Production PostgreSQL connection string
- [ ] **REDIS_URL** — Production Redis URL
- [ ] **NEXT_PUBLIC_API_URL** — `https://api.authora.studio`
- [ ] **NEXT_PUBLIC_MARKETING_URL** — `https://authora.studio`
- [ ] **NEXT_PUBLIC_APP_URL** — `https://app.authora.studio`
- [ ] **CORS_ORIGINS** — `["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]`
- [ ] **DOMAIN_API** — `api.authora.studio`
- [ ] **DOMAIN_MARKETING** — `authora.studio`
- [ ] **DOMAIN_APP** — `app.authora.studio`
- [ ] **ACME_EMAIL** — `admin@authora.studio` (for Let's Encrypt)
- [ ] **Caddyfile** — Generated via `./scripts/generate-caddyfile.sh`
- [ ] **DNS** — A or CNAME for `api.authora.studio`, `authora.studio`, `app.authora.studio`
- [ ] **Firewall** — Ports 80, 443 (and 22 for SSH) open
- [ ] **DEBUG** — `false` in production

## SSL (Caddy)

Caddy auto-provisions Let's Encrypt certificates. No manual cert steps if:

1. DNS records are correct for all hostnames before Caddy starts
2. Port 80 is reachable (HTTP-01 challenge)
3. `ACME_EMAIL` is set in Caddyfile/global block

## SSL (Nginx + Certbot)

```bash
sudo certbot --nginx -d api.authora.studio -d authora.studio -d app.authora.studio -d www.authora.studio
```

## Post-Deploy Verification

```bash
# 1. API health
curl -sf https://api.authora.studio/health
# Expect: {"status":"ok","app":"AUTHORA"}

# 2. Readiness
curl -sf https://api.authora.studio/health/ready
# Expect: {"status":"ready","checks":{"database":true,"redis":true}}

# 3. Full verification (API + CORS for marketing and app)
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio https://app.authora.studio
```

## Manual Checks

1. **Marketing** — Open https://authora.studio, click "Sign in" → should go to app.authora.studio/login
2. **App** — Open https://app.authora.studio, login/register, create project
3. **API docs** — https://api.authora.studio/api/docs
4. **CORS** — Requests from authora.studio and app.authora.studio to api.authora.studio should succeed
5. **SSL** — No mixed content or certificate warnings

## Cron Setup

```bash
# Reminders (hourly)
0 * * * * curl -X POST -H "X-Cron-Secret: YOUR_CRON_SECRET" https://api.authora.studio/api/v1/accountability/cron/reminders

# Backup (daily 2am)
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

## Rollback

```bash
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
```

## See Also

- [DOMAIN_ARCHITECTURE.md](DOMAIN_ARCHITECTURE.md) — Domain structure
- [DOMAIN_ENV_EXAMPLES.md](DOMAIN_ENV_EXAMPLES.md) — Env values
- [DOMAIN_REVERSE_PROXY.md](DOMAIN_REVERSE_PROXY.md) — Reverse proxy setup
- [DOMAIN_AUTH_SESSION.md](DOMAIN_AUTH_SESSION.md) — Auth/session/cookie strategy
- [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md) — General go-live checklist
