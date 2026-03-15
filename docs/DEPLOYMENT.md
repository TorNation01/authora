# AUTHORA Deployment Guide

## Related Documentation

- [Cloudflare Deployment](CLOUDFLARE-DEPLOYMENT.md) – Deploy behind Cloudflare
- [SSL Configuration](SSL.md) – TLS/HTTPS setup
- [Server Sizing](SERVER-SIZING.md) – Resource requirements
- [Monitoring](MONITORING.md) – Health checks and metrics
- [Logging](LOGGING.md) – Log configuration
- [Incident Recovery](INCIDENT-RECOVERY.md) – Runbooks

## Quick Start (Development)

```bash
# One-command dev setup
./scripts/deploy.sh dev

# Then start the app
npm run dev:api   # Backend on http://localhost:8000
npm run dev       # Frontend on http://localhost:3000

# Or run full stack in Docker
docker compose up -d
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
api.yourdomain.com {
    reverse_proxy api:8000
}

app.yourdomain.com {
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

## Bootstrap Scripts

- **Local dev**: `./scripts/bootstrap-dev.sh` – install deps, start infra, run migrations
- **Production**: `./scripts/bootstrap-prod.sh` – validate env, build, migrate, start stack

## Security Notes

1. Change `SECRET_KEY` in production
2. Use strong PostgreSQL password
3. Do not expose postgres/redis ports in production
4. Keep Caddyfile and `.env` out of version control (`.env` is gitignored)
