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

### One-Command Local Dev

```bash
git clone https://github.com/TorNation01/authora.git
cd authora
./scripts/install.sh
docker compose up -d postgres redis
until docker compose exec -T postgres pg_isready -U authora; do sleep 2; done
npm run db:migrate
npm run db:seed
npm run dev:api &   # Terminal 1
npm run dev         # Terminal 2
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/api/docs

### One-Command Production Deploy (Ubuntu)

```bash
./scripts/bootstrap.sh          # Fresh server: Docker, Node, Python
git clone https://github.com/TorNation01/authora.git && cd authora
./scripts/install.sh
cp .env.example .env && nano .env   # Set SECRET_KEY, DATABASE_URL, REDIS_URL, NEXT_PUBLIC_API_URL
source .env && ./scripts/validate-env.sh production
./scripts/bootstrap-prod.sh
./scripts/first-admin.sh --docker --prod
```

### Prerequisites

- **Local dev:** Node.js 18+, Python 3.11+, Docker
- **Production:** Docker, Docker Compose (see [UBUNTU_INSTALL.md](docs/UBUNTU_INSTALL.md))

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

## Documentation

| Doc | Purpose |
|-----|---------|
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Full deployment guide |
| [UBUNTU_INSTALL.md](docs/UBUNTU_INSTALL.md) | Fresh Ubuntu bootstrap |
| [UBUNTU_DEPLOY_COMMANDS.md](docs/UBUNTU_DEPLOY_COMMANDS.md) | Ubuntu deploy commands |
| [LOCAL_DEV.md](docs/LOCAL_DEV.md) | Local development |
| [OPERATIONS_QUICKSTART.md](docs/OPERATIONS_QUICKSTART.md) | Copy-paste commands |
| [QUICKSTART_COMMANDS.md](docs/QUICKSTART_COMMANDS.md) | Quickstart copy-paste |
| [GO_LIVE_CHECKLIST.md](docs/GO_LIVE_CHECKLIST.md) | Pre/post go-live validation |
| [GO_LIVE_COMMAND_CHECKLIST.md](docs/GO_LIVE_COMMAND_CHECKLIST.md) | One-page go-live commands |
| [BACKUP_AND_RESTORE.md](docs/BACKUP_AND_RESTORE.md) | Backup and restore |
| [OPERATOR_QUICK_REFERENCE.md](docs/OPERATOR_QUICK_REFERENCE.md) | Exact terminal commands |
| [OPERATOR_COMMANDS.md](docs/OPERATOR_COMMANDS.md) | Full operator command reference |
| [ANAKATECH_INTEGRATION.md](docs/ANAKATECH_INTEGRATION.md) | Anakatech ecosystem integration |
| [ANAKATECH_INTEGRATION_STRATEGY.md](docs/ANAKATECH_INTEGRATION_STRATEGY.md) | Integration strategy, standalone-first |
| [STANDALONE_VS_CONNECTED_MODE.md](docs/STANDALONE_VS_CONNECTED_MODE.md) | Standalone vs connected mode |
| [OPTIONAL_CONNECTOR_LAYER.md](docs/OPTIONAL_CONNECTOR_LAYER.md) | Optional adapter layer |
| [ANAKATECH_CONVENTIONS.md](docs/ANAKATECH_CONVENTIONS.md) | Ecosystem conventions |

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
