# AUTHORA Ubuntu Server Deployment

Launch-ready deployment path for AUTHORA on Ubuntu LTS (22.04 or 24.04) with Docker-first operations and domain-live support.

**Target:** Production use with authora.studio (or your domain).

**Quick commands:** See [UBUNTU_COMMAND_PACK](UBUNTU_COMMAND_PACK.md) for a copy-paste terminal command pack.

---

## Prerequisites

- Ubuntu 22.04 or 24.04 LTS server
- Root or sudo access
- SSH access (port 22)
- Domain pointed to server IP (or ready to configure)

---

## 1. Required Package Installation

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Base packages
sudo apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  software-properties-common \
  git \
  jq \
  unzip
```

---

## 2. Docker and Docker Compose Setup

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Add your user to docker group (avoid sudo for docker)
sudo usermod -aG docker "$USER"

# Install Docker Compose plugin
sudo apt-get install -y docker-compose-plugin

# Verify
docker --version
docker compose version
```

**Important:** Log out and back in (or run `newgrp docker`) so the docker group takes effect.

---

## 3. Firewall Guidance

```bash
# Allow SSH (do this first to avoid lockout)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw --force enable

# Verify
sudo ufw status
```

---

## 4. Repo Clone Path

```bash
# Clone (adjust URL if using a fork)
git clone https://github.com/TorNation01/authora.git
cd authora

# Make scripts executable
chmod +x scripts/*.sh
```

---

## 5. Environment File Preparation

```bash
# Copy production template
cp .env.production.example .env

# Generate SECRET_KEY
openssl rand -hex 32
# Copy output; set SECRET_KEY=... in .env

# Edit .env
nano .env
```

**Required variables for production:**

| Variable | Example | Notes |
|----------|---------|-------|
| `SECRET_KEY` | (from openssl rand -hex 32) | **Must change** from default |
| `DATABASE_URL` | `postgresql://authora:STRONG_PASS@postgres:5432/authora` | Use strong password |
| `REDIS_URL` | `redis://redis:6379/0` | Docker internal |
| `NEXT_PUBLIC_API_URL` | `https://api.authora.studio` | Public API URL |
| `NEXT_PUBLIC_MARKETING_URL` | `https://authora.studio` | Marketing site |
| `NEXT_PUBLIC_APP_URL` | `https://app.authora.studio` | App URL |
| `DOMAIN_API` | `api.authora.studio` | For Caddyfile |
| `DOMAIN_MARKETING` | `authora.studio` | For Caddyfile |
| `DOMAIN_APP` | `app.authora.studio` | For Caddyfile |
| `ACME_EMAIL` | `admin@your-domain.com` | Let's Encrypt contact |

**Optional:** `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OLLAMA_ENABLED`, `OLLAMA_BASE_URL`, Stripe keys.

---

## 6. Bootstrap Script Execution

**Option A: One-command (if starting from empty directory)**

```bash
./scripts/bootstrap-one.sh https://github.com/TorNation01/authora.git
cd authora
# Then configure .env and run production deploy
```

**Option B: Full server bootstrap (recommended for production)**

```bash
# Step 1: Install Docker, Node, Python (if not already done)
./scripts/bootstrap.sh

# Log out and back in (for docker group)

# Step 2: Install deps and prepare
./scripts/install.sh

# Step 3: Configure .env (see section 5)
cp .env.production.example .env
nano .env

# Step 4: Validate
source .env && ./scripts/validate-env.sh production

# Step 5: Production bootstrap (build, migrate, start)
./scripts/bootstrap-prod.sh
```

**Option C: Direct production deploy**

```bash
source .env && ./scripts/validate-env.sh production
./scripts/deploy.sh prod
```

---

## 7. Service Verification

```bash
# Check containers
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod ps

# Health checks
curl -s http://localhost:8000/health
curl -s http://localhost:8000/health/ready
curl -s http://localhost:8000/health/ai

# Or use script
./scripts/healthcheck.sh http://localhost:8000
```

**Expected:** All containers `Up`, health endpoints return `{"status":"ok"}` or similar.

---

## 8. Reverse Proxy and SSL

AUTHORA uses **Caddy** as a container (production profile). No host-level proxy needed.

**Generate Caddyfile from .env:**

```bash
./scripts/generate-caddyfile.sh
```

**Caddy runs when you use `--profile prod`:**

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d
```

Caddy will:
- Listen on 80 and 443
- Auto-provision Let's Encrypt certificates
- Reverse-proxy to API (8000) and Web (3000)
- Apply secure headers, gzip, WebSocket support

**Host-level proxy alternative:** If you prefer nginx or Apache on the host, disable the Caddy container and configure your proxy to forward to `localhost:8000` (API) and `localhost:3000` (Web). Document your setup.

---

## 9. SSL Enablement Flow

1. **DNS:** Ensure A records for `api.authora.studio`, `authora.studio`, `app.authora.studio` point to your server IP.
2. **Ports:** 80 and 443 open (see Firewall).
3. **Caddyfile:** Run `./scripts/generate-caddyfile.sh` (uses DOMAIN_* and ACME_EMAIL from .env).
4. **Start stack:** `docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod up -d`
5. **First request:** Caddy contacts Let's Encrypt; certificates are issued automatically.
6. **Verify:** `curl -sI https://api.authora.studio/health`

---

## 10. Domain DNS Checklist (authora.studio)

| Record Type | Name | Value | TTL |
|-------------|------|-------|-----|
| A | `api` | `<server-ip>` | 300 |
| A | `@` (authora.studio) | `<server-ip>` | 300 |
| A | `app` | `<server-ip>` | 300 |
| CNAME | `www` | `authora.studio` | 300 |

**Or if using root + subdomains:**

| Record | Target |
|--------|--------|
| `api.authora.studio` | A → server IP |
| `authora.studio` | A → server IP |
| `app.authora.studio` | A → server IP |
| `www.authora.studio` | CNAME → authora.studio |

**Propagation:** Allow 5–60 minutes. Check with `dig api.authora.studio` or `nslookup api.authora.studio`.

---

## 11. Basic Hardening Checklist

- [ ] `SECRET_KEY` changed from default (`openssl rand -hex 32`)
- [ ] Strong `POSTGRES_PASSWORD` in DATABASE_URL (or use Docker default with no external exposure)
- [ ] UFW enabled: 22, 80, 443 only
- [ ] SSH: key-based auth preferred; disable password auth if appropriate
- [ ] `.env` not committed; permissions `chmod 600 .env`
- [ ] Caddy handles TLS; no plain HTTP for production traffic
- [ ] `CRON_SECRET` set if using accountability cron
- [ ] AI keys (OpenAI, Anthropic) in .env, not in code
- [ ] Regular `apt-get update && apt-get upgrade`
- [ ] Backups scheduled (see section 14)

---

## 12. Reboot Persistence Checks

**Docker:** Containers use `restart: unless-stopped` in production compose. They will start on reboot.

**Verify:**

```bash
# Simulate reboot
sudo reboot

# After reboot, SSH back in and check
cd /path/to/authora
docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile prod ps
```

**Systemd (optional):** To start Docker on boot (usually default):

```bash
sudo systemctl enable docker
sudo systemctl is-enabled docker
```

---

## 13. Update Path

```bash
cd /path/to/authora

# Backup first
./scripts/backup.sh

# Update
./scripts/update.sh prod
# Or: npm run update:prod
```

**What it does:** `git pull` → rebuild images → run migrations → restart stack with `--profile prod`.

---

## 14. Backup Path

**Manual backup:**

```bash
cd /path/to/authora
./scripts/backup.sh
# Output: ./backups/authora_YYYYMMDD_HHMMSS.dump
```

**Cron (daily 2am):**

```bash
crontab -e
# Add:
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

**Restore:**

```bash
./scripts/restore.sh ./backups/authora_20250315_020000.dump
# Then restart: ./scripts/update.sh prod
```

**Rollback (restore + restart):**

```bash
./scripts/rollback.sh ./backups/authora_20250315_020000.dump prod
```

---

## Quick Reference: Full Deployment Flow

```bash
# 1. Server prep
sudo apt-get update && sudo apt-get upgrade -y
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in

# 2. Clone and configure
git clone https://github.com/TorNation01/authora.git
cd authora
chmod +x scripts/*.sh
cp .env.production.example .env
nano .env  # Set SECRET_KEY, DATABASE_URL, domains

# 3. Deploy
source .env && ./scripts/validate-env.sh production
./scripts/generate-caddyfile.sh
./scripts/deploy.sh prod

# 4. Verify
./scripts/healthcheck.sh https://api.authora.studio

# 5. First admin
./scripts/first-admin.sh --docker --prod
# Visit https://app.authora.studio/setup or /login
```

---

## Related

- [DEPLOYMENT_OVERVIEW.md](DEPLOYMENT_OVERVIEW.md) – Architecture
- [PRODUCTION_DEPLOYMENT.md](PRODUCTION_DEPLOYMENT.md) – Production details
- [DOMAIN_AND_SSL.md](DOMAIN_AND_SSL.md) – Domain and SSL
- [BACKUPS_AND_RESTORE.md](BACKUPS_AND_RESTORE.md) – Backup and restore
- [SECURITY_HARDENING.md](SECURITY_HARDENING.md) – Security
