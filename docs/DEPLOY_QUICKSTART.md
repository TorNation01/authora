# AUTHORA Deploy Quickstart

One-command deploy: clone → copy env → run deploy → complete setup wizard → go live.

---

## Quickstart (Development)

```bash
git clone https://github.com/TorNation01/authora.git && cd authora && cp .env.example .env && ./scripts/deploy.sh
```

Or with npm:

```bash
git clone https://github.com/TorNation01/authora.git && cd authora && cp .env.example .env && npm run deploy
```

**Then:** Visit http://localhost:3000/setup to complete the setup wizard.

---

## Quickstart (Production)

```bash
git clone https://github.com/TorNation01/authora.git && cd authora
cp .env.production.example .env
# Edit .env: SECRET_KEY (openssl rand -hex 32), DATABASE_URL, REDIS_URL, domains
./scripts/deploy.sh prod
```

**Then:** Visit https://your-domain/setup to complete the setup wizard.

---

## What the Deploy Script Does

| Step | Action |
|------|--------|
| 0 | Clone repo (if not already in a valid clone) |
| 1 | Preflight: Docker, Docker Compose, Git |
| 2 | Copy `.env` from example if missing |
| 3 | Validate environment variables |
| 4 | Create directories, Caddyfile (prod) |
| 5 | Start PostgreSQL and Redis |
| 6 | Run database migrations |
| 7 | Seed database (admin bootstrap) |
| 8 | Start API, Web, and Caddy (prod) |
| 9 | Verify health checks |
| 10 | Print next actions |

---

## Requirements

- **Docker** and **Docker Compose**
- **Git**
- **Bash**

On Ubuntu, if Docker is not installed:

```bash
./scripts/bootstrap.sh   # Installs Docker, Node, Python
```

---

## Idempotent

Safe to re-run. The script will:

- Skip clone if already in a valid repo
- Use existing `.env` if present
- Re-run migrations (idempotent)
- Skip seed if users already exist

---

## Failure Messages

| Error | Fix |
|-------|-----|
| Missing Docker | `sudo apt install docker.io docker-compose-plugin` or run `./scripts/bootstrap.sh` |
| Docker daemon not reachable | `sudo systemctl start docker` or add user to docker group |
| Clone failed | Install git: `sudo apt install git` |
| .env required (prod) | Copy `.env.production.example` to `.env`, edit, then re-run |
| SECRET_KEY must be changed | Run `openssl rand -hex 32` and set in `.env` |
| Migrations failed | Check `docker compose logs api`; run manually: `docker compose run --rm api alembic upgrade head` |
| Health check failed | Wait 30s; run `./scripts/healthcheck.sh http://localhost:8000` |

---

## Next Actions After Deploy

1. **Complete setup wizard** – `/setup`
2. **Create first admin** – or use seeded `admin@authora.local` / `admin123` (dev only)
3. **Sign in** – `/login`
4. **Production:** Configure backup cron: `0 2 * * * /path/to/scripts/backup.sh`
