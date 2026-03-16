# AUTHORA Quickstart Commands

Copy-paste commands for common flows. Run from project root.

---

## Fresh Server → Live (5 steps)

```bash
# 1. Bootstrap Ubuntu
cd ~
git clone https://github.com/TorNation01/authora.git && cd authora
chmod +x scripts/*.sh
./scripts/bootstrap.sh
# Log out and back in (for Docker group)

# 2. Install
./scripts/install.sh

# 3. Configure
cp .env.example .env
nano .env   # Set SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL, DOMAIN_API, DOMAIN_WEB, ACME_EMAIL

# 4. Validate and deploy
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh

# 5. First admin
./scripts/first-admin.sh --docker --prod
# Login: admin@authora.local / admin123 — change password immediately
```

---

## Local Dev (one-time setup)

```bash
cd authora
./scripts/install.sh
docker compose up -d postgres redis
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done
npm run db:migrate
npm run db:seed
```

---

## Local Dev Start (every session)

```bash
cd authora
npm run dev:api &    # Terminal 1
npm run dev          # Terminal 2
```

API: http://localhost:8000 | Web: http://localhost:3000

---

## Local Dev (full Docker stack)

```bash
cd authora
docker compose up -d
```

---

## Production Deploy

```bash
cd /path/to/authora
./scripts/deploy.sh prod
```

---

## Update Production

```bash
cd /path/to/authora
./scripts/update.sh prod
```

---

## Backup

```bash
cd /path/to/authora
./scripts/backup.sh
```

---

## Restore

```bash
cd /path/to/authora
./scripts/restore.sh ./backups/authora_20250315_020000.dump
```

---

## Rollback Production

```bash
cd /path/to/authora
./scripts/rollback.sh ./backups/authora_20250315_020000.dump prod
```

---

## Health Check

```bash
./scripts/healthcheck.sh
# Or production: ./scripts/healthcheck.sh https://api.yourdomain.com
```

---

## Go-Live Verify

```bash
./scripts/verify-go-live.sh https://api.yourdomain.com https://app.yourdomain.com
```

---

## Migrations

```bash
# Local
npm run db:migrate

# Production Docker
./scripts/db-migrate.sh --docker --prod
```

---

## First Admin

```bash
# Local
./scripts/first-admin.sh

# Production
./scripts/first-admin.sh --docker --prod
```

---

## Setup Wizard

```bash
npm run setup
```
