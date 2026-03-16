# AUTHORA Go-Live Checklist

Pre- and post-deployment validation for production go-live (Option 2: authora.studio, app.authora.studio, api.authora.studio).

## Pre-Deploy

- [ ] `.env` configured with production values
- [ ] `SECRET_KEY` changed (not default) — `openssl rand -hex 32`
- [ ] `NEXT_PUBLIC_API_URL` = `https://api.authora.studio`
- [ ] `NEXT_PUBLIC_MARKETING_URL` = `https://authora.studio`
- [ ] `NEXT_PUBLIC_APP_URL` = `https://app.authora.studio`
- [ ] `CORS_ORIGINS` = `["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]`
- [ ] `DOMAIN_API`, `DOMAIN_MARKETING`, `DOMAIN_APP`, `ACME_EMAIL` set for Caddy
- [ ] `./scripts/validate-env.sh production` passes (if available)
- [ ] `caddy/Caddyfile` exists (run `./scripts/generate-caddyfile.sh` if needed)
- [ ] DNS A/CNAME for `api.authora.studio`, `authora.studio`, `app.authora.studio`
- [ ] Firewall allows 80, 443 (and 22 for SSH)

## Deploy

```bash
cd /path/to/authora
./scripts/deploy.sh prod
```

Or:
```bash
npm run deploy:prod
```

## Post-Deploy Verification

```bash
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio
```

Or manual:

1. **API health**
   ```bash
   curl -sf https://api.authora.studio/health
   # Expect: {"status":"ok","app":"AUTHORA"}
   ```

2. **Readiness**
   ```bash
   curl -sf https://api.authora.studio/health/ready
   # Expect: {"status":"ready","checks":{"database":true,"redis":true}}
   ```

3. **Web app**
   - Open https://authora.studio
   - Login or register
   - Create a project

4. **First admin**
   ```bash
   ./scripts/first-admin.sh --docker --prod
   ```
   Login: `admin@authora.local` / `admin123` — change password immediately

## Backup Cron

```bash
# Add to crontab: daily backup at 2am
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

## Rollback (If Needed)

```bash
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
```

## Domain Documentation

- [DOMAIN_ARCHITECTURE.md](DOMAIN_ARCHITECTURE.md) — Option 2 structure (authora.studio, app.authora.studio, api.authora.studio)
- [DOMAIN_ENV_EXAMPLES.md](DOMAIN_ENV_EXAMPLES.md) — Exact env values
- [DOMAIN_REVERSE_PROXY.md](DOMAIN_REVERSE_PROXY.md) — Reverse proxy setup
- [DOMAIN_DNS_RECORDS.md](DOMAIN_DNS_RECORDS.md) — DNS record summary
- [DOMAIN_SSL_GO_LIVE.md](DOMAIN_SSL_GO_LIVE.md) — SSL and go-live checklist
- [DOMAIN_AUTH_SESSION.md](DOMAIN_AUTH_SESSION.md) — Auth/session/cookie strategy

## Known Manual Steps

- **SSL:** Caddy auto-provisions via Let's Encrypt. Ensure ports 80/443 open.
- **Email:** If using SMTP, configure in setup wizard or env.
- **AI keys:** Add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for AI features.
