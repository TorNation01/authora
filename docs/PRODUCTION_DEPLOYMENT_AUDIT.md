# AUTHORA Production Deployment Audit

**Audit date:** 2026-03-15  
**Status:** Production-ready

---

## 1. Deployment Summary

### One-Command Deploy

| Command | Mode | Flow |
|---------|------|------|
| `./scripts/deploy.sh` | dev | Clone → env → preflight → validate → docker → migrate → seed → verify |
| `./scripts/deploy.sh prod` | prod | Same + Caddy, production env validation |

**Quickstart:**
```bash
git clone https://github.com/TorNation01/authora.git && cd authora && cp .env.example .env && ./scripts/deploy.sh
```

### Environment Config

| File | Purpose |
|------|---------|
| `.env.example` | Dev defaults |
| `.env.production.example` | Production template |
| `scripts/validate-env.sh` | Pre-deploy validation (development \| staging \| production) |

**Production validation:**
```bash
source .env && ./scripts/validate-env.sh production
```

### Docker Support

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Base stack: postgres, redis, api, web |
| `docker-compose.prod.yml` | Production: Caddy, no port exposure, resource limits |
| `docker/Dockerfile.api` | FastAPI + uvicorn |
| `docker/Dockerfile.web` | Next.js |

**Production:**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d
```

### Reverse Proxy

| Component | Config | Ports |
|-----------|--------|-------|
| Caddy | `caddy/Caddyfile` | 80, 443 |
| TLS | Let's Encrypt (ACME) | Auto |
| Domains | `DOMAIN_API`, `DOMAIN_APP`, `DOMAIN_MARKETING` | From .env |

Generate Caddyfile: `./scripts/generate-caddyfile.sh`

---

## 2. Security Summary

### Authentication Hardening

| Feature | Implementation |
|---------|----------------|
| **Password hashing** | bcrypt, cost factor 12 |
| **JWT** | Short-lived access (60 min), refresh (7 days) |
| **Auth rate limit** | 5 attempts / 15 min per IP (login, register) |
| **Token storage** | Refresh token hashed in DB |

### Rate Limiting

| Scope | Limit | Window |
|-------|-------|--------|
| **General API** | 100 req/min per IP | 60 s |
| **Auth (login/register)** | 5 attempts | 15 min |
| **AI actions** | 60/min per user (configurable) | 60 s |

- Redis-backed (scales across instances)
- In-memory fallback when Redis unavailable
- Configurable: `RATE_LIMIT_REQUESTS_PER_MINUTE`, `RATE_LIMIT_AUTH_ATTEMPTS`

### Input Validation

| Layer | Implementation |
|-------|----------------|
| **API** | Pydantic on all request bodies |
| **File uploads** | Type allowlist, size limits |
| **SQL** | SQLAlchemy ORM only; no raw user input |

### Secure API Handling

| Header | Value |
|--------|-------|
| X-Content-Type-Options | nosniff |
| X-Frame-Options | DENY |
| X-XSS-Protection | 1; mode=block |
| Referrer-Policy | strict-origin-when-cross-origin |
| Permissions-Policy | geolocation=(), microphone=(), camera=() |
| Strict-Transport-Security | max-age=31536000 (when `HSTS_MAX_AGE` set) |
| X-Request-ID | Per-request trace ID |

### Cron Endpoint Protection

- `CRON_SECRET` + `X-Cron-Secret` header for `/accountability/cron/reminders`

---

## 3. Scaling Summary

### Horizontal Scaling

| Component | Replicas | Notes |
|-----------|----------|-------|
| **API** | `deploy.replicas: 2+` | Stateless; Redis for rate limit |
| **Web** | `deploy.replicas: 2+` | Stateless Next.js |
| **PostgreSQL** | 1 (or managed) | Primary |
| **Redis** | 1 (or managed) | Shared state |

**Enable:** `docker-compose.prod.yml` → `api.deploy.replicas: 2`

### Load Balancing

- **Caddy** reverse-proxies to api:8000 and web:3000
- For multiple replicas: use Caddy's `reverse_proxy api:8000 api2:8000` or external LB (nginx, HAProxy, cloud LB)

### Database Optimization

| Setting | Default | Production |
|---------|---------|------------|
| Pool size | 20 | 20–50 |
| Max overflow | 10 | 20 |
| Connection string | - | Use connection pooling (pgbouncer optional) |

**Indexes:** See `alembic/versions/039_add_performance_indexes.py` for projects, books.

**Sizing:** See [SERVER-SIZING.md](./SERVER-SIZING.md)

---

## 4. Monitoring Summary

### Logs

| Source | Format | Destination |
|--------|--------|-------------|
| **API** | JSON (structlog) | stdout |
| **Web** | Next.js default | stdout |
| **Docker** | stdout/stderr | journald or logging driver |

**View:**
```bash
docker compose logs -f api
```

### Error Tracking

| Option | Implementation |
|--------|----------------|
| **Sentry** | Set `SENTRY_DSN`; optional `pip install sentry-sdk` |
| **Built-in** | Unhandled exceptions logged with request_id |

### Uptime Monitoring

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness |
| `GET /health/ready` | Readiness (DB, Redis) |
| `GET /health/ai` | AI provider status |

**External monitoring:** Poll `https://api.yourdomain.com/health` and `https://api.yourdomain.com/health/ready` (e.g. UptimeRobot, Pingdom).

---

## 5. Production-Ready Confirmation

### Checklist

- [x] One-command deploy (`./scripts/deploy.sh prod`)
- [x] Environment validation (`validate-env.sh production`)
- [x] Docker Compose (dev + prod)
- [x] Reverse proxy (Caddy, TLS)
- [x] Auth hardening (bcrypt, JWT, auth rate limit)
- [x] Rate limiting (general + auth, Redis-backed)
- [x] Input validation (Pydantic)
- [x] Secure headers (incl. HSTS when configured)
- [x] Horizontal scaling (replicas, resource limits)
- [x] Database optimization (pool, indexes)
- [x] Logs (stdout, structlog)
- [x] Error tracking (Sentry-ready)
- [x] Health endpoints (liveness, readiness)
- [x] Cron secret protection

### Pre-Launch

1. Set `SECRET_KEY` (openssl rand -hex 32)
2. Set `DATABASE_URL`, `REDIS_URL`
3. Set `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_APP_URL`, `NEXT_PUBLIC_MARKETING_URL`
4. Configure DNS (A records for domains)
5. Run `./scripts/validate-env.sh production`
6. Run `./scripts/deploy.sh prod`
7. Complete setup wizard at `https://app.yourdomain.com/setup`

### Post-Launch

- Add backup cron: `0 2 * * * /path/to/scripts/backup.sh`
- Configure reminders cron (see DEPLOYMENT.md)
- Optional: `HSTS_MAX_AGE=31536000`, `SENTRY_DSN` for error tracking

---

## See Also

- [DEPLOYMENT.md](./DEPLOYMENT.md) — Full deployment guide
- [SECURITY.md](./SECURITY.md) — Security architecture
- [SERVER-SIZING.md](./SERVER-SIZING.md) — Resource sizing
- [LOGGING.md](./LOGGING.md) — Logging guide
- [GO_LIVE_CHECKLIST.md](./GO_LIVE_CHECKLIST.md) — Pre/post go-live
