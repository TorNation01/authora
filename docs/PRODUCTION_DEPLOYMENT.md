# Production Deployment

This guide covers deploying AUTHORA to production with Docker and Caddy.

## Prerequisites

- Server with Docker and Docker Compose
- Domain(s) pointed to your server
- SSL certificates (Caddy obtains these automatically via Let's Encrypt)

## 1. Prepare Environment

```bash
cp .env.production.example .env
```

Edit `.env` and set:

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | `openssl rand -hex 32` |
| `DATABASE_URL` | Yes | PostgreSQL connection |
| `REDIS_URL` | Yes | Redis connection |
| `NEXT_PUBLIC_API_URL` | Yes | e.g. `https://api.yourdomain.com` |
| `NEXT_PUBLIC_MARKETING_URL` | No | e.g. `https://yourdomain.com` |
| `NEXT_PUBLIC_APP_URL` | No | e.g. `https://app.yourdomain.com` |
| `DOMAIN_API` | Yes* | For Caddy |
| `DOMAIN_MARKETING` | Yes* | For Caddy |
| `DOMAIN_APP` | Yes* | For Caddy |
| `ACME_EMAIL` | Yes* | For Let's Encrypt |

\* Required when using `generate-caddyfile.sh`

## 2. Generate Caddyfile

```bash
./scripts/generate-caddyfile.sh
```

This creates `caddy/Caddyfile` from your `.env` domain variables.

## 3. Validate Environment

```bash
source .env
./scripts/validate-env.sh production
```

## 4. Bootstrap (First Deploy)

```bash
./scripts/bootstrap-prod.sh
```

Or manually:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres redis
# Wait for PostgreSQL
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm -e DATABASE_URL="${DATABASE_URL}" api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d
```

## 5. Complete Setup Wizard

Visit `https://your-domain/setup` and complete the wizard to create your first admin account.

## 6. Post-Deployment

### Backup Cron

```bash
# Add to crontab: daily at 2 AM
0 2 * * * /path/to/authora/scripts/backup.sh
```

### Health Monitoring

```bash
./scripts/healthcheck.sh https://api.yourdomain.com
```

### Updates

```bash
./scripts/update.sh prod
```

## Architecture

Production uses:

- **Caddy** – Reverse proxy, automatic SSL, secure headers, gzip, WebSocket support
- **No exposed ports** – PostgreSQL and Redis are internal only
- **Restart policy** – `unless-stopped` for all services

## See Also

- [DOMAIN_AND_SSL.md](DOMAIN_AND_SSL.md) – Domain and SSL details
- [BACKUPS_AND_RESTORE.md](BACKUPS_AND_RESTORE.md) – Backup procedures
- [SECURITY_HARDENING.md](SECURITY_HARDENING.md) – Security recommendations
