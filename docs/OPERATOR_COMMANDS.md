# AUTHORA Operator Commands

Exact terminal commands for this project. Run from project root (`/path/to/authora`) unless noted.

---

## Fresh Ubuntu Bootstrap

On Ubuntu 22.04/24.04 (install git first if needed: `sudo apt update && sudo apt install -y git`):

```bash
cd ~
git clone https://github.com/TorNation01/authora.git
cd authora
chmod +x scripts/*.sh
./scripts/bootstrap.sh
```

Or with bootstrap script only (repo already cloned):

```bash
cd /path/to/authora
./scripts/bootstrap.sh
```

Installs: Docker, Docker Compose plugin, Node.js 20, Python 3, base apt packages. **Log out and back in** after Docker install for group membership.

---

## Package Installation

```bash
cd /path/to/authora
./scripts/install.sh
```

Creates `.env` from `.env.example` if missing, runs `npm install`, `pip install -e apps/api`, creates `backups`, `storage`, `caddy` dirs. Idempotent.

---

## Docker Install (Manual)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in
```

---

## Docker Compose Install (Manual)

```bash
sudo apt-get install -y docker-compose-plugin
```

---

## Repo Clone

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
```

---

## Working Directory Setup

```bash
cd /path/to/authora
chmod +x scripts/*.sh
mkdir -p backups storage caddy
```

---

## Environment File Creation

```bash
cd /path/to/authora
cp .env.example .env
nano .env
```

Required: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`. Production: also `NEXT_PUBLIC_API_URL`, `DOMAIN_API`, `DOMAIN_WEB`, `ACME_EMAIL`.

Generate SECRET_KEY: `openssl rand -hex 32`

Validate production env:

```bash
source .env && ./scripts/validate-env.sh production
```

---

## Migrations

**Local (PostgreSQL on localhost):**

```bash
cd /path/to/authora
npm run db:migrate
```

**Via Docker (dev compose):**

```bash
cd /path/to/authora
./scripts/db-migrate.sh --docker
```

**Production (prod compose):**

```bash
cd /path/to/authora
./scripts/db-migrate.sh --docker --prod
```

---

## Seed

**Local:**

```bash
cd /path/to/authora
npm run db:seed
```

**Via Docker (dev):**

```bash
cd /path/to/authora
./scripts/db-seed.sh --docker
```

**Production:**

```bash
cd /path/to/authora
./scripts/db-seed.sh --docker --prod
```

---

## Local Dev Start

**Option A: Infra + npm**

```bash
cd /path/to/authora
docker compose up -d postgres redis
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done
npm run db:migrate
npm run db:seed
npm run dev:api &    # Terminal 1: API on http://localhost:8000
npm run dev          # Terminal 2: Web on http://localhost:3000
```

**Option B: Deploy script then npm**

```bash
cd /path/to/authora
./scripts/deploy.sh
npm run dev:api &
npm run dev
```

---

## Local Production-Like Start (Full Docker Stack)

```bash
cd /path/to/authora
docker compose up -d
```

- API: http://localhost:8000
- Web: http://localhost:3000
- Postgres: localhost:5432, Redis: localhost:6379

---

## Setup Wizard Launch

```bash
cd /path/to/authora
npm run setup
```

Interactive CLI for DATABASE_URL, Redis, SECRET_KEY, AI keys. Writes to `.env`.

---

## First Admin Creation

**Local:**

```bash
cd /path/to/authora
./scripts/first-admin.sh
```

**Production (Docker):**

```bash
cd /path/to/authora
./scripts/first-admin.sh --docker --prod
```

Default: `admin@authora.local` / `admin123` — change password after first login.

---

## Production Deploy

**Full bootstrap (first time):**

```bash
cd /path/to/authora
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh
```

**Deploy only (bootstrap already done):**

```bash
cd /path/to/authora
./scripts/deploy.sh prod
```

Or via npm: `npm run deploy:prod`

---

## Reverse Proxy Startup (Caddy)

Caddy is started automatically by production compose. To generate Caddyfile first:

```bash
cd /path/to/authora
./scripts/generate-caddyfile.sh
```

Requires `.env` with `DOMAIN_API`, `DOMAIN_WEB`, `ACME_EMAIL`. Output: `caddy/Caddyfile`.

Production stack includes Caddy:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Health Checks

**Local default (http://localhost:8000):**

```bash
cd /path/to/authora
./scripts/healthcheck.sh
```

**Production API URL:**

```bash
./scripts/healthcheck.sh https://api.yourdomain.com
```

**Via npm:**

```bash
npm run healthcheck
```

**Manual curl:**

```bash
curl -sf http://localhost:8000/health
curl -sf http://localhost:8000/health/ready
```

---

## Go-Live Verification

**Local:**

```bash
cd /path/to/authora
./scripts/verify-go-live.sh
```

**Production (API + Web URLs):**

```bash
./scripts/verify-go-live.sh https://api.yourdomain.com https://app.yourdomain.com
```

---

## Update Deployment

**Dev:**

```bash
cd /path/to/authora
./scripts/update.sh
```

**Production:**

```bash
cd /path/to/authora
./scripts/update.sh prod
```

Or: `npm run update:prod`

---

## Rollback Deployment

**Dev:**

```bash
cd /path/to/authora
./scripts/rollback.sh ./backups/authora_20250315_020000.dump
```

**Production:**

```bash
cd /path/to/authora
./scripts/rollback.sh ./backups/authora_20250315_020000.dump prod
```

---

## Backup

**Default output (./backups/):**

```bash
cd /path/to/authora
./scripts/backup.sh
```

**Custom output directory:**

```bash
./scripts/backup.sh /path/to/backups
```

Output: `./backups/authora_YYYYMMDD_HHMMSS.dump`

---

## Restore

```bash
cd /path/to/authora
./scripts/restore.sh ./backups/authora_20250315_020000.dump
```

Stop API/web first for production. After restore: restart services, optionally run migrations.

---

## Logs Inspection

**Dev compose:**

```bash
cd /path/to/authora
docker compose logs -f api
docker compose logs -f web
docker compose logs -f postgres
docker compose logs -f redis
docker compose logs -f
```

**Production compose:**

```bash
cd /path/to/authora
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f caddy
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

**Last N lines:**

```bash
docker compose logs --tail=100 api
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=100 api
```

---

## Service Restart

**Dev compose:**

```bash
cd /path/to/authora
docker compose restart api
docker compose restart api web
docker compose restart
```

**Production compose:**

```bash
cd /path/to/authora
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart api
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart api web caddy
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart
```

---

## Service Stop / Start

**Dev compose:**

```bash
cd /path/to/authora
docker compose stop api web
docker compose start api web
docker compose down
docker compose up -d
```

**Production compose:**

```bash
cd /path/to/authora
docker compose -f docker-compose.yml -f docker-compose.prod.yml stop api web caddy
docker compose -f docker-compose.yml -f docker-compose.prod.yml start api web caddy
docker compose -f docker-compose.yml -f docker-compose.prod.yml down
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Status Checks

**Dev compose:**

```bash
cd /path/to/authora
docker compose ps
```

**Production compose:**

```bash
cd /path/to/authora
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

**API health:**

```bash
curl -s http://localhost:8000/health | jq
curl -s http://localhost:8000/health/ready | jq
```

---

## Compose File Reference

| Environment | Compose Files |
|-------------|---------------|
| Dev | `docker-compose.yml` |
| Production | `docker-compose.yml` + `docker-compose.prod.yml` |

**Dev:** `docker compose up -d`  
**Prod:** `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

---

## Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/install.sh` | Repo install, deps, .env |
| `scripts/bootstrap.sh` | Fresh Ubuntu bootstrap |
| `scripts/bootstrap-dev.sh` | Local dev bootstrap |
| `scripts/bootstrap-prod.sh` | Production bootstrap |
| `scripts/deploy.sh [dev\|prod]` | One-command deploy |
| `scripts/validate-env.sh [standalone\|production]` | Env validation |
| `scripts/db-migrate.sh [--docker] [--prod]` | Migrations |
| `scripts/db-seed.sh [--docker] [--prod]` | Seed |
| `scripts/first-admin.sh [--docker] [--prod]` | First admin |
| `scripts/backup.sh [output_dir]` | PostgreSQL backup |
| `scripts/restore.sh <file.dump>` | PostgreSQL restore |
| `scripts/rollback.sh <file.dump> [dev\|prod]` | Restore + restart |
| `scripts/update.sh [dev\|prod]` | Pull, rebuild, migrate, restart |
| `scripts/healthcheck.sh [base_url]` | Health verification |
| `scripts/verify-go-live.sh [api_url] [web_url]` | Go-live checks |
| `scripts/generate-caddyfile.sh` | Generate caddy/Caddyfile |
