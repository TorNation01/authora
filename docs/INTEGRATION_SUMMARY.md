# AUTHORA Integration Summary

## Integration Architecture Summary

AUTHORA uses an **adapter layer** (`authora/integration/`) to integrate with the Anakatech ecosystem. All integration is optional and environment-driven.

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHORA Core Product                         │
│  (auth, projects, books, export, billing, notifications, etc.)   │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ optional calls
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Integration Adapter Layer                      │
│  identity | navigation | notifications | analytics | billing     │
│  branding | storage                                              │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ when flags enabled
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Anakatech Ecosystem                            │
│  (SSO, portal, notification center, audit, entitlements)         │
└─────────────────────────────────────────────────────────────────┘
```

- **Core product**: No direct Anakatech dependency. Works standalone.
- **Adapters**: No-op when integration flags are off.
- **Registry**: `IntegrationRegistry` centralizes feature-flag checks.

---

## Standalone vs Anakatech-Connected Mode Summary

| Aspect | Standalone | Anakatech Connected |
|--------|------------|---------------------|
| **Auth** | Local email/password | Optional SSO + local fallback |
| **Setup** | Setup wizard | May skip (provisioned) |
| **Navigation** | Full sidebar | Optional embeddable shell |
| **Notifications** | In-app + email | Optional shared center |
| **Analytics** | Internal only | Optional shared forwarding |
| **Billing** | Internal plans | Optional shared entitlements |
| **Branding** | AUTHORA default | Optional overrides |
| **Storage** | Local/S3/R2 | Optional shared adapter |
| **Dependencies** | None | Anakatech services (when enabled) |

---

## Environment Variable Map for All Modes

| Variable | Standalone | Anakatech | White-Label |
|----------|------------|-----------|-------------|
| `APP_MODE` / `DEPLOYMENT_MODE` | `standalone` | `anakatech` | `white_label` |
| `ENABLE_SSO` | false | true (optional) | false |
| `ENABLE_SHARED_NAV` | false | true (optional) | false |
| `ENABLE_SHARED_NOTIFICATIONS` | false | true (optional) | false |
| `ENABLE_SHARED_ANALYTICS` | false | true (optional) | false |
| `ENABLE_SHARED_BILLING` | false | true (optional) | false |
| `ENABLE_BRAND_OVERRIDES` | false | true | true |
| `API_GATEWAY_URL` | - | set | - |
| `BRANDING_*` | optional | optional | set |

---

## Feature Flag List

| Flag | Description | Standalone | Anakatech |
|------|-------------|------------|-----------|
| `standalone_auth` | Local login/register | ✓ | optional |
| `standalone_landing` | Marketing landing | ✓ | ✗ |
| `standalone_setup_wizard` | First-run wizard | ✓ | ✗ |
| `local_admin_creation` | Create admin via setup | ✓ | ✗ |
| `sso_ready` | SSO redirect/token | ✗ | ✓ |
| `embeddable_shell` | No sidebar, content-only | ✗ | ✓ |
| `shared_notifications` | Shared notification center | ✗ | ✓ |
| `shared_workspace_identity` | Workspace from parent | ✗ | ✓ |
| `tenant_aware` | Multi-tenant isolation | ✗ | optional |
| `billing` | Plan/entitlement gating | optional | ✓ |

---

## How AUTHORA Plugs Into Anakatech

1. Set `APP_MODE=anakatech` and enable integration toggles as needed.
2. Deploy AUTHORA behind the Anakatech gateway (`API_GATEWAY_URL`).
3. Embed AUTHORA in the portal (iframe or route). Pass auth token via `postMessage`, URL param, or gateway header.
4. When `ENABLE_SHARED_NAV=true`, AUTHORA renders without sidebar; parent provides navigation.
5. When `ENABLE_SHARED_ANALYTICS=true`, request-level audit events are forwarded automatically.
6. When `ENABLE_SHARED_BILLING=true`, entitlement checks can delegate to Anakatech.
7. Adapters provide hooks; implement the actual Anakatech API calls in your deployment.

---

## How AUTHORA Remains Fully Standalone

1. **Default mode**: `APP_MODE=standalone` is the default. No Anakatech config required.
2. **No hard dependencies**: Integration adapters are no-ops when flags are off.
3. **Core isolation**: Core product modules do not import from `authora.integration`.
4. **Standalone flows**: Auth, setup, admin, dashboard, notifications, storage, and billing all work without Anakatech.
5. **Tests**: Core product tests run in standalone mode. Integration tests are separate.
6. **Deployment**: AUTHORA can be deployed as a single stack (API + web + DB + Redis) with no external services.

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| `ANAKATECH_INTEGRATION.md` | Integration architecture, adapters, usage |
| `STANDALONE_MODE.md` | Standalone guarantees and configuration |
| `APP_MODES.md` | Standalone, Anakatech, white-label modes |
| `BRANDING_OVERRIDES.md` | White-label branding configuration |
| `SSO_READY_NOTES.md` | SSO setup and implementation notes |
| `INTEGRATION.md` | Existing integration guide (feature flags, embedding) |
| `ENV-MAP.md` | Environment variable reference |
