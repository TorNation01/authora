# Terminal Commands Reference

Quick reference for AUTHORA deployment and operations.

## Bootstrap & Install

| Command | Description |
|---------|-------------|
| `./scripts/bootstrap.sh` | Fresh Ubuntu: install Docker, Node, Python |
| `./scripts/bootstrap-one.sh [repo_url]` | One-command: clone → install → docker → migrate → seed → health |
| `./scripts/install.sh [repo_url]` | Install deps, create .env, prepare directories |
| `./scripts/bootstrap-prod.sh` | Production bootstrap (requires .env) |

## Docker

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start dev stack |
| `docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d` | Start staging |
| `docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d` | Start production |
| `docker compose down` | Stop all services |
| `docker compose logs -f api` | Follow API logs |
| `docker compose ps` | List running services |

## Database

| Command | Description |
|---------|-------------|
| `./scripts/db-migrate.sh` | Migrate (local) |
| `./scripts/db-migrate.sh --docker` | Migrate via Docker |
| `./scripts/db-migrate.sh --docker --prod` | Migrate (production) |
| `./scripts/db-seed.sh --docker` | Seed templates |
| `./scripts/backup.sh [dir]` | PostgreSQL backup |
| `./scripts/restore.sh <file>` | Restore from backup |

## Deployment

| Command | Description |
|---------|-------------|
| `./scripts/deploy.sh dev` | Deploy dev (infra + migrate) |
| `./scripts/deploy.sh prod` | Deploy production |
| `./scripts/update.sh [dev\|prod]` | Pull, rebuild, migrate, restart |

## Validation & Health

| Command | Description |
|---------|-------------|
| `./scripts/validate-env.sh [development\|staging\|production]` | Validate .env |
| `./scripts/healthcheck.sh [url]` | Health check (default: http://localhost:8000) |
| `./scripts/generate-caddyfile.sh` | Generate Caddyfile from .env |

## Development

| Command | Description |
|---------|-------------|
| `npm run dev` | Start Next.js dev server |
| `npm run dev:api` | Start FastAPI dev server |
| `npm run db:migrate` | Run migrations (via package.json) |
| `npm run db:seed` | Seed database |
| `npm run setup` | Run setup wizard (CLI) |
