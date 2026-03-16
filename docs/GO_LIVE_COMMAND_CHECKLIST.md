# AUTHORA Go-Live Command Checklist (One Page)

**Run from project root.** Primary production domain: authora.studio.

---

## Pre-Deploy

```bash
cd /path/to/authora
cp .env.example .env
nano .env   # SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_*_URL, DOMAIN_*, CORS_ORIGINS, ACME_EMAIL
openssl rand -hex 32   # Use for SECRET_KEY
source .env && ./scripts/validate-env.sh production
./scripts/generate-caddyfile.sh   # If caddy/Caddyfile missing
```

- [ ] DNS A records: `api.authora.studio`, `authora.studio`, `app.authora.studio` → server IP
- [ ] Firewall: 80, 443, 22 open

---

## Deploy

```bash
cd /path/to/authora
./scripts/deploy.sh prod
```

---

## Post-Deploy

```bash
./scripts/first-admin.sh --docker --prod
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio https://app.authora.studio
```

- [ ] `curl -sf https://api.authora.studio/health` → `{"status":"ok",...}`
- [ ] `curl -sf https://api.authora.studio/health/ready` → `{"status":"ready",...}`
- [ ] Open https://authora.studio — login, create project
- [ ] Login: `admin@authora.local` / `admin123` — change password

---

## Backup Cron

```bash
crontab -e
# Add: 0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

---

## Rollback (If Needed)

```bash
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy | `./scripts/deploy.sh prod` |
| Update | `./scripts/update.sh prod` |
| Backup | `./scripts/backup.sh` |
| Restore | `./scripts/restore.sh ./backups/authora_*.dump` |
| Rollback | `./scripts/rollback.sh ./backups/authora_*.dump prod` |
| Health | `./scripts/healthcheck.sh https://api.authora.studio` |
| Verify | `./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio https://app.authora.studio` |
