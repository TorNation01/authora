# AUTHORA Deployment – Final Summary

## Deployment Architecture

```
                    ┌─────────────┐
                    │   Caddy     │ 80/443
                    │ (TLS, proxy)│
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
       ┌──────▼──────┐           ┌─────▼─────┐
       │  Next.js    │           │  FastAPI   │
       │  (web:3000) │           │ (api:8000) │
       └─────────────┘           └─────┬──────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
             ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
             │ PostgreSQL  │    │   Redis     │    │   Storage   │
             │  (5432)     │    │  (6379)     │    │  (volume)   │
             └─────────────┘    └─────────────┘    └─────────────┘
```

## Exact Install and Deploy Commands

### Fresh Ubuntu Server

```bash
# 1. Bootstrap (Docker, Node, Python)
curl -fsSL https://raw.githubusercontent.com/TorNation01/authora/main/scripts/bootstrap.sh -o /tmp/bootstrap.sh
chmod +x /tmp/bootstrap.sh && /tmp/bootstrap.sh
# Log out and back in

# 2. Clone and install
git clone https://github.com/TorNation01/authora.git
cd authora
chmod +x scripts/*.sh
./scripts/install.sh

# 3. Configure
cp .env.example .env
nano .env
# Set: SECRET_KEY=$(openssl rand -hex 32)
#      DATABASE_URL=postgresql://authora:YOUR_PASSWORD@postgres:5432/authora
#      REDIS_URL=redis://redis:6379/0
#      NEXT_PUBLIC_API_URL=https://api.authora.studio
#      DOMAIN_API=api.authora.studio
#      DOMAIN_WEB=authora.studio
#      ACME_EMAIL=admin@authora.studio

# 4. Generate Caddyfile
./scripts/generate-caddyfile.sh

# 5. Validate and deploy
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh

# 6. First admin
./scripts/first-admin.sh --docker --prod
# Login: admin@authora.local / admin123
```

### One-Command Production Deploy (after install)

```bash
cd /path/to/authora
npm run deploy:prod
```

## Exact Update and Rollback Commands

### Update

```bash
cd /path/to/authora
npm run update:prod
```

Or manually:
```bash
git pull --rebase
source .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres redis
sleep 5
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm -e DATABASE_URL="$DATABASE_URL" api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Rollback

```bash
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
```

## Exact Backup and Restore Commands

### Backup

```bash
./scripts/backup.sh
# Output: ./backups/authora_YYYYMMDD_HHMMSS.dump
```

### Restore

```bash
./scripts/restore.sh ./backups/authora_20250315_020000.dump
```

## Exact First Admin Creation

```bash
./scripts/first-admin.sh --docker --prod
```

Default: `admin@authora.local` / `admin123` — change immediately.

## Post-Deploy Validation Checklist

- [ ] `curl -sf https://api.authora.studio/health` → `{"status":"ok"}`
- [ ] `curl -sf https://api.authora.studio/health/ready` → `{"status":"ready"}`
- [ ] Open https://authora.studio — login/register works
- [ ] Create project, create book — no errors
- [ ] `./scripts/verify-go-live.sh https://api.authora.studio` passes

## Go-Live Checklist

See [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md).

## Known Manual Steps

1. **DNS:** Create A records for DOMAIN_API and DOMAIN_WEB pointing to server IP
2. **SECRET_KEY:** Must be changed from default (run `openssl rand -hex 32`)
3. **Cron (reminders):** Add hourly cron for `/api/v1/accountability/cron/reminders` with `X-Cron-Secret`
4. **Backup cron:** Add daily `./scripts/backup.sh` to crontab
