# AUTHORA Ubuntu Deploy Commands

Exact commands for deploying AUTHORA on a fresh Ubuntu 22.04 or 24.04 server.

---

## 1. Fresh Ubuntu Bootstrap

**Option A: With repo clone (recommended)**

```bash
cd ~
git clone https://github.com/TorNation01/authora.git
cd authora
chmod +x scripts/*.sh
./scripts/bootstrap.sh
```

**Option B: Bootstrap script only (repo already cloned)**

```bash
cd /path/to/authora
./scripts/bootstrap.sh
```

**Option C: Remote bootstrap (no clone yet)**

```bash
curl -fsSL https://raw.githubusercontent.com/TorNation01/authora/main/scripts/bootstrap.sh -o /tmp/bootstrap.sh
chmod +x /tmp/bootstrap.sh
/tmp/bootstrap.sh
```

Installs: Docker, Docker Compose plugin, Node.js 20, Python 3, git, jq, base packages.

**After Docker install:** Log out and back in so `docker` works without sudo.

---

## 2. Manual Package Install (Alternative)

If you prefer manual install instead of bootstrap:

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release \
  software-properties-common git jq unzip python3 python3-pip python3-venv
```

---

## 3. Manual Docker Install

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in
```

---

## 4. Manual Docker Compose Install

```bash
sudo apt-get install -y docker-compose-plugin
```

---

## 5. Repo Clone

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
chmod +x scripts/*.sh
```

---

## 6. Working Directory Setup

```bash
cd authora
./scripts/install.sh
```

Creates `.env` from `.env.example`, installs Node and API deps, creates `backups`, `storage`, `caddy`.

---

## 7. Environment File Creation

```bash
cd authora
cp .env.example .env
nano .env
```

**Required for production:**
- `SECRET_KEY` — generate: `openssl rand -hex 32`
- `DATABASE_URL` — e.g. `postgresql://authora:PASSWORD@postgres:5432/authora`
- `REDIS_URL` — e.g. `redis://redis:6379/0`
- `NEXT_PUBLIC_API_URL` — e.g. `https://api.authora.studio`
- `DOMAIN_API` — e.g. `api.authora.studio`
- `DOMAIN_WEB` — e.g. `authora.studio`
- `ACME_EMAIL` — for Let's Encrypt

**Validate:**

```bash
source .env && ./scripts/validate-env.sh production
```

---

## 8. Caddyfile Generation (Reverse Proxy)

```bash
cd authora
./scripts/generate-caddyfile.sh
```

Uses `DOMAIN_API`, `DOMAIN_WEB`, `ACME_EMAIL` from `.env`. Output: `caddy/Caddyfile`.

---

## 9. Production Bootstrap (First Deploy)

```bash
cd authora
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh
```

Starts postgres, redis, runs migrations, builds and starts api, web, caddy.

---

## 10. Production Deploy (Subsequent)

```bash
cd authora
./scripts/deploy.sh prod
```

---

## 11. Migrations (Production)

```bash
cd authora
./scripts/db-migrate.sh --docker --prod
```

---

## 12. Seed (Production)

```bash
cd authora
./scripts/db-seed.sh --docker --prod
```

---

## 13. First Admin (Production)

```bash
cd authora
./scripts/first-admin.sh --docker --prod
```

Default: `admin@authora.local` / `admin123`

---

## 14. Health Check

```bash
cd authora
./scripts/healthcheck.sh https://api.authora.studio
```

---

## 15. Go-Live Verification

```bash
cd authora
./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio
```

---

## 16. Update Deployment

```bash
cd authora
git pull
./scripts/update.sh prod
```

---

## 17. Backup

```bash
cd authora
./scripts/backup.sh
```

Output: `./backups/authora_YYYYMMDD_HHMMSS.dump`

---

## 18. Restore

```bash
cd authora
docker compose -f docker-compose.yml -f docker-compose.prod.yml stop api web caddy
./scripts/restore.sh ./backups/authora_20250315_020000.dump
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## 19. Rollback

```bash
cd authora
./scripts/rollback.sh ./backups/authora_20250315_020000.dump prod
```

---

## 20. Firewall (Optional)

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

---

## 21. Backup Cron

```bash
crontab -e
# Add:
0 2 * * * cd /path/to/authora && ./scripts/backup.sh
```

---

## Full Flow Summary

| Step | Command |
|------|---------|
| 1. Bootstrap | `./scripts/bootstrap.sh` |
| 2. Clone | `git clone https://github.com/TorNation01/authora.git && cd authora` |
| 3. Install | `./scripts/install.sh` |
| 4. Configure | `cp .env.example .env && nano .env` |
| 5. Validate | `source .env && ./scripts/validate-env.sh production` |
| 6. Caddyfile | `./scripts/generate-caddyfile.sh` |
| 7. Deploy | `./scripts/bootstrap-prod.sh` |
| 8. First admin | `./scripts/first-admin.sh --docker --prod` |
| 9. Verify | `./scripts/verify-go-live.sh https://api.authora.studio https://authora.studio` |
