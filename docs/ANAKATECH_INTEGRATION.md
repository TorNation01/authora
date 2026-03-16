# Anakatech Integration Guide

AUTHORA integrates into the Anakatech ecosystem through an optional adapter layer. For ecosystem conventions, see [ANAKATECH_CONVENTIONS.md](./ANAKATECH_CONVENTIONS.md). Integration is modular, environment-driven, and does not affect standalone operation.

## Strategy Documents

- **[ANAKATECH_INTEGRATION_STRATEGY](ANAKATECH_INTEGRATION_STRATEGY.md)** — Overall strategy, what stays standalone, what can integrate
- **[STANDALONE_VS_CONNECTED_MODE](STANDALONE_VS_CONNECTED_MODE.md)** — Mode comparison and switching
- **[OPTIONAL_CONNECTOR_LAYER](OPTIONAL_CONNECTOR_LAYER.md)** — Adapter architecture and usage

## Architecture Overview

The integration layer lives in `authora/integration/` and provides:

- **Identity adapter** – SSO readiness, shared identity compatibility
- **Navigation adapter** – Shared nav shell, workspace launcher
- **Notifications adapter** – Shared notification center hooks
- **Analytics adapter** – Audit and analytics event forwarding
- **Billing adapter** – Anakatech-wide entitlement checks
- **Branding adapter** – Environment-driven brand overrides
- **Storage adapter** – Optional shared storage compatibility

All adapters are **no-ops** when integration flags are disabled. Core product logic is isolated from integration logic.

## How AUTHORA Plugs Into Anakatech

1. **Deployment mode**: Set `APP_MODE=anakatech` or `DEPLOYMENT_MODE=anakatech`.

2. **Integration toggles**: Enable only the integrations you need:
   - `ENABLE_SSO=true` – SSO login, shared identity
   - `ENABLE_SHARED_NAV=true` – Embeddable shell, workspace launcher
   - `ENABLE_SHARED_NOTIFICATIONS=true` – Forward to shared notification center
   - `ENABLE_SHARED_ANALYTICS=true` – Forward audit/analytics events
   - `ENABLE_SHARED_BILLING=true` – Use Anakatech entitlement checks
   - `ENABLE_BRAND_OVERRIDES=true` – Apply branding overrides

3. **Feature flags**: Set Anakatech-specific feature flags (see `docs/INTEGRATION.md`).

4. **Gateway**: Set `API_GATEWAY_URL` to route through the Anakatech gateway.

5. **Embedding**: Load AUTHORA in an iframe or as a route in the Anakatech portal. Pass auth token via `postMessage`, URL param, or gateway header.

## Integration Points

| Area | Adapter | When Enabled |
|------|---------|---------------|
| Identity | `authora.integration.identity` | `ENABLE_SSO=true` + `FEATURE_SSO_READY=true` |
| Navigation | `authora.integration.navigation` | `ENABLE_SHARED_NAV=true` + `FEATURE_EMBEDDABLE_SHELL=true` |
| Notifications | `authora.integration.notifications` | `ENABLE_SHARED_NOTIFICATIONS=true` |
| Analytics | `authora.integration.analytics` | `ENABLE_SHARED_ANALYTICS=true` |
| Billing | `authora.integration.billing` | `ENABLE_SHARED_BILLING=true` + `FEATURE_BILLING=true` |
| Branding | `authora.integration.branding` | `ENABLE_BRAND_OVERRIDES=true` |
| Storage | `authora.integration.storage` | `ENABLE_SHARED_STORAGE=true` (future) |

## Adapter Usage

### Identity

```python
from authora.integration.identity import use_sso_login, should_use_local_auth

if use_sso_login():
    # Show SSO button, redirect to IdP
    ...
if should_use_local_auth():
    # Show email/password form
    ...
```

### Navigation

```python
from authora.integration.navigation import use_embeddable_shell, get_workspace_launcher_entry

if use_embeddable_shell():
    # Render without sidebar; parent provides nav
    ...
entry = get_workspace_launcher_entry()  # For portal launcher
```

### Analytics

```python
from authora.integration.analytics import forward_audit_event, should_forward_audit_events

if should_forward_audit_events():
    await forward_audit_event(action="create", resource="project", user_id=...)
```

Request-level audit forwarding is automatic via `IntegrationAuditForwardingMiddleware` when `ENABLE_SHARED_ANALYTICS=true`.

### Billing

```python
from authora.integration.billing import use_shared_entitlements, check_shared_entitlement

if use_shared_entitlements():
    allowed, err = await check_shared_entitlement(user_id, "ai")
    if not allowed:
        return forbidden(err)
```

## Safety Rules

- Do not merge Anakatech logic into core product modules.
- Do not remove or weaken standalone functionality.
- All integration points are optional and configurable.
- Core product tests must pass in standalone mode.
- Integration mode must not duplicate core systems.
