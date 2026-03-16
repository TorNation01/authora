# AUTHORA Production Deployment Summary

**Confirmation: AUTHORA is production-deployable.**

This document summarizes the deployment layer and provides quick reference for operators.

---

## 1. Deployment Architecture Summary

| Component | Port | Notes |
|-----------|------|-------|
| Caddy (prod) | 80, 443 | Reverse proxy, TLS, secure headers |
| API | 8000 (internal) | FastAPI, health at /health, /health/ready, /health/ai |
| Web | 3000 (internal) | Next.js |
| PostgreSQL | 5432 (internal) | pgvector |
| Redis | 6379 (internal) | Cache, queues |
| Storage | volume | authora_storage for exports, uploads |

**Environments:** development | staging | production

**Profiles:** `docker compose` (dev), `-f docker-compose.staging.yml` (staging), `--profile prod` (production with Caddy)

---

## 2. One-Command Bootstrap Summary

```bash
# From empty directory or existing clone
./scripts/bootstrap-one.sh [repo_url]
# Or: npm run bootstrap:one
```

**Flow:** Clone → Install deps → Validate env → Docker up (postgres, redis) → Migrate → Seed → Start API+Web → Health check

**Result:** AUTHORA running at http://localhost:3000 (web), http://localhost:8000 (API)

**Next:** Visit /setup for first-run wizard, or /login to sign in.

---

## 3. Setup Wizard Summary

**Path:** `/setup` (when `feature_standalone_setup_wizard` is enabled)

**Steps:**
1. Branding (app name, tagline)
2. Domain & SSL
3. Database (PostgreSQL URL)
4. Redis URL
5. Admin account (email, password)
6. Email (optional)
7. Storage (local/S3/R2)
8. AI Provider (OpenAI, Anthropic, Ollama)
9. Stripe (optional billing)
10. Backup & preferences
11. Go Live (apply + finalize)

**Block launch when:** Database, Redis, Admin account missing. Other steps can be "configure later."

---

## 4. Domain / SSL Summary

- **Caddy** auto-provisions Let's Encrypt certificates
- **Generate Caddyfile:** `./scripts/generate-caddyfile.sh` (uses DOMAIN_API, DOMAIN_MARKETING, DOMAIN_APP, ACME_EMAIL from .env)
- **DNS:** A records for api.authora.studio, authora.studio, app.authora.studio (or your domains)
- **www redirect:** Configured in Caddyfile
- **Secure headers:** X-Frame-Options, X-Content-Type-Options, Referrer-Policy, etc.
- **WebSocket:** Supported for streaming
- **Upload size:** 100MB default

---

## 5. Backups / Ops Summary

| Task | Command |
|------|---------|
| Backup DB | `./scripts/backup.sh [dir]` |
| Restore DB | `./scripts/restore.sh <file>` |
| Rollback | `./scripts/rollback.sh <backup> prod` |
| Update | `./scripts/update.sh prod` |
| Health | `./scripts/healthcheck.sh [url]` |

**Cron (daily 2am):** `0 2 * * * cd /path/to/authora && ./scripts/backup.sh`

---

## 6. Install Command Summary

| Command | Purpose |
|---------|---------|
| `./scripts/bootstrap.sh` | Fresh Ubuntu: Docker, Node, Python |
| `./scripts/bootstrap-one.sh` | One-command: clone → install → docker → migrate → seed |
| `./scripts/install.sh` | Install deps, .env, directories |
| `./scripts/bootstrap-prod.sh` | Production bootstrap (requires .env) |
| `./scripts/deploy.sh dev` | Dev: infra + migrate |
| `./scripts/deploy.sh prod` | Production: full stack + Caddy |
| `./scripts/validate-env.sh production` | Validate .env for production |
| `./scripts/generate-caddyfile.sh` | Generate Caddyfile from .env |

---

## 7. Documentation Index

| Doc | Purpose |
|-----|---------|
| [DEPLOYMENT_OVERVIEW.md](DEPLOYMENT_OVERVIEW.md) | Architecture overview |
| [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) | Step-by-step install |
| [ONE_COMMAND_BOOTSTRAP.md](ONE_COMMAND_BOOTSTRAP.md) | Bootstrap script |
| [FIRST_RUN_SETUP_WIZARD.md](FIRST_RUN_SETUP_WIZARD.md) | Setup wizard |
| [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) | Production deploy |
| [DOMAIN_AND_SSL.md](DOMAIN_AND_SSL.md) | Domain, SSL, DNS |
| [DATABASE_AND_STORAGE.md](DATABASE_AND_STORAGE.md) | DB, migrations, storage |
| [BACKUPS_AND_RESTORE.md](BACKUPS_AND_RESTORE.md) | Backup, restore |
| [MONITORING_AND_HEALTH.md](MONITORING_AND_HEALTH.md) | Health, logs |
| [UPDATE_AND_ROLLBACK.md](UPDATE_AND_ROLLBACK.md) | Update, rollback |
| [SECURITY_HARDENING.md](SECURITY_HARDENING.md) | Security |
| [TERMINAL_COMMANDS.md](TERMINAL_COMMANDS.md) | Command reference |

---

## Production-Ready Checklist

- [x] Docker-first deployment
- [x] One-command bootstrap
- [x] Setup wizard for first run
- [x] Environment validation (dev/staging/prod)
- [x] Reverse proxy with SSL
- [x] Database migrations
- [x] Backup/restore scripts
- [x] Health checks (/health, /health/ready, /health/ai)
- [x] AI provider env support (OpenAI, Anthropic, Ollama)
- [x] Update and rollback workflows
- [x] Documentation and runbooks
