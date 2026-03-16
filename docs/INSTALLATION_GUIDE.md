# AUTHORA Installation Guide

This guide walks through installing AUTHORA from scratch.

## Prerequisites

- **Docker** and **Docker Compose** (v2+)
- **Git**
- **Node.js 20** (for local dev; optional if using Docker only)
- **Python 3.11+** (for local dev; optional if using Docker only)

## Option 1: One-Command Bootstrap

For the fastest setup:

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
./scripts/bootstrap-one.sh
```

This will: clone (if needed), install deps, validate env, start Docker, migrate, seed, and run a health check. Visit http://localhost:3000/setup to complete the setup wizard.

See [ONE_COMMAND_BOOTSTRAP.md](ONE_COMMAND_BOOTSTRAP.md) for details.

## Option 2: Manual Installation

### 1. Clone the Repository

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

- `DATABASE_URL` – PostgreSQL connection string
- `REDIS_URL` – Redis connection string
- `SECRET_KEY` – Generate with `openssl rand -hex 32` for production

### 3. Install Dependencies

```bash
npm install
pip install -e apps/api
```

### 4. Start Infrastructure

```bash
docker compose up -d postgres redis
```

Wait for PostgreSQL to be ready:

```bash
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done
```

### 5. Run Migrations

```bash
./scripts/db-migrate.sh --docker
```

### 6. Seed Database (Optional)

```bash
./scripts/db-seed.sh --docker
```

### 7. Start Application

```bash
docker compose up -d
```

Or for local development:

```bash
npm run dev:api   # Terminal 1
npm run dev       # Terminal 2
```

### 8. Complete Setup

Visit http://localhost:3000/setup to run the setup wizard and create your first admin account.

## Environment Files by Deployment

| File | Use Case |
|------|----------|
| `.env.example` | General reference |
| `.env.development.example` | Local development |
| `.env.staging.example` | Staging deployment |
| `.env.production.example` | Production deployment |

Copy the appropriate example to `.env` and configure.

## Validation

Validate your environment before deploying:

```bash
source .env
./scripts/validate-env.sh development   # or staging, production
```

## Next Steps

- [FIRST_RUN_SETUP_WIZARD.md](FIRST_RUN_SETUP_WIZARD.md) – Setup wizard walkthrough
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) – Production deployment
