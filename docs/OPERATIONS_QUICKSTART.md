# AUTHORA Operations Quickstart

Copy-paste commands for common operations.

## Fresh Server → Live

```bash
# 1. Bootstrap Ubuntu
./scripts/bootstrap.sh
# Log out and back in (for Docker group)

# 2. Clone and install
git clone https://github.com/TorNation01/authora.git && cd authora
./scripts/install.sh

# 3. Configure
cp .env.example .env
nano .env  # Set SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL, DOMAIN_*

# 4. Validate and deploy
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh

# 5. First admin
./scripts/first-admin.sh --docker --prod
# Login: admin@authora.local / admin123
```

## Local Dev Start

```bash
cd authora
./scripts/install.sh
docker compose up -d postgres redis
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done
npm run db:migrate
npm run db:seed
npm run dev:api &   # Terminal 1
npm run dev         # Terminal 2
```

## Production Deploy

```bash
cd /path/to/authora
npm run deploy:prod
```

## Update Deploy

```bash
cd /path/to/authora
npm run update:prod
```

## Rollback

```bash
./scripts/rollback.sh ./backups/authora_20250315_020000.dump prod
```

## Backup

```bash
./scripts/backup.sh
```

## Restore

```bash
./scripts/restore.sh ./backups/authora_20250315_020000.dump
```

## Migrations

```bash
# Local
npm run db:migrate

# Docker prod
./scripts/db-migrate.sh --docker --prod
```

## Seed / First Admin

```bash
# Local
npm run db:seed

# Docker prod
./scripts/first-admin.sh --docker --prod
```

## Health Check

```bash
./scripts/healthcheck.sh http://localhost:8000
# Or production:
./scripts/healthcheck.sh https://api.authora.studio
```

## Go-Live Verification

```bash
./scripts/verify-go-live.sh https://api.authora.studio
```
