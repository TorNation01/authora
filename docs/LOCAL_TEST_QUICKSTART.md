# AUTHORA Local Testing Quickstart

## URLs

| Service | URL |
|---------|-----|
| **Website (app)** | http://localhost:3031 |
| **Login** | http://localhost:3031/login |
| **Register** | http://localhost:3031/register |
| **Admin panel** | http://localhost:3031/dashboard/admin |
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

# 3. Start web app (separate terminal)
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"; npm run dev
```

Web runs on **port 3031** (not 3000).

## Test Logins

### Option A: Register a new account
1. Go to http://localhost:3031/register
2. Create an account (email + password)
3. Use it to log in and test

### Option B: Admin user (if seed ran)
- **Email:** admin@authora.local  
- **Password:** admin123  
- Change password after first login.

If the seed script failed (model error), use Option A to register, then promote to admin:

```powershell
cd apps/api
$env:DATABASE_URL="postgresql://authora:authora@localhost:5432/authora"
python -m authora.scripts.promote_admin your@email.com
```

## Verify

- **API:** http://localhost:8000/health → `{"status":"ok"}`
- **Web:** http://localhost:3031 → landing page
- **Login:** http://localhost:3031/login
