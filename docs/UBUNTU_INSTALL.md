# AUTHORA Ubuntu Server Install

Exact commands for installing AUTHORA on a fresh Ubuntu 22.04 or 24.04 server.

## 1. Fresh Ubuntu Bootstrap

Run this on a clean Ubuntu server (as a user with sudo):

```bash
# One-command bootstrap (installs Docker, Docker Compose, Git, Node, Python)
curl -fsSL https://raw.githubusercontent.com/TorNation01/authora/main/scripts/bootstrap.sh -o /tmp/bootstrap.sh
chmod +x /tmp/bootstrap.sh
/tmp/bootstrap.sh
```

Or if you already have the repo cloned:

```bash
cd /path/to/authora
chmod +x scripts/*.sh
./scripts/bootstrap.sh
```

**What it installs:**
- `apt-transport-https`, `ca-certificates`, `curl`, `gnupg`, `git`, `jq`, `unzip`
- Docker (via get.docker.com)
- Docker Compose plugin
- Node.js 20 LTS (for setup wizard, local dev)
- Python 3 (for local migrations)

**After Docker install:** Log out and back in so `docker` works without sudo.

## 2. Apt Packages (Manual Alternative)

If you prefer manual install:

```bash
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release \
  software-properties-common git jq unzip python3 python3-pip python3-venv
```

## 3. Docker Install (Manual)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Log out and back in
```

## 4. Docker Compose

```bash
sudo apt-get install -y docker-compose-plugin
```

## 5. Node.js 20 (Optional, for setup wizard)

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 6. Firewall (Optional)

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## 7. Clone and Install

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
./scripts/install.sh
```

## 8. Configure Environment

```bash
cp .env.example .env
nano .env
# Set: SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL
# For production: DOMAIN_API, DOMAIN_WEB, ACME_EMAIL
```

Generate SECRET_KEY:
```bash
openssl rand -hex 32
```

## 9. Production Deploy

```bash
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh
```

Or one-command deploy:
```bash
npm run deploy:prod
```

## 10. First Admin

```bash
./scripts/first-admin.sh --docker --prod
# Default: admin@authora.local / admin123 — change immediately
```
