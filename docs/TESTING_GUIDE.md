# AUTHORA – Full Testing Guide

## Quick Start

**Services running:**
- **Postgres** – `localhost:5433` (Docker)
- **Redis** – `localhost:6380` (Docker)
- **API** – `http://localhost:8000`
- **Web** – `http://localhost:3031` (or `http://localhost:3000`)

**Admin login:**
- **Email:** `admin@authora.local`
- **Password:** `admin123`

---

## All Pages & Access

### Public (no login)

| URL | Description |
|-----|-------------|
| `http://localhost:3031/` | Marketing homepage |
| `http://localhost:3031/login` | Login |
| `http://localhost:3031/register` | Register |
| `http://localhost:3031/pricing` | Pricing |
| `http://localhost:3031/features` | Features |
| `http://localhost:3031/for-fiction-writers` | Fiction writers |
| `http://localhost:3031/for-nonfiction-writers` | Nonfiction writers |
| `http://localhost:3031/story-integrity-engine` | Story integrity |
| `http://localhost:3031/story-density-engine` | Story density |
| `http://localhost:3031/contact` | Contact |
| `http://localhost:3031/demo` | Demo |
| `http://localhost:3031/help` | Help center |
| `http://localhost:3031/help/[slug]` | Help article |
| `http://localhost:3031/faq` | FAQ |
| `http://localhost:3031/privacy` | Privacy |
| `http://localhost:3031/terms` | Terms |
| `http://localhost:3031/share/[slug]` | Share card (public) |
| `http://localhost:3031/setup` | Setup wizard |

### Dashboard (login required)

| URL | Description |
|-----|-------------|
| `http://localhost:3031/dashboard` | Home |
| `http://localhost:3031/dashboard/templates` | Templates |
| `http://localhost:3031/dashboard/notes` | Ideas & notes |
| `http://localhost:3031/dashboard/journey` | Your journey |
| `http://localhost:3031/dashboard/accountability` | Progress |
| `http://localhost:3031/dashboard/gamification` | Celebrations |
| `http://localhost:3031/dashboard/export` | Export |
| `http://localhost:3031/dashboard/settings` | Settings |
| `http://localhost:3031/dashboard/billing` | Billing (if enabled) |
| `http://localhost:3031/dashboard/notifications` | Notifications |
| `http://localhost:3031/dashboard/projects/new` | New project |
| `http://localhost:3031/dashboard/projects/[id]` | Project overview |
| `http://localhost:3031/dashboard/projects/[id]/manage` | Manage books |
| `http://localhost:3031/dashboard/projects/[id]/settings` | Project settings |
| `http://localhost:3031/dashboard/projects/[id]/sharing` | Sharing |
| `http://localhost:3031/dashboard/projects/[id]/vault` | Vault |
| `http://localhost:3031/dashboard/projects/[id]/search` | Search |
| `http://localhost:3031/dashboard/projects/[id]/notes` | Project notes |
| `http://localhost:3031/dashboard/projects/[id]/books/new` | New book |
| `http://localhost:3031/dashboard/projects/[id]/books/[bookId]` | Book / manuscript |
| `http://localhost:3031/dashboard/projects/[id]/books/[bookId]/plan` | Chapter plan |
| `http://localhost:3031/dashboard/projects/[id]/books/[bookId]/edit` | Edit |
| `http://localhost:3031/dashboard/projects/[id]/books/[bookId]/ghostwriter` | Ghostwriter |
| `http://localhost:3031/dashboard/export/[bookId]/publishing` | Export publishing |
| `http://localhost:3031/onboarding` | Onboarding flow |

### Admin (admin only)

| URL | Description |
|-----|-------------|
| `http://localhost:3031/dashboard/admin` | Admin overview |
| `http://localhost:3031/dashboard/admin/users` | User management |
| `http://localhost:3031/dashboard/admin/feature-flags` | Feature flags |
| `http://localhost:3031/dashboard/admin/ai` | AI providers |
| `http://localhost:3031/dashboard/admin/ai-usage` | AI usage |
| `http://localhost:3031/dashboard/admin/export-jobs` | Export jobs |
| `http://localhost:3031/dashboard/admin/notification-logs` | Notification logs |
| `http://localhost:3031/dashboard/admin/reminders` | Reminders |
| `http://localhost:3031/dashboard/admin/errors` | Error monitoring |
| `http://localhost:3031/dashboard/admin/health` | System health |
| `http://localhost:3031/dashboard/admin/setup` | Setup state |
| `http://localhost:3031/dashboard/admin/storage` | Storage |
| `http://localhost:3031/dashboard/admin/audit` | Audit logs |
| `http://localhost:3031/dashboard/admin/grants` | Entitlement grants |
| `http://localhost:3031/dashboard/admin/promo-codes` | Promo codes |
| `http://localhost:3031/dashboard/admin/entitlement-audit` | Entitlement audit |
| `http://localhost:3031/dashboard/admin/support` | Support tools |
| `http://localhost:3031/dashboard/admin/content` | Content templates |
| `http://localhost:3031/dashboard/admin/onboarding` | Onboarding |
| `http://localhost:3031/dashboard/admin/activation` | Activation |
| `http://localhost:3031/dashboard/admin/encouragement` | Encouragement messages |
| `http://localhost:3031/dashboard/admin/accountability-rules` | Accountability rules |
| `http://localhost:3031/dashboard/admin/gamification` | Gamification |

---

## Start Everything (Commands)

```powershell
# 1. Start Postgres + Redis
cd e:\anakatech-legal-collective\authora
docker compose up -d postgres redis

# 2. Run migrations (if needed)
docker compose run --rm -e DATABASE_URL="postgresql://authora:authora@postgres:5432/authora" api alembic upgrade head

# 3. Seed admin user (if needed)
docker compose run --rm -e DATABASE_URL="postgresql://authora:authora@postgres:5432/authora" -e REDIS_URL="redis://redis:6379/0" -e SECRET_KEY="dev-secret" api python -m authora.scripts.seed

# 4. Start API (terminal 1)
npm run dev:api

# 5. Start Web (terminal 2)
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"; npm run dev
```

**Note:** If `.env` uses `POSTGRES_PORT=5433` and `REDIS_PORT=6380`, the API runs locally and connects to `localhost:5433` and `localhost:6380`. The web runs on port 3031 (or 3000 if WEB_PORT not set).

---

## Test Flow

1. **Login:** http://localhost:3031/login → `admin@authora.local` / `admin123`
2. **Dashboard:** http://localhost:3031/dashboard
3. **Admin:** http://localhost:3031/dashboard/admin (sidebar: Admin)
4. **Create project:** http://localhost:3031/dashboard/projects/new
5. **Create book:** Project → New book
6. **Write:** Open book → Edit or Ghostwriter
7. **Export:** http://localhost:3031/dashboard/export

---

## API Health

- `http://localhost:8000/health` – Liveness
- `http://localhost:8000/health/ai` – AI providers
