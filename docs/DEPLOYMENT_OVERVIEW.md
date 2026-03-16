# AUTHORA Deployment Overview

This document provides a high-level overview of the AUTHORA deployment architecture and options.

## Deployment Modes

| Mode | Use Case | Compose | Profile |
|------|----------|---------|---------|
| **Development** | Local dev, Docker stack | `docker-compose.yml` | (default) |
| **Staging** | Pre-production testing | `docker-compose.yml` + `docker-compose.staging.yml` | - |
| **Production** | Live deployment with Caddy | `docker-compose.yml` + `docker-compose.prod.yml` | `prod` |

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │              Caddy (prod only)           │
                    │  80/443, SSL, reverse proxy, headers   │
                    └──────────────────┬──────────────────────┘
                                       │
         ┌─────────────────────────────┼─────────────────────────────┐
         │                             │                             │
         ▼                             ▼                             ▼
  api.authora.studio            authora.studio              app.authora.studio
  (API :8000)                   (Web :3000)                 (Web :3000)
         │                             │                             │
         └─────────────────────────────┼─────────────────────────────┘
                                       │
                    ┌──────────────────┴──────────────────────┐
                    │  PostgreSQL (pgvector)  │  Redis        │
                    └────────────────────────────────────────┘
```

## Key Components

- **postgres** – PostgreSQL 16 with pgvector extension
- **redis** – Redis 7 for caching and queues
- **api** – FastAPI backend (Python)
- **web** – Next.js frontend
- **caddy** – Reverse proxy with automatic SSL (production only)

## Quick Start

### Development
```bash
docker compose up -d
# API: http://localhost:8000, Web: http://localhost:3000
```

### Production
```bash
cp .env.production.example .env
# Edit .env: SECRET_KEY, DATABASE_URL, REDIS_URL, domains
./scripts/generate-caddyfile.sh
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d
```

## Related Documentation

- [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) – Step-by-step installation
- [ONE_COMMAND_BOOTSTRAP.md](ONE_COMMAND_BOOTSTRAP.md) – Single-command setup
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) – Production deployment details
- [DOMAIN_AND_SSL.md](DOMAIN_AND_SSL.md) – Domain and SSL configuration
