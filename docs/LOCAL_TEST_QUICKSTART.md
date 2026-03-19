# AUTHORA Local Testing Quickstart

## URLs

| Service | URL |
|---------|-----|
| **Website (app)** | http://localhost:3031 |
| **Login** | http://localhost:3031/login |
| **Register** | http://localhost:3031/register |
| **Admin panel** | http://localhost:3031/dashboard/admin |
| **Templates** | http://localhost:3031/dashboard/templates |
| **New project** | http://localhost:3031/dashboard/projects/new |
| **API** | http://localhost:8000 |
| **API health** | http://localhost:8000/health |
| **API docs** | http://localhost:8000/api/docs |

## Start Everything

```powershell
cd e:\anakatech-legal-collective\authora

# 1. Start PostgreSQL + Redis + API
docker compose up -d postgres redis api

# 2. Run migrations (first time only)
docker compose run --rm -e DATABASE_URL="postgresql://authora:authora@postgres:5432/authora" api alembic upgrade head

# 3. Seed users + templates + frameworks (first time only)
docker compose run --rm -e DATABASE_URL="postgresql://authora:authora@postgres:5432/authora" -e REDIS_URL="redis://redis:6379/0" -e SECRET_KEY="dev-secret" api python -m authora.scripts.seed

# 4. Start web app (separate terminal)
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"; npm run dev
```

Web runs on **port 3031** (not 3000).

## Test Credentials (after seed)

| Role | Email | Password |
|------|-------|----------|
| **Admin** | admin@authora.local | admin123 |
| **User** | test@authora.local | test123 |

### Option A: Register a new account
1. Go to http://localhost:3031/register
2. Create an account (email + password)
3. Use it to log in and test

### Promote to admin (if seed failed)
```powershell
cd apps/api
$env:DATABASE_URL="postgresql://authora:authora@localhost:5432/authora"
python -m authora.scripts.promote_admin your@email.com
```

## Where Templates Appear

- **Dashboard → Templates** (`/dashboard/templates`) — browse all templates
- **New project** (`/dashboard/projects/new`) — choose template when creating a project
- **Onboarding** — template selector for new users
- **Admin → Templates** (`/dashboard/admin/templates`) — manage templates (admin only)

## Verify

- **API:** http://localhost:8000/health → `{"status":"ok"}`
- **Web:** http://localhost:3031 → landing page
- **Login:** http://localhost:3031/login
- **Templates:** http://localhost:3031/dashboard/templates (requires login)
