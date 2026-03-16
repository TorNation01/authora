# AUTHORA Deployment Guide

## Deployment Architecture Summary

| Layer | Component | Port | Notes |
|-------|-----------|------|-------|
| Reverse proxy | Caddy | 80, 443 | TLS termination, Let's Encrypt |
| API | FastAPI (uvicorn) | 8000 (internal) | Behind Caddy |
| Web | Next.js | 3000 (internal) | Behind Caddy |
| Database | PostgreSQL 16 | 5432 (internal) | Docker volume |
| Cache | Redis 7 | 6379 (internal) | Docker volume |
| Storage | Local / R2 | - | File uploads, exports |

**Modes:**
- **Standalone:** Single-server Docker Compose (default)
- **Anakatech-integrated:** Future; same API, different auth/tenant model

## Related Documentation

- **[DEPLOY_QUICKSTART](DEPLOY_QUICKSTART.md)** – One-command deploy (clone → copy env → deploy → setup wizard)
- **[UBUNTU_COMMAND_PACK](UBUNTU_COMMAND_PACK.md)** – Copy-paste terminal commands for Ubuntu
- **[UBUNTU_SERVER_DEPLOYMENT](UBUNTU_SERVER_DEPLOYMENT.md)** – Launch-ready Ubuntu deployment path
- **[OPERATIONS_QUICKSTART](OPERATIONS_QUICKSTART.md)** – Copy-paste commands
- **[Exact Commands](DEPLOYMENT-COMMANDS.md)** – Full command reference
- [UBUNTU_INSTALL](UBUNTU_INSTALL.md) – Fresh Ubuntu bootstrap
- [LOCAL_DEV](LOCAL_DEV.md) – Local development
- [GO_LIVE_CHECKLIST](GO_LIVE_CHECKLIST.md) – Pre/post go-live
- [BACKUP_AND_RESTORE](BACKUP_AND_RESTORE.md) – Backup and restore
- [Cloudflare Deployment](DEPLOYMENT-CLOUDFLARE.md) – Deploy behind Cloudflare
- [SSL & Domain Setup](DEPLOYMENT-SSL-DOMAIN.md) – TLS/HTTPS and DNS
- [Billing Deployment](BILLING_DEPLOYMENT.md) – Stripe, tiers, promo codes, subscriptions
- [QA Strategy](QA_STRATEGY.md) – Test strategy, coverage
- [Release Gates](RELEASE_GATES.md) – Pre-launch gates
- [Production Readiness Report](PRODUCTION_READINESS_REPORT.md) – Readiness assessment

## Quick Start (Development)

```bash
# One-command deploy (clone → copy env → deploy)
git clone https://github.com/TorNation01/authora.git && cd authora && cp .env.example .env && ./scripts/deploy.sh

# Then complete setup wizard at http://localhost:3000/setup
```

Or from an existing clone:

```bash
./scripts/deploy.sh
# or
npm run deploy
```

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local dev)
- Python 3.11+ (for local dev)

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `REDIS_URL` | Yes | Redis connection string |
| `SECRET_KEY` | Yes | JWT signing key (use `openssl rand -hex 32` in prod) |
| `NEXT_PUBLIC_API_URL` | Prod | Public API URL for the frontend |
| `OPENAI_API_KEY` | No | AI features (optional) |
| `ANTHROPIC_API_KEY` | No | AI features (optional) |

Validate before production:

```bash
source .env && ./scripts/validate-env.sh production
```

## Docker Compose

### Development (`docker-compose.yml`)

- PostgreSQL on 5432, Redis on 6379
- API on 8000, Web on 3000
- Volumes for postgres and redis data
- Healthchecks on all services

### Production (`docker-compose.prod.yml`)

Overrides for production:

- `restart: unless-stopped` on all services
- No host port exposure (internal network only)
- Caddy reverse proxy for TLS termination
- Secrets from environment

```bash
# Production deploy
./scripts/validate-env.sh production
./scripts/deploy.sh prod
```

## Caddy Reverse Proxy

Edit `caddy/Caddyfile` with your domains:

```
api.authora.studio {
    reverse_proxy api:8000
}

authora.studio {
    reverse_proxy web:3000
}
```

Caddy auto-provisions TLS via Let's Encrypt.

## Backup & Restore

### Backup

```bash
./scripts/backup.sh [output_dir]
# Default: ./backups/authora_YYYYMMDD_HHMMSS.dump
```

### Restore

```bash
./scripts/restore.sh ./backups/authora_20250115_020000.dump
```

### Rollback (restore + restart)

```bash
./scripts/rollback.sh ./backups/authora_20250115_020000.dump prod
```

## Update & Rollback

### Update (pull, rebuild, migrate)

```bash
./scripts/update.sh [dev|prod]
```

### Rollback (restore from backup)

```bash
./scripts/rollback.sh <backup_file> [dev|prod]
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `validate-env.sh [mode]` | Validate required env vars |
| `deploy.sh [dev\|prod]` | One-command deploy |
| `update.sh [dev\|prod]` | Pull, rebuild, migrate |
| `rollback.sh <backup> [mode]` | Restore backup and restart |
| `backup.sh [dir]` | PostgreSQL backup |
| `restore.sh <file>` | PostgreSQL restore |

## Health Checks

- **API liveness**: `GET /health` → `{"status":"ok"}`
- **API readiness**: `GET /health/ready` → `{"status":"ready","checks":{"database":true,"redis":true}}` (503 if degraded)
- **Web**: Root path returns 200
- **PostgreSQL**: `pg_isready -U authora`
- **Redis**: `redis-cli ping`

## Cron Jobs

### Reminders (Accountability)

The accountability engine sends daily, weekly, milestone, streak, overdue, finish-date risk, resume, and chapter-target reminders. Call the cron endpoint from a scheduler (e.g., system cron, Cloudflare Workers Cron, or Kubernetes CronJob).

**Endpoint:** `POST /api/v1/accountability/cron/reminders`

**Recommended schedule:**
- Run every hour so daily reminders are sent at users' configured times (timezone-aware)
- Weekly reminders are processed when the job runs on Monday
- Respects user quiet hours and reminder type preferences

**Example (system cron):**
```bash
# Every hour (when CRON_SECRET is set, include the header)
0 * * * * curl -X POST http://localhost:8000/api/v1/accountability/cron/reminders \
  -H "Content-Type: application/json" \
  -H "X-Cron-Secret: $CRON_SECRET"
```

**Security:** When `CRON_SECRET` is set in the API environment, the endpoint requires the `X-Cron-Secret` header to match. Set `CRON_SECRET` in production (e.g. `openssl rand -hex 32`) and pass it in the cron job. If `CRON_SECRET` is not set, the endpoint remains open (backward compatible; not recommended for production).

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `bootstrap.sh` | Fresh Ubuntu: Docker, Node, Python |
| `install.sh` | Clone/setup: .env, deps, Caddyfile |
| `bootstrap-dev.sh` | Local dev: deps, infra, migrations |
| `bootstrap-prod.sh` | Production: validate, build, migrate, start |
| `deploy.sh [dev\|prod]` | One-command deploy |
| `update.sh [dev\|prod]` | Pull, rebuild, migrate, restart |
| `rollback.sh <backup> [mode]` | Restore backup and restart |
| `backup.sh [dir]` | PostgreSQL backup |
| `restore.sh <file>` | PostgreSQL restore |
| `healthcheck.sh [url]` | Health verification |
| `first-admin.sh [--docker] [--prod]` | Create admin user |
| `verify-go-live.sh [url]` | Go-live validation |
| `validate-env.sh [mode]` | Validate required env vars |

## Security Notes

1. Change `SECRET_KEY` in production
2. Use strong PostgreSQL password
3. Do not expose postgres/redis ports in production
4. Keep Caddyfile and `.env` out of version control (`.env` is gitignored)
