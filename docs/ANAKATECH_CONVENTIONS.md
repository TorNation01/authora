# Anakatech Ecosystem Conventions

Standard conventions for products in the Anakatech ecosystem. AUTHORA aligns with these.

## 1. Environment Naming

| Convention | Pattern | Example |
|------------|---------|---------|
| Deployment mode | `APP_MODE` or `DEPLOYMENT_MODE` | `standalone` \| `anakatech` \| `white_label` |
| Integration toggles | `ENABLE_*` | `ENABLE_SSO`, `ENABLE_SHARED_NAV` |
| Branding overrides | `BRANDING_*` | `BRANDING_PRODUCT_NAME`, `BRANDING_LOGO_URL` |
| Feature flags | `FEATURE_*` | `FEATURE_SSO_READY`, `FEATURE_BILLING` |
| Gateway / public URL | `API_GATEWAY_URL`, `API_PUBLIC_URL` | Gateway for Anakatech routing |
| Frontend API URL | `NEXT_PUBLIC_API_URL` | Browser-visible API base |
| App-specific prefix | Optional `{APP}_*` | `AUTHORA_*` for app-specific overrides |

## 2. Deployment Script Naming

| Script | Purpose |
|--------|---------|
| `install.sh` | System dependencies, initial setup |
| `bootstrap.sh` | Full dev environment |
| `bootstrap-dev.sh` | Dev-specific bootstrap |
| `bootstrap-prod.sh` | Production bootstrap |
| `deploy.sh` | Deploy to target |
| `backup.sh` | Database backup |
| `restore.sh` | Database restore |
| `db-migrate.sh` | Run migrations |
| `healthcheck.sh` | Health verification |
| `validate-env.sh` | Environment validation |
| `first-admin.sh` | Create first admin user |

## 3. Folder Structure

```
apps/
  api/          # Backend API
  web/          # Frontend
  worker/       # Background jobs (optional)
docs/           # Documentation
scripts/        # Deployment and ops scripts
docker/         # Dockerfiles
```

## 4. Shared Logging Conventions

- **Structured logging**: Use structlog or equivalent with consistent keys
- **Standard keys**: `request_id`, `app`, `event`, `level`, `timestamp`
- **App identifier**: Bind `app` (e.g. `authora`) for log aggregation
- **Event naming**: `audit_request`, `reminder_cron_completed`, etc.

## 5. Shared Audit / Event Conventions

When forwarding to Anakatech:

| Field | Type | Description |
|-------|------|-------------|
| `app` | string | Product identifier (e.g. `authora`) |
| `action` | string | Action type (e.g. `request`, `create`, `login`) |
| `resource` | string | Resource path or type |
| `resource_id` | string? | Optional resource ID |
| `user_id` | string? | User ID when authenticated |
| `details` | object? | Additional context |
| `ip_address` | string? | Client IP |
| `timestamp` | string | ISO 8601 |
| `source` | string | `authora` or product name |

## 6. Shared Integration Mode Conventions

- **APP_MODE** values: `standalone` | `anakatech` | `white_label`
- **Integration layer**: Isolated in `{app}/integration/` or equivalent
- **Registry pattern**: Central `IntegrationRegistry` for feature-flag checks
- **Adapters**: No-op when integration disabled; optional and configurable

## 7. Shared Admin / Operator Patterns

- **Admin prefix**: `/admin` or `/api/v1/admin`
- **Admin-only**: Require admin role; no public access
- **Standard admin routes**: users, feature-flags, health, audit, errors, storage
- **First admin**: Script or setup wizard for bootstrap

## 8. Shared Documentation Patterns

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview, quick start |
| `docs/ENV-MAP.md` | Environment variable reference |
| `docs/DEPLOYMENT.md` | Deployment instructions |
| `docs/OPERATIONS_QUICKSTART.md` | Copy-paste ops commands |
| `docs/OPERATOR_QUICK_REFERENCE.md` | Exact terminal commands for operators |
| `docs/GO_LIVE_CHECKLIST.md` | Pre/post go-live validation |
| `docs/ANAKATECH_INTEGRATION.md` | Integration guide |
| `docs/ANAKATECH_CONVENTIONS.md` | Ecosystem conventions |
| `docs/BACKUP_AND_RESTORE.md` | Backup/restore procedures |

## 9. Shared Branding Patterns

- **Config endpoint**: `GET /api/v1/config` or `GET /api/v1/config/branding`
- **Branding fields**: `product_name`, `tagline`, `logo_url`, `favicon_url`, `primary_color`, `show_powered_by`
- **Override via env**: `BRANDING_*` variables

## 10. Setup Wizard Conventions

- **Purpose**: First-run configuration for standalone deployments
- **Path**: `GET/POST /api/v1/setup/*` or `/setup/*`
- **Standard routes**: `status`, `test`, `apply`, `finalize`
- **Standalone-only**: Setup wizard is disabled when `APP_MODE=anakatech` or `white_label`; Anakatech mode uses centralized provisioning
- **Status response**: `setup_complete`, `has_users`, `can_connect`
- **Script**: Optional `scripts/setup-wizard.mjs` or equivalent for CLI setup

## 11. Health Check Conventions

- **Liveness**: `GET /health` — minimal check; returns `status`, `app`, optionally `version`
- **Readiness**: `GET /health/ready` — checks DB, Redis, etc.; returns `status`, `checks`, `app`; 503 when degraded
- **Response shape**: `{ "status": "ok"|"ready"|"degraded", "app": "<product>", "checks": {...} }`
- **Script**: `scripts/healthcheck.sh` — calls `/health` and optionally `/health/ready`
- **Skip rate limit**: Health endpoints excluded from rate limiting

## 12. Feature Flag Conventions

- **Env prefix**: `FEATURE_*` (e.g. `FEATURE_SSO_READY`, `FEATURE_BILLING`)
- **Override hierarchy**: Env (base) → DB (`Setting feature.*`) → runtime
- **Config endpoint**: `GET /api/v1/config` or `GET /api/v1/config/mode` returns merged `feature_flags`
- **Admin**: Feature flags editable via admin UI when DB-backed
- **Naming**: Snake_case keys in API; env vars use `FEATURE_` prefix

## 13. Security Conventions

- **Headers**: `X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`, `Referrer-Policy`, `Permissions-Policy`
- **Request ID**: `X-Request-ID` on requests and responses for tracing
- **Rate limiting**: Per-IP, per-path; skip health/docs; configurable limits
- **PII-safe errors**: 500 responses return generic message; `request_id` for support lookup
- **Docs**: `docs/SECURITY.md`, `docs/SECURITY-CHECKLIST.md`

---

## Intentional Differences (AUTHORA)

| Area | Difference | Reason |
|------|-------------|--------|
| Setup wizard | Standalone-only; 404 in Anakatech mode | Anakatech uses centralized provisioning; no first-run wizard needed |
| Health path | `/health`, `/health/ready` (no `/api/v1` prefix) | Simpler for load balancers and Docker HEALTHCHECK |
