# AUTHORA Environment Variable Examples (Option 2)

Exact env values for production with **authora.studio**, **app.authora.studio**, **api.authora.studio**.

## Production .env (Option 2)

```bash
# Deployment
DEPLOYMENT_MODE=standalone

# Database (replace with your production URL)
DATABASE_URL=postgresql://authora:YOUR_PASSWORD@postgres:5432/authora

# Redis
REDIS_URL=redis://redis:6379/0

# Auth (generate: openssl rand -hex 32)
SECRET_KEY=your-64-char-hex-secret
CRON_SECRET=your-64-char-hex-secret

# Frontend (Option 2)
NEXT_PUBLIC_API_URL=https://api.authora.studio
NEXT_PUBLIC_MARKETING_URL=https://authora.studio
NEXT_PUBLIC_APP_URL=https://app.authora.studio
NEXT_PUBLIC_DEPLOYMENT_MODE=standalone

# API (Docker internal; optional if same host)
API_URL=http://api:8000

# CORS - both marketing and app must call API
CORS_ORIGINS=["https://authora.studio","https://www.authora.studio","https://app.authora.studio"]

# Production domains (for Caddy)
DOMAIN_API=api.authora.studio
DOMAIN_MARKETING=authora.studio
DOMAIN_APP=app.authora.studio
ACME_EMAIL=admin@authora.studio

# AI (optional)
OPENAI_API_KEY=sk-...
# or ANTHROPIC_API_KEY=sk-ant-...
```

## Docker Compose Overrides

```bash
NEXT_PUBLIC_API_URL=https://api.authora.studio
NEXT_PUBLIC_MARKETING_URL=https://authora.studio
NEXT_PUBLIC_APP_URL=https://app.authora.studio
```

## Cloudflare Tunnel

- Tunnel routes: `api.authora.studio` → `http://localhost:8000`, `authora.studio` and `app.authora.studio` → `http://localhost:3000`
- DNS: CNAME all three to your tunnel hostname
- Same env values as above

## Health Check Examples

```bash
# API health
curl -sf https://api.authora.studio/health

# Readiness
curl -sf https://api.authora.studio/health/ready

# Go-live verification
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio https://app.authora.studio
```

## Cron (Reminders)

```bash
0 * * * * curl -X POST -H "X-Cron-Secret: YOUR_CRON_SECRET" https://api.authora.studio/api/v1/accountability/cron/reminders
```
