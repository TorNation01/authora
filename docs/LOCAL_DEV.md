# AUTHORA Local Development

Exact commands for running AUTHORA in development mode on your workstation.

## Prerequisites

- Node.js 18+
- Python 3.11+
- Docker (for PostgreSQL and Redis) — or local Postgres/Redis

## 1. Clone and Install

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
./scripts/install.sh
```

Or manual:

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
cp .env.example .env
npm install
pip install -e apps/api
```

## 2. Environment

```bash
# .env is created by install.sh. Default values work for local Docker:
# DATABASE_URL=postgresql://authora:authora@localhost:5432/authora
# REDIS_URL=redis://localhost:6379/0
# SECRET_KEY=dev-secret-change-in-production
```

Edit `.env` if using non-Docker Postgres/Redis.

## 3. Start Infrastructure

```bash
docker compose up -d postgres redis
```

Wait for PostgreSQL:
```bash
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done
```

## 4. Run Migrations

```bash
npm run db:migrate
```

Or with Docker:
```bash
./scripts/db-migrate.sh --docker
```

## 5. Seed Starter Data

```bash
npm run db:seed
```

Creates admin user: `admin@authora.local` / `admin123`

## 6. Start Application

**Terminal 1 – API:**
```bash
npm run dev:api
```
API: http://localhost:8000

**Terminal 2 – Web:**
```bash
npm run dev
```
Web: http://localhost:3000

## 7. Alternative: Full Stack in Docker

```bash
docker compose up -d --build
```

Then run migrations (first time only):
```bash
./scripts/db-migrate.sh --docker
./scripts/db-seed.sh --docker
```

Access: http://localhost:3000 (web), http://localhost:8000 (API)

## 8. Setup Wizard (Optional)

```bash
npm run setup
```

Interactive prompts for DATABASE_URL, REDIS_URL, SECRET_KEY, AI keys. Writes `.env`.

## 9. Verify Health

```bash
./scripts/healthcheck.sh http://localhost:8000
```

Or:
```bash
curl -sf http://localhost:8000/health
curl -sf http://localhost:8000/health/ready
```

## 10. Run Tests

```bash
npm run test:api
npm run test:e2e
```
