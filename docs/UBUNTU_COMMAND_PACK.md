# AUTHORA Ubuntu Command Pack

Practical, copy-paste friendly commands for deploying AUTHORA on a fresh Ubuntu LTS (22.04 or 24.04) server. Commands are ordered for a typical first-time deployment.

---

## 1. System Update

```bash
sudo apt-get update && sudo apt-get upgrade -y
```

Refreshes package lists and upgrades installed packages. Run before installing new software.

---

## 2. Docker Install

```bash
curl -fsSL https://get.docker.com | sh
```

Installs Docker Engine using the official script. No manual repo setup required.

```bash
sudo usermod -aG docker "$USER"
```

Adds your user to the `docker` group so you can run Docker without `sudo`. **Log out and back in** (or run `newgrp docker`) for it to take effect.

---

## 3. Docker Compose Plugin Verification

```bash
sudo apt-get install -y docker-compose-plugin
```

Installs the Docker Compose V2 plugin (if not already present).

```bash
docker --version
docker compose version
```

Verifies both Docker and Docker Compose are available. Expect output like `Docker version 24.x` and `Docker Compose version v2.x`.

---

## 4. Git, Curl, and Basic Tools

```bash
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common git jq unzip
```

Installs tools used by the deploy flow: `git` (clone), `curl` (Docker install, health checks), `jq` (JSON), `unzip` (optional extras).

---

## 5. Repo Clone

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
chmod +x scripts/*.sh
```

Clones the repo and makes scripts executable. Adjust the URL if using a fork.

---

## 6. Environment Setup

```bash
cp .env.production.example .env
```

Creates `.env` from the production template.

```bash
openssl rand -hex 32
```

Generates a secure `SECRET_KEY`. Copy the output and set `SECRET_KEY=<output>` in `.env`.

```bash
nano .env
```

Edit and set at minimum:

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | (from openssl output) |
| `DATABASE_URL` | `postgresql://authora:YOUR_STRONG_PASSWORD@postgres:5432/authora` |
| `REDIS_URL` | `redis://redis:6379/0` |
| `NEXT_PUBLIC_API_URL` | `https://api.your-domain.com` |
| `DOMAIN_API` | `api.your-domain.com` |
| `DOMAIN_MARKETING` | `your-domain.com` |
| `DOMAIN_APP` | `app.your-domain.com` |
| `ACME_EMAIL` | `admin@your-domain.com` |

---

## 7. Bootstrap Command

```bash
./scripts/deploy.sh prod
```

One-command deploy: starts PostgreSQL and Redis, runs migrations, seeds, builds images, and starts the full stack (including Caddy). Idempotent — safe to re-run.

**First run:** Ensure `.env` is configured and DNS points to the server before running.

---

## 8. Service Status Checks

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

Lists running containers and their status.

```bash
./scripts/healthcheck.sh https://api.your-domain.com
```

Verifies API health (`/health`, `/health/ready`). Replace with your API URL.

```bash
curl -s https://api.your-domain.com/health | jq .
```

Quick health check with JSON output.

---

## 9. Logs Checks

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f api
```

Follow API logs (Ctrl+C to stop).

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=100 api
```

Last 100 lines of API logs.

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs --tail=50 web postgres caddy
```

Last 50 lines from multiple services.

---

## 10. Reverse Proxy / SSL Follow-Up

Caddy runs in the prod stack and handles reverse proxy and SSL automatically.

**Generate or refresh Caddyfile from `.env`:**

```bash
./scripts/generate-caddyfile.sh
```

**Restart Caddy to pick up changes:**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml restart caddy
```

**DNS checklist (before first deploy):**

- A record: `api.your-domain.com` → server IP
- A record: `your-domain.com` → server IP
- A record: `app.your-domain.com` → server IP
- `ACME_EMAIL` set in `.env` for Let's Encrypt

---

## 11. Backup Command Examples

```bash
./scripts/backup.sh
```

Creates a PostgreSQL backup in `./backups/` with timestamp (e.g. `authora_20250315_143022.dump`).

```bash
./scripts/backup.sh /var/backups/authora
```

Backs up to a specific directory.

```bash
# Cron: daily backup at 2 AM
0 2 * * * cd /path/to/authora && ./scripts/backup.sh /var/backups/authora
```

Add to crontab (`crontab -e`) for automated daily backups.

---

## 12. Update Command Examples

```bash
./scripts/update.sh prod
```

Pulls latest code, rebuilds images, runs migrations, and restarts the stack. Use for production updates.

```bash
git pull --rebase && ./scripts/update.sh prod
```

Explicit pull before update (update script also pulls, but this ensures you have latest).

```bash
./scripts/update.sh
```

Dev mode update (no Caddy, different compose files).

---

## Quick Reference

| Action | Command |
|--------|---------|
| Deploy (first time) | `./scripts/deploy.sh prod` |
| Update | `./scripts/update.sh prod` |
| Backup | `./scripts/backup.sh` |
| Health check | `./scripts/healthcheck.sh https://api.your-domain.com` |
| View logs | `docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f api` |
| Restart stack | `docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d` |

---

## See Also

- [UBUNTU_SERVER_DEPLOYMENT](UBUNTU_SERVER_DEPLOYMENT.md) — Full deployment guide with hardening, firewall, and troubleshooting
- [DEPLOY_QUICKSTART](DEPLOY_QUICKSTART.md) — One-command deploy flow
- [BACKUP_AND_RESTORE](BACKUP_AND_RESTORE.md) — Backup and restore procedures
