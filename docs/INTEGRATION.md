# AUTHORA Integration Guide

AUTHORA runs in two deployment modes:

- **Standalone** – Full self-contained product with local auth, landing page, and setup wizard
- **Anakatech** – Integrated into the Anakatech platform with SSO, embeddable shell, and shared services

## Environment Configuration

### Standalone Mode (default)

```env
DEPLOYMENT_MODE=standalone
FEATURE_STANDALONE_AUTH=true
FEATURE_STANDALONE_LANDING=true
FEATURE_STANDALONE_SETUP_WIZARD=true
FEATURE_LOCAL_ADMIN_CREATION=true
FEATURE_EMBEDDABLE_SHELL=false
FEATURE_SSO_READY=false
```

### Anakatech Mode

```env
DEPLOYMENT_MODE=anakatech
FEATURE_STANDALONE_AUTH=false
FEATURE_STANDALONE_LANDING=false
FEATURE_STANDALONE_SETUP_WIZARD=false
FEATURE_LOCAL_ADMIN_CREATION=false
FEATURE_SSO_READY=true
FEATURE_EMBEDDABLE_SHELL=true
FEATURE_SHARED_NOTIFICATIONS=true
FEATURE_SHARED_WORKSPACE_IDENTITY=true
FEATURE_TENANT_AWARE=false
FEATURE_BILLING=true

# SSO (when implementing)
SSO_ISSUER_URL=
SSO_CLIENT_ID=
SSO_METADATA_URL=

# API gateway (optional)
API_GATEWAY_URL=
```

### Frontend

```env
NEXT_PUBLIC_DEPLOYMENT_MODE=standalone
NEXT_PUBLIC_API_URL=
```

Config is fetched from `/api/v1/config` at runtime; `NEXT_PUBLIC_DEPLOYMENT_MODE` is a fallback for SSR.

---

## Feature Flags

| Flag | Standalone | Anakatech | Description |
|------|------------|-----------|-------------|
| `standalone_auth` | ✓ | ✗ | Local login/register |
| `standalone_landing` | ✓ | ✗ | Full marketing landing page |
| `standalone_setup_wizard` | ✓ | ✗ | First-run setup wizard |
| `local_admin_creation` | ✓ | ✗ | Create admin via setup |
| `sso_ready` | ✗ | ✓ | SSO redirect / token exchange |
| `embeddable_shell` | ✗ | ✓ | No sidebar; content-only for iframe |
| `shared_notifications` | ✗ | ✓ | Use parent notification system |
| `shared_workspace_identity` | ✗ | ✓ | Workspace from parent context |
| `tenant_aware` | ✗ | ✓ | Multi-tenant data isolation |
| `billing` | ✗ | ✓ | Billing/entitlements integration |

---

## White-Label Branding

Override via environment:

```env
BRANDING_PRODUCT_NAME=My Writing App
BRANDING_TAGLINE=Write Your Book
BRANDING_LOGO_URL=https://authora.studio/logo.png
BRANDING_FAVICON_URL=https://authora.studio/favicon.ico
BRANDING_PRIMARY_COLOR=#6366f1
BRANDING_SHOW_POWERED_BY=false
```

Branding is exposed at `GET /api/v1/config/branding` and used in the sidebar, landing page, and metadata.

---

## Modular Auth

### Standalone

- `/login`, `/register` – Local email/password
- Tokens stored in `localStorage` (`access_token`, `refresh_token`)
- `GET /api/v1/auth/me` validates session

### Anakatech (SSO-ready)

- `/sso` – Entry point; redirects to IdP or exchanges token from parent
- Token may be passed via `postMessage`, URL param, or gateway header
- Implement `apps/web/src/app/(auth)/sso/page.tsx` to wire your IdP

---

## Modular Navigation

### Standalone

- Full sidebar with nav items (Dashboard, Notes, Journey, etc.)
- `BrandedSidebar` uses `branding.product_name` and optional logo

### Anakatech (embeddable)

- `embeddable_shell=true` → No sidebar; content renders in a minimal wrapper
- Parent app provides navigation; AUTHORA is an embedded module

---

## Embeddable Module Architecture

To embed AUTHORA in an iframe or parent app:

1. Set `FEATURE_EMBEDDABLE_SHELL=true` and `DEPLOYMENT_MODE=anakatech`
2. Load AUTHORA at a route like `/authora` or in an iframe
3. Pass auth token via:
   - `postMessage` from parent
   - URL param (less secure)
   - Gateway header (server-side)

Example iframe integration:

```html
<iframe
  src="https://app.authora.studio/dashboard?token=..."
  data-authora-embed="true"
  title="AUTHORA"
></iframe>
```

The `EmbeddableModule` component wraps content with `data-authora-embed="true"` for parent detection.

---

## API Gateway Compatibility

- **Standalone**: Requests go to `NEXT_PUBLIC_API_URL` (or same-origin via Next.js rewrites)
- **Anakatech**: Set `API_GATEWAY_URL` to route through your gateway; frontend uses `NEXT_PUBLIC_API_URL` pointing at the gateway

---

## Billing Abstraction

When `FEATURE_BILLING=true`:

- `getBillingStatus()` in `@/lib/billing` is the integration point
- Implement a call to your billing/entitlements API
- Use for feature gating (e.g. AI limits, export limits)

---

## Config API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/config` | Full config (mode, flags, branding) |
| `GET /api/v1/config/mode` | Deployment mode and feature flags |
| `GET /api/v1/config/branding` | White-label branding only |

All are public (no auth required) for frontend bootstrap.
