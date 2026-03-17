# AUTHORA Performance & Scaling Guide

Production optimizations for fast loading, scalable backend, efficient database queries, caching, and API performance.

---

## 1. Performance Summary

### Backend (FastAPI)

| Optimization | Status | Impact |
|-------------|--------|--------|
| **GZip compression** | ✅ Enabled | Responses >500 bytes compressed; reduces payload 60–80% for JSON |
| **DB connection pool** | ✅ Configurable | `DB_POOL_SIZE=20`, `DB_POOL_MAX_OVERFLOW=10` (env); supports concurrent requests |
| **Redis rate limiting** | ✅ Enabled | Shared across API instances; fallback to in-memory when Redis unavailable |
| **Config API caching** | ✅ 60s TTL | `/api/v1/config`, `/mode`, `/branding`, `/ai` cached; reduces DB hits on frontend loads |
| **Reference cache** | ✅ In-memory | Dictionary/thesaurus lookups cached (24h TTL, 2000 entries) |
| **Eager loading** | ✅ `selectinload` | Notes, books, collaboration, export, ghostwriter use `selectinload` to avoid N+1 |
| **Pagination** | ✅ Projects, collaboration, admin | `limit`/`offset` on list endpoints; default limit 50–200 |
| **Indexes** | ✅ Migration 039 | `projects.user_id`, `projects.updated_at`, `books.project_id` for list queries |

### Frontend (Next.js)

| Optimization | Status | Notes |
|-------------|--------|-------|
| **Compression** | ✅ Built-in | Next.js compresses in production |
| **Static assets** | ✅ CDN-ready | `/_next/static/*` cacheable (see CLOUDFLARE_SETUP.md) |
| **Code splitting** | ✅ App Router | Route-based splitting by default |
| **Loading states** | ✅ Implemented | Suspense/loading across dashboard, panels, modals |

### API Endpoints

- **Health**: `/health`, `/health/ready` (DB + Redis), `/health/ai` — excluded from rate limit
- **Docs**: `/api/docs`, `/api/redoc`, `/openapi.json` — excluded from rate limit
- **Rate limit**: 100 req/min per IP per key (Redis-backed when available)

---

## 2. Scaling Readiness Summary

### Horizontal Scaling

| Component | Ready | Notes |
|----------|-------|-------|
| **API** | ✅ | Stateless; Redis for rate limit; DB pool per instance |
| **Web** | ✅ | Stateless; can run multiple replicas behind LB |
| **PostgreSQL** | ✅ | Connection pooling; consider PgBouncer for many API instances |
| **Redis** | ✅ | Required for readiness; used for rate limit and health check |

### Vertical Scaling

- **DB pool**: Increase `DB_POOL_SIZE` (e.g. 50) and `DB_POOL_MAX_OVERFLOW` (e.g. 20) for heavier load
- **API workers**: `uvicorn main:app --workers 4` (or more) for CPU-bound traffic
- **Redis**: Single instance sufficient for rate limit; cluster for session/cache at scale

### Database

- **Indexes**: Migration 039 adds indexes for `list_projects` and `list_books`
- **Queries**: Eager loading used; no known N+1 on hot paths
- **Migrations**: Run `alembic upgrade head` before scaling

### Caching Strategy

| Data | Cache | TTL | Scope |
|------|-------|-----|-------|
| Config / feature flags | In-memory | 60s | Per API instance |
| Reference (dict/thesaurus) | In-memory | 24h | Per API instance |
| Rate limit counters | Redis | 60s window | Shared |
| Static assets | CDN | 1 month | Edge |

---

## 3. Production-Ready Confirmation

### Checklist

- [x] GZip compression on API responses
- [x] Configurable DB pool for production
- [x] Redis-backed rate limiting (with in-memory fallback)
- [x] Config API caching (60s)
- [x] Database indexes for list queries
- [x] Pagination on projects list (limit/offset)
- [x] Eager loading on relational queries
- [x] Health checks (liveness, readiness with DB + Redis)
- [x] Secure headers (X-Content-Type-Options, X-Frame-Options, etc.)
- [x] Request ID for tracing

### Environment Variables (Production)

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/authora
DB_POOL_SIZE=20
DB_POOL_MAX_OVERFLOW=10

# Redis (required for readiness; used for rate limit)
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<openssl rand -hex 32>
```

### Deployment

1. Run migration: `alembic upgrade head`
2. Ensure PostgreSQL and Redis are running
3. Verify readiness: `GET /health/ready` → `{"status":"ready","checks":{"database":true,"redis":true}}`
4. Scale API: multiple uvicorn workers or replicas behind load balancer

---

## See Also

- [DEPLOYMENT.md](DEPLOYMENT.md) — Deployment architecture
- [CLOUDFLARE_SETUP.md](CLOUDFLARE_SETUP.md) — CDN and cache rules
- [GO_LIVE_CHECKLIST.md](GO_LIVE_CHECKLIST.md) — Pre-launch validation
