# AUTHORA Deployment – Exact Commands

Copy-paste commands for local development, production deployment, and operations.

---

## Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **Docker** and **Docker Compose** (for containerized runs)
- **PostgreSQL** 16+ (or Docker)
- **Redis** 7+ (or Docker)

---

## 1. Local Development Boot

### One-command bootstrap (recommended)

```bash
cd /path/to/authora
npm run bootstrap:dev
```

Then start the app:

```bash
npm run dev:api    # Terminal 1: API on http://localhost:8000
npm run dev        # Terminal 2: Web on http://localhost:3000
```

### Manual steps (if bootstrap fails)

```bash
cd /path/to/authora

# Create .env
cp .env.example .env
# Edit .env: DATABASE_URL, REDIS_URL, SECRET_KEY

# Install deps
npm install
pip install -e apps/api

# Start infra (Docker)
docker compose up -d postgres redis

# Wait for Postgres
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done

# Migrate
npm run db:migrate

# Start app
npm run dev:api &
npm run dev
```

---

## 2. Local Production-Like Boot (Docker full stack)

```bash
cd /path/to/authora

# Ensure .env exists
cp .env.example .env
# Edit .env: SECRET_KEY, CORS_ORIGINS, NEXT_PUBLIC_API_URL=http://localhost:8000

# Build and run full stack (postgres, redis, api, web)
docker compose up -d --build

# Run migrations (first time)
docker compose run --rm -e DATABASE_URL="postgresql://authora:authora@postgres:5432/authora" api alembic upgrade head

# Seed admin (optional)
docker compose run --rm -e DATABASE_URL="postgresql://authora:authora@postgres:5432/authora" -e REDIS_URL="redis://redis:6379/0" -e SECRET_KEY="your-secret" api python -m authora.scripts.seed
```

Access: http://localhost:3000 (web), http://localhost:8000 (API)

---

## 3. Ubuntu Server Deployment

### Initial setup (one-time)

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in

# Clone repo
git clone https://github.com/your-org/authora.git
cd authora

# Create .env
cp .env.example .env
nano .env
# Set: SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL, DOMAIN_API, DOMAIN_WEB, ACME_EMAIL

# Validate env
source .env && ./scripts/validate-env.sh production

# Bootstrap production
npm run bootstrap:prod
```

### First deploy

```bash
cd /path/to/authora
npm run deploy:prod
```

### Create first admin (after deploy)

```bash
cd /path/to/authora
source .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm \
  -e DATABASE_URL="$DATABASE_URL" -e REDIS_URL="$REDIS_URL" -e SECRET_KEY="$SECRET_KEY" \
  api python -m authora.scripts.seed
```

Default admin: `admin@authora.local` / `admin123` — change immediately.

---

## 4. Update Deployment

```bash
cd /path/to/authora
npm run update:prod
```

Or manually:

```bash
cd /path/to/authora
git pull --rebase
source .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d postgres redis
sleep 3
docker compose -f docker-compose.yml -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm -e DATABASE_URL="$DATABASE_URL" api alembic upgrade head
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 5. Rollback Deployment

```bash
cd /path/to/authora
./scripts/rollback.sh ./backups/authora_YYYYMMDD_HHMMSS.dump prod
```

Example:

```bash
./scripts/rollback.sh ./backups/authora_20250315_020000.dump prod
```

---

## 6. Database Migration Run

### Local (no Docker)

```bash
cd /path/to/authora
source .env
cd apps/api && alembic upgrade head && cd ../..
```

Or:

```bash
npm run db:migrate
```

### With Docker (dev)

```bash
cd /path/to/authora
npm run db:migrate:docker
```

Or:

```bash
./scripts/db-migrate.sh --docker
```

### With Docker (prod)

```bash
cd /path/to/authora
source .env
./scripts/db-migrate.sh --docker --prod
```

---

## 7. Seed Run

### Local (no Docker)

```bash
cd /path/to/authora
npm run db:seed
```

### With Docker (dev)

```bash
./scripts/db-seed.sh --docker
```

### With Docker (prod)

```bash
cd /path/to/authora
source .env
./scripts/db-seed.sh --docker --prod
```

---

## 8. First Admin Creation

### Via seed script (creates admin@authora.local)

```bash
# Local
npm run db:seed

# Docker prod
source .env
docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm \
  -e DATABASE_URL="$DATABASE_URL" -e REDIS_URL="$REDIS_URL" -e SECRET_KEY="$SECRET_KEY" \
  api python -m authora.scripts.seed
```

### Via setup wizard (standalone)

1. Visit `https://your-domain/setup`
2. Complete wizard (DB, Redis, AI, email, admin)
3. Admin created at final step

---

## 9. Health Verification

### Quick check

```bash
curl -sf http://localhost:8000/health
curl -sf http://localhost:8000/health/ready
```

### Via npm

```bash
npm run health
```

### Production (via domain)

```bash
curl -sf https://api.authora.studio/health
curl -sf https://api.authora.studio/health/ready
```

Expected: `{"status":"ok"}` and `{"status":"ready","checks":{...}}`

---

## 10. Backup Run

```bash
cd /path/to/authora
npm run backup
```

Or with custom output dir:

```bash
./scripts/backup.sh /path/to/backups
```

Output: `./backups/authora_YYYYMMDD_HHMMSS.dump`

### Cron (daily 2am)

```cron
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

---

## 11. Restore Run

```bash
cd /path/to/authora
./scripts/restore.sh ./backups/authora_20250315_020000.dump
```

Or via npm (pass path after --):

```bash
npm run restore -- ./backups/authora_20250315_020000.dump
```

**Warning:** Overwrites database. Stop API/web first (or use rollback script).

---

## 12. Generate Caddyfile from .env

```bash
cd /path/to/authora
# Ensure .env has DOMAIN_API, DOMAIN_WEB, ACME_EMAIL
./scripts/generate-caddyfile.sh
```

---

## 13. Validate Environment

```bash
cd /path/to/authora
source .env
./scripts/validate-env.sh standalone   # dev
./scripts/validate-env.sh production  # prod
```
