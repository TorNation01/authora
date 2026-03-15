# AUTHORA Production Architecture

> Production-grade architecture supporting standalone self-hosted, cloud SaaS, and future Anakatech integration modes.

---

## 1. Repository Tree

```
authora/
├── apps/
│   ├── web/                      # Next.js 14 frontend (App Router)
│   │   ├── src/
│   │   │   ├── app/              # Routes, layouts
│   │   │   ├── components/       # UI, editor, domain components
│   │   │   ├── features/         # Feature-specific modules
│   │   │   ├── lib/              # Client utils, hooks
│   │   │   └── providers/        # Context, feature flags
│   │   └── public/
│   │
│   ├── api/                      # FastAPI backend
│   │   ├── authora/
│   │   │   ├── api/              # Routes, middleware, deps
│   │   │   ├── domains/          # Domain modules (see §2)
│   │   │   ├── services/         # Application services
│   │   │   ├── infrastructure/   # DB, cache, storage, queues
│   │   │   └── core/             # Config, errors, telemetry
│   │   ├── alembic/
│   │   └── tests/
│   │
│   └── worker/                   # Background job processor
│       ├── authora_worker/
│       │   ├── jobs/             # Job handlers
│       │   ├── consumers/         # Event/queue consumers
│       │   └── core/
│       └── tests/
│
├── packages/
│   ├── shared/                   # Shared types, constants, schemas
│   │   ├── src/
│   │   │   ├── contracts/        # API contracts, events
│   │   │   ├── schemas/          # Pydantic + Zod schemas
│   │   │   └── constants/
│   │   └── package.json
│   │
│   ├── storage-abstraction/      # Storage provider interface + impls
│   │   ├── src/
│   │   │   ├── providers/        # Local, S3, R2, GCS
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   ├── ai-provider/              # AI provider abstraction
│   │   ├── src/
│   │   │   ├── providers/        # OpenAI, Anthropic, local/fallback
│   │   │   └── index.ts
│   │   └── package.json
│   │
│   └── export-engine/            # Export service abstraction
│       ├── src/
│       │   ├── formats/          # DOCX, PDF, EPUB, TXT
│       │   └── index.ts
│       └── package.json
│
├── docker/
│   ├── Dockerfile.web
│   ├── Dockerfile.api
│   ├── Dockerfile.worker
│   └── docker-compose*.yml
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
│   └── BACKUP-RESTORE.md
│
├── .github/workflows/
├── package.json                  # Workspace root
├── pyproject.toml                # Python workspace (optional)
└── README.md
```

---

## 2. App Boundaries

| App | Responsibility | Port | Deployment |
|-----|----------------|------|------------|
| **web** | SPA/SSR, auth UI, editor, dashboards, setup wizard | 3000 | Next.js |
| **api** | REST/GraphQL API, auth, domain logic, orchestration | 8000 | FastAPI |
| **worker** | Async jobs, event processing, scheduled tasks | - | Long-running process |

**Boundary rules:**
- Web never talks to DB directly; only to API.
- API delegates heavy work to worker via queues.
- Worker reads/writes via API or shared DB with defined boundaries.
- Shared packages are consumed by web and api; no circular deps.

---

## 3. Service Boundaries (Domain Modules)

### 3.1 Domain Map

| Domain | API Module | Worker Jobs | Key Entities |
|--------|------------|-------------|--------------|
| **1. Identity & Auth** | `auth` | token cleanup, session invalidation | User, Session, OAuthProvider |
| **2. User Profile & Preferences** | `users` | - | UserProfile, Preferences |
| **3. Book Projects** | `projects` | - | Project |
| **4. Fiction Planning** | `fiction_planner` | - | FictionPlan, Character, PlotPoint |
| **5. Non-Fiction Planning** | `nonfiction_planner` | - | NonfictionPlan, Outline |
| **6. Chapters/Scenes/Sections** | `chapters` | word count sync | Chapter, Scene, Section |
| **7. Rich Text & Editor State** | `documents` | - | Document, EditorState |
| **8. Notes/Highlights/Comments** | `annotations` | - | Note, Highlight, Comment |
| **9. AI Assist Actions** | `ai_assist` | batch suggestions | AIRequest, AIResponse |
| **10. Accountability Goals** | `goals` | reminder jobs | Goal, Reminder |
| **11. Gamification** | `gamification` | streak calc, achievement check | Streak, Achievement, XP |
| **12. Editing Analysis** | `insights` | analysis jobs | WritingInsight, Readability |
| **13. Dictionary/Thesaurus** | `reference` | - | (external API) |
| **14. Export Generation** | `export` | export jobs | ExportJob, ExportArtifact |
| **15. Publishing Prep** | `publishing` | asset generation | Cover, Metadata, ISBN |
| **16. Notifications** | `notifications` | send jobs | Notification, Channel |
| **17. Billing** | `billing` | usage sync, invoice | Subscription, Usage, Invoice |
| **18. Admin & Observability** | `admin` | - | AuditLog, FeatureFlag, Metric |

### 3.2 Cross-Cutting Services

| Service | Responsibility | Abstraction |
|---------|----------------|-------------|
| **Storage** | File/blob storage (exports, uploads, assets) | `StorageProvider` interface |
| **AI Provider** | LLM completions, embeddings | `AIProvider` interface |
| **Export Engine** | Format conversion (DOCX, PDF, EPUB) | `ExportEngine` interface |
| **Notification** | Email, in-app, push | `NotificationChannel` interface |
| **Audit** | Action logging, compliance | `AuditLogger` |
| **Telemetry** | Metrics, traces, logs | `Telemetry` |
| **Feature Flags** | Toggle features by user/tenant/env | `FeatureFlagService` |

---

## 4. API Contracts

### 4.1 API Structure

```
/api/v1/
├── auth/                 # Identity & Auth
│   ├── POST   /register
│   ├── POST   /login
│   ├── POST   /refresh
│   ├── POST   /logout
│   ├── GET    /me
│   └── POST   /forgot-password
│
├── users/                # User Profile & Preferences
│   ├── GET    /me
│   ├── PATCH  /me
│   └── GET    /me/preferences
│
├── projects/             # Book Projects
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /:id
│   ├── PATCH  /:id
│   └── DELETE /:id
│
├── projects/:pid/books/  # Books (fiction/nonfiction)
│   ├── GET    /
│   ├── POST   /
│   ├── GET    /:id
│   ├── PATCH  /:id
│   └── DELETE /:id
│
├── books/:bid/
│   ├── fiction-plan/     # Fiction Planning
│   │   ├── GET
│   │   └── PUT
│   ├── nonfiction-plan/  # Non-Fiction Planning
│   │   ├── GET
│   │   └── PUT
│   ├── chapters/         # Chapters/Scenes/Sections
│   │   ├── GET    /
│   │   ├── POST   /
│   │   ├── GET    /:id
│   │   ├── PATCH  /:id
│   │   └── DELETE /:id
│   ├── documents/        # Rich Text & Editor State
│   │   ├── GET    /:docId
│   │   └── PATCH  /:docId
│   ├── annotations/      # Notes/Highlights/Comments
│   │   ├── GET    /
│   │   ├── POST   /
│   │   ├── PATCH  /:id
│   │   └── DELETE /:id
│   └── notes/            # Research notes
│       ├── GET    /
│       ├── POST   /
│       ├── PATCH  /:id
│       └── DELETE /:id
│
├── ai/                   # AI Assist Actions
│   ├── POST   /complete          # Streaming
│   ├── POST   /suggest
│   └── POST   /analyze
│
├── goals/                # Accountability Goals
│   ├── GET    /
│   ├── POST   /
│   ├── PATCH  /:id
│   └── DELETE /:id
│
├── gamification/         # Gamification
│   ├── GET    /stats
│   ├── GET    /achievements
│   └── GET    /streaks
│
├── reference/            # Dictionary/Thesaurus
│   ├── GET    /dictionary/lookup
│   └── GET    /dictionary/thesaurus
│
├── export/               # Export Generation
│   ├── POST   /books/:id          # Create export job
│   ├── GET    /jobs/:id           # Job status
│   └── GET    /jobs/:id/download  # Download artifact
│
├── publishing/           # Publishing Prep
│   ├── GET    /books/:id/assets
│   └── POST   /books/:id/assets
│
├── notifications/        # Notifications
│   ├── GET    /
│   ├── PATCH  /:id/read
│   └── GET    /preferences
│
├── billing/              # Billing (abstraction)
│   ├── GET    /subscription
│   ├── GET    /usage
│   └── GET    /invoices
│
└── admin/                # Admin & Observability
    ├── GET    /audit-logs
    ├── GET    /feature-flags
    ├── PATCH  /feature-flags/:key
    └── GET    /health
```

### 4.2 Shared Schemas (packages/shared)

See `docs/API-CONTRACTS.md` for full OpenAPI-style schemas. Key shared types:

- `User`, `UserProfile`, `Preferences`
- `Project`, `Book`, `Chapter`, `Document`
- `FictionPlan`, `NonfictionPlan`
- `Goal`, `Reminder`, `Streak`, `Achievement`
- `ExportJob`, `ExportFormat`
- `Notification`, `NotificationPreferences`
- `AuditLog`, `FeatureFlag`

---

## 5. Queue & Job Design

### 5.1 Queue Topology

```
queues/
├── export.jobs           # Export generation (DOCX, PDF, EPUB)
├── ai.batch              # Batch AI requests (analysis, suggestions)
├── notifications.send    # Send email/push/in-app
├── insights.analyze      # Writing analysis, readability
├── gamification.sync     # Streak/achievement recalculation
├── reminders.trigger     # Goal reminders
└── audit.flush           # Batch audit log writes (optional)
```

### 5.2 Job Types

| Job | Queue | Trigger | Retries | Timeout |
|-----|-------|---------|---------|---------|
| `export.generate` | export.jobs | API request | 3 | 5m |
| `ai.complete_batch` | ai.batch | API or scheduled | 2 | 2m |
| `notification.send` | notifications.send | Event | 5 | 30s |
| `insights.analyze_document` | insights.analyze | Document save | 2 | 1m |
| `gamification.recalc_streak` | gamification.sync | Daily / event | 2 | 30s |
| `reminders.dispatch` | reminders.trigger | Cron (every 15m) | 1 | 1m |

### 5.3 Job Payload Schema

```json
{
  "job_id": "uuid",
  "type": "export.generate",
  "payload": { "book_id": "uuid", "format": "docx", "user_id": "uuid" },
  "created_at": "ISO8601",
  "retry_count": 0
}
```

---

## 6. Event Design

### 6.1 Event Types (Domain Events)

| Event | Source | Consumers | Payload |
|-------|--------|------------|---------|
| `user.registered` | auth | notifications, billing | user_id |
| `user.logged_in` | auth | audit | user_id, ip |
| `book.created` | projects | - | book_id, project_id |
| `chapter.updated` | chapters | insights, gamification | chapter_id, word_delta |
| `document.saved` | documents | insights | document_id |
| `goal.created` | goals | reminders | goal_id, deadline |
| `goal.completed` | goals | gamification | goal_id |
| `export.requested` | export | worker | export_job_id |
| `export.completed` | worker | notifications | export_job_id, url |

### 6.2 Event Schema

```json
{
  "id": "uuid",
  "type": "chapter.updated",
  "source": "api",
  "timestamp": "ISO8601",
  "user_id": "uuid",
  "tenant_id": "uuid",
  "payload": {},
  "metadata": {}
}
```

### 6.3 Transport

- **Standalone**: Redis Streams or in-process event bus
- **SaaS**: Redis Streams / RabbitMQ / SQS
- **Anakatech**: Shared message bus (TBD)

---

## 7. Database Design Overview

### 7.1 Schema Groups

| Group | Tables | Purpose |
|-------|--------|---------|
| **Identity** | users, sessions, oauth_providers | Auth, sessions |
| **Profile** | user_profiles, preferences | Profile, settings |
| **Projects** | projects, books | Project hierarchy |
| **Planning** | fiction_plans, characters, plot_points, nonfiction_plans, outlines | Planning data |
| **Content** | chapters, documents, editor_states | Chapters, rich text |
| **Annotations** | notes, highlights, comments | Notes, comments |
| **AI** | ai_requests, ai_responses | AI usage, cost tracking |
| **Accountability** | goals, reminders, reminder_logs | Goals, reminders |
| **Gamification** | user_stats, achievements, streak_logs | Streaks, XP |
| **Insights** | writing_insights, readability_scores | Analysis cache |
| **Export** | export_jobs, export_artifacts | Export queue, results |
| **Publishing** | publishing_assets, covers | Prep assets |
| **Notifications** | notifications, notification_preferences | In-app, prefs |
| **Billing** | subscriptions, usage_records, invoices | Billing abstraction |
| **System** | audit_logs, feature_flags, settings | Admin, config |

### 7.2 Multi-Tenancy

- **Standalone**: Single tenant; `tenant_id` = default UUID
- **SaaS**: `tenant_id` on all tenant-scoped tables; row-level filtering
- **Anakatech**: `tenant_id` maps to org; shared auth/identity

### 7.3 Key Indexes

- `(tenant_id, user_id)` on user-scoped tables
- `(book_id, sort_order)` on chapters
- `(user_id, date)` on streak_logs
- `(created_at)` on audit_logs (partitioned by month)

---

## 8. Environment Variable Map

### 8.1 Core

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NODE_ENV` | No | development | development \| production |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `REDIS_URL` | Yes* | redis://localhost:6379/0 | Redis for cache, queues, sessions |
| `SECRET_KEY` | Yes | - | JWT signing, encryption |
| `CORS_ORIGINS` | No | http://localhost:3000 | JSON array of origins |

*Optional in minimal standalone (no worker, no queues)

### 8.2 Storage

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `STORAGE_PROVIDER` | No | local | local \| s3 \| r2 \| gcs |
| `STORAGE_LOCAL_PATH` | If local | ./storage | Local filesystem path |
| `AWS_ACCESS_KEY_ID` | If S3/R2 | - | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | If S3/R2 | - | AWS credentials |
| `AWS_REGION` | If S3 | - | AWS region |
| `S3_BUCKET` | If S3 | - | Bucket name |
| `R2_ACCOUNT_ID` | If R2 | - | Cloudflare R2 |
| `R2_BUCKET` | If R2 | - | R2 bucket |

### 8.3 AI

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AI_PROVIDER` | No | openai | openai \| anthropic \| none |
| `OPENAI_API_KEY` | If OpenAI | - | OpenAI key |
| `ANTHROPIC_API_KEY` | If Anthropic | - | Anthropic key |
| `AI_MODEL` | No | gpt-4o-mini | Model name |
| `AI_MAX_TOKENS` | No | 2048 | Max completion tokens |

### 8.4 Notifications

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOTIFICATION_EMAIL_PROVIDER` | No | none | smtp \| sendgrid \| ses |
| `SMTP_HOST` | If SMTP | - | SMTP host |
| `SMTP_PORT` | If SMTP | 587 | SMTP port |
| `SENDGRID_API_KEY` | If SendGrid | - | SendGrid key |

### 8.5 Telemetry

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEMETRY_ENABLED` | No | false | Enable metrics/traces |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | If telemetry | - | OTLP endpoint |
| `SENTRY_DSN` | No | - | Sentry error tracking |

### 8.6 Feature Flags

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `FEATURE_FLAGS_PROVIDER` | No | database | database \| launchdarkly \| env |
| `LAUNCHDARKLY_SDK_KEY` | If LD | - | LaunchDarkly key |

### 8.7 Deployment Mode

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEPLOYMENT_MODE` | No | standalone | standalone \| saas \| anakatech |
| `TENANT_ID` | If standalone | - | Default tenant UUID |
| `API_PUBLIC_URL` | Yes (prod) | - | Public API URL |
| `WEB_PUBLIC_URL` | Yes (prod) | - | Public web URL |

---

## 9. Dependency Map

```
                    ┌─────────────┐
                    │    web      │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │  shared  │ │  storage  │ │ ai-prov  │
       └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │     api     │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │  shared  │ │  storage  │ │ export   │
       │  (py)    │ │  (py)     │ │ engine   │
       └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           │
                    ┌──────▼──────┐
                    │   worker    │
                    └─────────────┘
```

**Rules:**
- `shared` has no app dependencies
- `storage`, `ai-provider`, `export-engine` depend only on `shared`
- `api` depends on all abstractions
- `worker` depends on `api` contracts and shared infra (DB, Redis, queues)

---

## 10. Security Architecture

### 10.1 Authentication

- **Mechanism**: JWT access tokens (short-lived) + refresh tokens (long-lived, stored)
- **Storage**: Access in memory/header; refresh in httpOnly cookie or secure storage
- **OAuth**: Optional OAuth2 providers (Google, GitHub) via `oauth_providers` table

### 10.2 Authorization

- **Model**: RBAC + resource-level (user owns project → book → chapter)
- **Checks**: Middleware/deps verify `user_id` or `tenant_id` + role
- **Admin**: `is_admin` flag; admin routes require admin role

### 10.3 Data Protection

- **At rest**: DB encryption (provider-managed); storage encryption (S3/R2 SSE)
- **In transit**: TLS everywhere (API, web, DB connections)
- **Secrets**: Env vars, secret manager in cloud (e.g. AWS Secrets Manager)

### 10.4 Input Validation

- Pydantic schemas on all API inputs
- Rate limiting per user/IP
- File upload: type/size validation; virus scan optional

### 10.5 Audit

- All mutating actions logged to `audit_logs` (who, what, when, resource)
- Sensitive fields redacted in logs
- Retention policy configurable

---

## 11. Backup & Restore Strategy

### 11.1 Database

- **Frequency**: Daily full backup; WAL archiving for PITR (production)
- **Retention**: 7 daily, 4 weekly, 12 monthly
- **Storage**: Same region as DB; encrypted
- **Restore**: Documented runbook; test restore quarterly

### 11.2 File Storage

- **Exports, uploads**: Versioned bucket or daily snapshots
- **Retention**: Align with data retention policy

### 11.3 Redis

- **RDB snapshots**: Hourly if persistence enabled
- **Use case**: Session/cache recovery; queues are ephemeral

### 11.4 Restore Procedure

1. Restore DB from backup
2. Restore file storage if needed
3. Restart API and worker
4. Verify health endpoints
5. Run smoke tests

---

## 12. Deployment Modes

### 12.1 Standalone (Self-Hosted)

- Single-tenant
- All services on one or few nodes
- Local/S3 storage
- No billing logic; feature flags from DB/env
- Setup wizard creates admin, configures env

### 12.2 SaaS (Cloud)

- Multi-tenant
- API/worker scaled horizontally
- S3/R2 storage; Redis Cluster
- Billing integration (Stripe abstraction)
- Feature flags (LaunchDarkly or DB)
- Telemetry enabled

### 12.3 Anakatech Integration

- Tenant = organization
- Shared identity/SSO
- Events published to Anakatech bus
- Billing delegated to Anakatech
- Feature flags from Anakatech config

---

## 13. Setup Wizard System

### 13.1 Flow

1. **Detect first run**: No users in DB or `setup_complete` = false
2. **Health checks**: DB, Redis, storage (if configured)
3. **Config steps**:
   - Database URL
   - Redis URL
   - Secret key
   - Storage provider (local/S3/R2)
   - AI provider + keys (optional)
   - Email (optional)
4. **Admin user**: Create first admin account
5. **Finalize**: Set `setup_complete`; redirect to dashboard

### 13.2 Implementation

- **CLI**: `scripts/setup-wizard.mjs` (interactive)
- **Web**: `/setup` page (guided UI)
- **API**: `POST /api/v1/setup/complete` (idempotent, admin-only after first run)

---

## 14. Admin & Settings System

### 14.1 Admin Panel

- **Access**: `is_admin` users only
- **Features**: User list, audit log viewer, feature flags, system health
- **Routes**: `/admin/*` (protected)

### 14.2 Settings

- **User**: Preferences, notification prefs (in `users` domain)
- **System**: Key-value in `settings` table; admin-editable
- **Feature flags**: Per-tenant or global; toggled via admin UI or API
