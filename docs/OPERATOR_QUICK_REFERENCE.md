# AUTHORA Operator Quick Reference

Exact terminal commands for this project. Run from project root unless noted.

---

## Fresh Ubuntu Bootstrap

On a fresh Ubuntu 22.04/24.04 server (requires `git` — install with `sudo apt update && sudo apt install -y git` if needed):

```bash
cd ~
git clone https://github.com/TorNation01/authora.git
cd authora
./scripts/bootstrap.sh
```

Installs Docker, Docker Compose, Node 20, Python. Log out and back in if Docker was just installed (for `docker` without sudo).

---

## Repo Clone

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
```

---

## Install (after clone)

```bash
cd authora
./scripts/install.sh
```

Creates `.env` from `.env.example` if missing, installs Node and API deps. Idempotent.

---

## Env Setup

```bash
cd authora
cp .env.example .env
nano .env   # Set SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL
```

Validate before production:

```bash
source .env && ./scripts/validate-env.sh production
```

---

## Local Dev Start

**Option A: Infra + npm (recommended)**

```bash
cd authora
docker compose up -d postgres redis
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done
npm run db:migrate
npm run db:seed
npm run dev:api &    # Terminal 1: API on http://localhost:8000
npm run dev          # Terminal 2: Web on http://localhost:3000
```

**Option B: One-command deploy then start**

```bash
cd authora
./scripts/deploy.sh
npm run dev:api &
npm run dev
```

---

## Local Production-Like Start (Docker full stack)

```bash
cd authora
cp .env.example .env
# Edit .env: SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL
source .env && ./scripts/validate-env.sh production
docker compose up -d
```

- Web: http://localhost:3000
- API: http://localhost:8000

---

## Production Deploy

```bash
cd authora
# Ensure .env is configured
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh
```

Or deploy only (when bootstrap already done):

```bash
cd authora
./scripts/deploy.sh prod
```

---

## Update Deploy

```bash
cd authora
./scripts/update.sh prod
```

For dev:

```bash
./scripts/update.sh
```

---

## Rollback Deploy

```bash
cd authora
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
```

For dev:

```bash
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump
```

---

## Migrations

**Local (PostgreSQL on localhost):**

```bash
cd authora
npm run db:migrate
```

**Via Docker:**

```bash
cd authora
npm run db:migrate:docker
```

**Production (with prod compose):**

```bash
cd authora
./scripts/db-migrate.sh --docker --prod
```

---

## Seed

**Local:**

```bash
cd authora
npm run db:seed
```

**Via Docker:**

```bash
cd authora
npm run db:seed:docker
```

**Production:**

```bash
cd authora
./scripts/db-seed.sh --docker --prod
```

---

## First Admin Creation

**Local:**

```bash
cd authora
./scripts/first-admin.sh
```

**Production (Docker):**

```bash
cd authora
./scripts/first-admin.sh --docker --prod
```

Default: `admin@authora.local` / `admin123` — change password after first login.

---

## Health Checks

**Local default (http://localhost:8000):**

```bash
cd authora
./scripts/healthcheck.sh
```

**Production API URL:**

```bash
./scripts/healthcheck.sh https://api.authora.studio
```

**Via npm:**

```bash
npm run healthcheck
```

---

## Backup

**Default output (./backups/):**

```bash
cd authora
./scripts/backup.sh
```

**Custom output directory:**

```bash
./scripts/backup.sh /path/to/backups
```

Output: `./backups/authora_YYYYMMDD_HHMMSS.dump`

**Via npm:**

```bash
npm run backup
```

---

## Restore

```bash
cd authora
./scripts/restore.sh ./backups/authora_YYYYMMDD_HHMMSS.dump
```

Stop API/web first for production. After restore, restart services and run migrations if needed.

---

## Setup Wizard Launch

```bash
cd authora
npm run setup
```

Interactive wizard for DATABASE_URL, Redis, SECRET_KEY, AI keys.

---

## Go-Live Verification

**Local:**

```bash
cd authora
./scripts/verify-go-live.sh
```

**Production:**

```bash
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio
```

Second arg (web URL) is optional; used for CORS check.

---

## Quick Reference Table

| Task | Command |
|------|---------|
| Fresh Ubuntu bootstrap | `./scripts/bootstrap.sh` |
| Clone repo | `git clone https://github.com/TorNation01/authora.git && cd authora` |
| Install | `./scripts/install.sh` |
| Env setup | `cp .env.example .env && nano .env` |
| Validate env (prod) | `source .env && ./scripts/validate-env.sh production` |
| Local dev start | `docker compose up -d postgres redis` then `npm run db:migrate` then `npm run dev:api &` and `npm run dev` |
| Local prod-like | `docker compose up -d` |
| Production deploy | `./scripts/deploy.sh prod` |
| Production bootstrap | `./scripts/bootstrap-prod.sh` |
| Update deploy | `./scripts/update.sh prod` |
| Rollback | `./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod` |
| Migrations (local) | `npm run db:migrate` |
| Migrations (Docker prod) | `./scripts/db-migrate.sh --docker --prod` |
| Seed (local) | `npm run db:seed` |
| Seed (Docker prod) | `./scripts/db-seed.sh --docker --prod` |
| First admin (local) | `./scripts/first-admin.sh` |
| First admin (prod) | `./scripts/first-admin.sh --docker --prod` |
| Health check | `./scripts/healthcheck.sh [base_url]` |
| Backup | `./scripts/backup.sh [output_dir]` |
| Restore | `./scripts/restore.sh <backup_file.dump>` |
| Setup wizard | `npm run setup` |
| Go-live verify | `./scripts/verify-go-live.sh [api_url] [web_url]` |

---

## Cron (Production)

```cron
# Reminders (hourly)
0 * * * * cd /path/to/authora && curl -X POST -H "X-Cron-Secret: YOUR_CRON_SECRET" https://api.authora.studio/api/v1/accountability/cron/reminders

# Backup (daily 2am)
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```
