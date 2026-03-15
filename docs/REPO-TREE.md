# AUTHORA Repository Tree

```
authora/
├── apps/
│   ├── web/                          # Next.js 14 frontend
│   │   ├── src/
│   │   │   ├── app/                  # App Router, pages, layouts
│   │   │   ├── components/           # UI, editor, domain components
│   │   │   ├── features/             # Feature modules
│   │   │   ├── lib/                  # API client, utils, hooks
│   │   │   └── providers/            # Auth, feature flags
│   │   ├── package.json
│   │   └── next.config.js
│   │
│   ├── api/                           # FastAPI backend
│   │   ├── authora/
│   │   │   ├── api/                   # Routes, middleware, deps
│   │   │   ├── core/                  # Config, audit, telemetry, feature flags
│   │   │   ├── domains/               # (Future) Domain modules
│   │   │   ├── infrastructure/        # Storage, AI, export, notifications
│   │   │   │   ├── storage/           # Local, S3, R2
│   │   │   │   ├── ai_provider/       # OpenAI, Anthropic, Null
│   │   │   │   ├── export_engine/     # DOCX, PDF, EPUB, TXT
│   │   │   │   └── notifications/     # In-app, email
│   │   │   ├── models/                # SQLAlchemy models
│   │   │   ├── schemas/               # Pydantic schemas
│   │   │   ├── services/              # Business logic
│   │   │   └── main.py
│   │   ├── alembic/
│   │   └── tests/
│   │
│   └── worker/                        # Background job processor
│       ├── authora_worker/
│       │   ├── jobs/                  # Job handlers
│       │   ├── consumers/             # Queue consumers
│       │   └── main.py
│       └── pyproject.toml
│
├── packages/
│   └── shared/                        # Shared types, contracts
│       ├── src/
│       │   ├── contracts/             # Events, API contracts
│       │   ├── types.ts
│       │   └── constants.ts
│       └── package.json
│
├── docker/
│   ├── Dockerfile.web
│   ├── Dockerfile.api
│   └── Dockerfile.worker
│
├── scripts/
│   ├── setup-wizard.mjs
│   ├── deploy.sh
│   ├── backup.sh
│   └── restore.sh
│
├── docs/
│   ├── ARCHITECTURE-PRODUCTION.md
│   ├── API-CONTRACTS.md
│   ├── EVENTS-QUEUES.md
│   ├── DATABASE-DESIGN.md
│   ├── ENV-MAP.md
│   ├── SECURITY.md
│   ├── BACKUP-RESTORE.md
│   └── REPO-TREE.md
│
├── .github/workflows/
├── package.json
├── docker-compose.yml
└── README.md
```
