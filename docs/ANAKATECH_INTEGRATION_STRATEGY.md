# Anakatech Integration Strategy

AUTHORA is designed **standalone-first**. Anakatech integration is an optional connector layer added after the product is stable. AUTHORA must remain independently deployable; the Anakatech connector is never required for core operation.

## Guiding Principles

1. **Standalone is default** — AUTHORA runs fully without any Anakatech dependency.
2. **Integration is additive** — Anakatech features layer on top; they do not replace core logic.
3. **No tight coupling** — Core product modules never import Anakatech-specific code.
4. **Environment-driven** — Integration is toggled via `DEPLOYMENT_MODE` and `ENABLE_*` flags.
5. **Stability first** — Add Anakatech integration only after standalone is production-ready.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Optional unified admin/portal integration (future)    │
├─────────────────────────────────────────────────────────────────┤
│  Layer 4: Optional analytics/reporting handoff                   │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Optional shared auth / ecosystem identity (SSO-ready)  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Optional connector / integration adapter layer         │
│           (authora/integration/*)                                │
├─────────────────────────────────────────────────────────────────┤
│  Layer 1: Standalone core (always present)                      │
│           Auth, billing, storage, API, web                       │
└─────────────────────────────────────────────────────────────────┘
```

## What Remains Standalone

| Area | Standalone Behavior | Never Coupled To |
|------|---------------------|------------------|
| **Auth** | Local email/password, JWT, sessions | Anakatech IdP, gateway auth |
| **Billing** | Internal plans, Stripe, admin grants | Anakatech entitlement API |
| **Storage** | Local filesystem, S3, R2 | Anakatech shared storage |
| **Database** | PostgreSQL, migrations, models | Anakatech data stores |
| **API** | REST, OpenAPI, versioned routes | Anakatech gateway contracts |
| **Web** | Next.js, full UI, setup wizard | Anakatech portal shell |
| **Deployment** | Docker Compose, one-command deploy | Anakatech infra |
| **Health** | `/health`, `/health/ready` | Anakatech health aggregation |

## What Can Be Integrated Later

| Area | Integration Point | When Enabled |
|------|-------------------|--------------|
| **Identity** | SSO redirect, token exchange | `ENABLE_SSO=true` + `DEPLOYMENT_MODE=anakatech` |
| **Navigation** | Embeddable shell, workspace launcher | `ENABLE_SHARED_NAV=true` |
| **Notifications** | Forward to shared notification center | `ENABLE_SHARED_NOTIFICATIONS=true` |
| **Analytics** | Audit/analytics event forwarding | `ENABLE_SHARED_ANALYTICS=true` |
| **Billing** | Anakatech entitlement checks (fallback) | `ENABLE_SHARED_BILLING=true` |
| **Branding** | Override product name, logo, colors | `ENABLE_BRAND_OVERRIDES=true` |
| **Admin/Portal** | Embed in unified admin (future) | TBD |

## What Should Never Be Tightly Coupled

- **Core domain logic** — Projects, books, chapters, AI, export, accountability
- **Database schema** — No Anakatech-specific tables required for core operation
- **API contracts** — AUTHORA API is self-contained; no Anakatech types in public schemas
- **Deployment scripts** — `deploy.sh`, `bootstrap-prod.sh` work without Anakatech
- **Tests** — Core tests run in standalone mode; integration tests are separate
- **Dependencies** — No required Anakatech SDK or library in `pyproject.toml` / `package.json`

## Clean APIs for Ecosystem Interoperability

To support future ecosystem integration without coupling, AUTHORA exposes:

### 1. Webhooks (outbound)

| Event | Payload | Use Case |
|-------|---------|----------|
| `project.created` | `{ project_id, user_id, name }` | Sync to ecosystem catalog |
| `book.completed` | `{ book_id, project_id, user_id }` | Analytics, reporting |
| `export.completed` | `{ export_id, format, user_id }` | Usage aggregation |

**Design**: Webhooks are optional, configurable via `WEBHOOK_URL`, `WEBHOOK_SECRET`. No Anakatech-specific code.

### 2. Events (internal, forwardable)

| Event | Forwarded When | Destination |
|-------|-----------------|-------------|
| Audit events | `ENABLE_SHARED_ANALYTICS=true` | Anakatech audit API |
| Analytics events | `ENABLE_SHARED_ANALYTICS=true` | Anakatech analytics |

**Design**: `authora.integration.analytics` forwards when enabled; core audit log is always local.

### 3. Config API (inbound)

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/config` | Mode, flags, branding — for frontend bootstrap |
| `GET /api/v1/config/mode` | Deployment mode, integration flags |
| `GET /api/v1/config/branding` | White-label overrides |

**Design**: Public, no auth. Consumed by frontend and optionally by ecosystem portal.

### 4. Health API (inbound)

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness |
| `GET /health/ready` | Readiness (DB, Redis) |

**Design**: Standard paths for load balancers and ecosystem health aggregation.

## Implementation Order

1. **Phase 1 (current)**: Standalone core stable, one-command deploy, billing, setup wizard.
2. **Phase 2**: Optional connector layer (`authora/integration/`) with no-op adapters, registry, env toggles.
3. **Phase 3**: Implement adapters (SSO, analytics forwarding) when Anakatech APIs are available.
4. **Phase 4**: Embeddable shell, shared nav, portal integration when needed.
5. **Phase 5**: Unified admin/portal integration (future).

## Related Documentation

- [STANDALONE_VS_CONNECTED_MODE](STANDALONE_VS_CONNECTED_MODE.md) — Mode comparison and switching
- [OPTIONAL_CONNECTOR_LAYER](OPTIONAL_CONNECTOR_LAYER.md) — Adapter architecture and usage
- [ANAKATECH_INTEGRATION](ANAKATECH_INTEGRATION.md) — Integration guide
- [ANAKATECH_CONVENTIONS](ANAKATECH_CONVENTIONS.md) — Ecosystem conventions
