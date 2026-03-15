# AUTHORA Go-Live Checklist

Pre- and post-deployment validation for production go-live.

## Pre-Deploy

- [ ] `.env` configured with production values
- [ ] `SECRET_KEY` changed (not default) — `openssl rand -hex 32`
- [ ] `NEXT_PUBLIC_API_URL` set to public API URL (e.g. `https://api.yourdomain.com`)
- [ ] `DOMAIN_API`, `DOMAIN_WEB`, `ACME_EMAIL` set for Caddy
- [ ] `./scripts/validate-env.sh production` passes
- [ ] `caddy/Caddyfile` exists (run `./scripts/generate-caddyfile.sh` if needed)
- [ ] DNS A records point to server for `DOMAIN_API` and `DOMAIN_WEB`
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
./scripts/verify-go-live.sh https://api.yourdomain.com
```

Or manual:

1. **API health**
   ```bash
   curl -sf https://api.yourdomain.com/health
   # Expect: {"status":"ok","app":"AUTHORA"}
   ```

2. **Readiness**
   ```bash
   curl -sf https://api.yourdomain.com/health/ready
   # Expect: {"status":"ready","checks":{"database":true,"redis":true}}
   ```

3. **Web app**
   - Open https://app.yourdomain.com
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

## Known Manual Steps

- **SSL:** Caddy auto-provisions via Let's Encrypt. Ensure ports 80/443 open.
- **Email:** If using SMTP, configure in setup wizard or env.
- **AI keys:** Add `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for AI features.
