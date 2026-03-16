# Standalone vs Connected Mode

AUTHORA supports two deployment modes: **standalone** (default) and **connected** (Anakatech). This document defines what each mode means and how to switch.

## Mode Overview

| Aspect | Standalone | Connected (Anakatech) |
|--------|------------|----------------------|
| **Default** | Yes | No |
| **Deployment** | Independent, self-hosted | Can be embedded in Anakatech portal |
| **Auth** | Local email/password | SSO (when enabled) or local |
| **Billing** | Internal plans + Stripe | Internal or Anakatech entitlements |
| **Setup** | Setup wizard, first admin | Centralized provisioning |
| **Landing** | Full marketing page | Minimal or none (parent provides) |
| **Navigation** | Full sidebar | Embeddable shell (parent provides nav) |
| **Analytics** | Local audit log | Optional forward to Anakatech |
| **Dependencies** | None on Anakatech | Optional adapters when enabled |

## What Remains Standalone (Always)

Regardless of mode, these are **always** standalone:

- **Core product** — Projects, books, chapters, AI, export, accountability, gamification
- **Database** — PostgreSQL, migrations, schema
- **API** — REST endpoints, OpenAPI
- **Storage** — Local, S3, R2
- **Deployment** — Docker Compose, scripts
- **Health** — `/health`, `/health/ready`

AUTHORA never requires an Anakatech service to start, run, or serve users.

## What Changes in Connected Mode

When `DEPLOYMENT_MODE=anakatech` (or `white_label`):

| Feature | Standalone | Connected |
|---------|------------|-----------|
| Setup wizard | Enabled | Disabled (centralized provisioning) |
| Local auth | Primary | Optional (SSO primary when `ENABLE_SSO=true`) |
| Landing page | Full | Minimal or hidden |
| Sidebar | Full | Embeddable shell (no sidebar when `ENABLE_SHARED_NAV=true`) |
| Billing | Internal + Stripe | Internal + Stripe, or Anakatech when `ENABLE_SHARED_BILLING=true` |
| Audit/analytics | Local only | Optional forward when `ENABLE_SHARED_ANALYTICS=true` |
| Branding | Default | Overridable via `BRANDING_*` |

## Environment Configuration

### Standalone (Default)

```env
DEPLOYMENT_MODE=standalone
# or omit; standalone is default

FEATURE_STANDALONE_AUTH=true
FEATURE_STANDALONE_LANDING=true
FEATURE_STANDALONE_SETUP_WIZARD=true
FEATURE_EMBEDDABLE_SHELL=false
FEATURE_SSO_READY=false
```

### Connected (Anakatech)

```env
DEPLOYMENT_MODE=anakatech

FEATURE_STANDALONE_AUTH=false
FEATURE_STANDALONE_LANDING=false
FEATURE_STANDALONE_SETUP_WIZARD=false
FEATURE_EMBEDDABLE_SHELL=true
FEATURE_SSO_READY=true

# Optional integration toggles
ENABLE_SSO=true
ENABLE_SHARED_NAV=true
ENABLE_SHARED_NOTIFICATIONS=true
ENABLE_SHARED_ANALYTICS=true
ENABLE_SHARED_BILLING=false
ENABLE_BRAND_OVERRIDES=true

# When using gateway
API_GATEWAY_URL=https://gateway.anakatech.example.com
```

### White-Label (Connected with Custom Branding)

```env
DEPLOYMENT_MODE=white_label

BRANDING_PRODUCT_NAME=My Writing App
BRANDING_TAGLINE=Write Your Book
BRANDING_LOGO_URL=https://...
# ... other BRANDING_* vars
```

## Switching Modes

1. **Standalone → Connected**: Set `DEPLOYMENT_MODE=anakatech`, configure `ENABLE_*` toggles, disable standalone features, enable SSO/embeddable as needed.
2. **Connected → Standalone**: Set `DEPLOYMENT_MODE=standalone`, re-enable `FEATURE_STANDALONE_*`. No data migration required; core data is unchanged.

**Important**: Mode is a runtime configuration. The same deployment can be switched by changing env vars and restarting. No code changes.

## What Should Never Be Tightly Coupled

- **Core domain** — Projects, books, AI, export logic
- **Database** — Schema, migrations
- **API contracts** — Request/response shapes
- **Deployment** — Docker, scripts, health checks

These remain identical in both modes. Integration touches only:

- `authora/integration/*` — Adapters
- `authora/config.py` — Mode and flags
- Frontend — Conditional rendering (embeddable shell, SSO button)
- Middleware — Optional audit forwarding

## Recommendation

**Keep AUTHORA standalone-first.** Add Anakatech integration as an optional connector layer after the product is stable. Standalone deployment and testing must always pass without any Anakatech configuration.
