# AUTHORA

AI-powered book builder and writing studio for fiction and non-fiction authors. A guided writing journey from idea to finished book.

## Features

- **Guided journey**: Step-by-step planning, outlining, writing, editing, and exporting
- **Writing studio**: TipTap-based editor with chapter management
- **AI assistance**: OpenAI/Anthropic integration for writing help
- **Accountability**: Streaks, goals, achievements
- **Export**: DOCX, PDF, EPUB, TXT
- **Dictionary/Thesaurus**: Built-in lookup (Free Dictionary API)

## Tech Stack

- **Frontend**: Next.js 14, TypeScript, Tailwind, shadcn/ui, TipTap
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Worker**: Background jobs (export, notifications, insights)
- **Deployment**: Docker Compose

## Architecture

See [docs/ARCHITECTURE-PRODUCTION.md](docs/ARCHITECTURE-PRODUCTION.md) for the full production architecture:

- App boundaries (web, api, worker)
- Domain modules (18 domains)
- Storage, AI, export, notification abstractions
- Queue/job design, event design
- Database design, env map, security, backup

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 16
- Redis 7

### 1. Clone and install

```bash
git clone <repo>
cd authora
npm install
pip install -e apps/api
```

### 2. Environment

```bash
cp .env.example .env
# Edit .env with your database URL, Redis URL, and optional AI keys
```

### 3. Database

```bash
# Start Postgres and Redis (Docker)
docker compose up -d postgres redis

# Run migrations
cd apps/api && alembic upgrade head

# Seed demo admin (optional)
python -m authora.scripts.seed
# Admin: admin@authora.local / admin123
```

### 4. Run

```bash
# Terminal 1 - API
npm run dev:api

# Terminal 2 - Web
npm run dev
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/api/docs

## Setup Wizard

```bash
npm run setup
```

Guides you through database URL, Redis, secret key, and optional AI API keys.

## Docker

```bash
docker compose up -d
```

- Web: http://localhost:3000
- API: http://localhost:8000

## Project Structure

```
authora/
├── apps/
│   ├── api/          # FastAPI backend
│   └── web/          # Next.js frontend
├── packages/
│   └── shared/       # Shared types
├── docker/
├── scripts/
├── docs/
└── .github/workflows/
```

## API Keys (Optional)

- **OpenAI**: For GPT-based writing assistance. Add `OPENAI_API_KEY` to `.env`
- **Anthropic**: Alternative AI. Add `ANTHROPIC_API_KEY` and set `AI_PROVIDER=anthropic`
- **Dictionary**: Free Dictionary API - no key required

## License

Proprietary - Anakatech Legal Collective
