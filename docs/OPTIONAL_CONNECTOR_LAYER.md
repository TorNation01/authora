# Optional Connector Layer

The optional connector layer (`authora/integration/`) provides adapters for integrating AUTHORA into the Anakatech ecosystem. All adapters are **no-ops** when integration is disabled. The connector is never required for core operation.

## Architecture

```
authora/
  integration/
    __init__.py       # Exports get_integration_registry
    registry.py       # IntegrationRegistry — central flag checks
    identity.py       # SSO / shared identity
    navigation.py     # Embeddable shell, workspace launcher
    notifications.py  # Shared notification center
    analytics.py      # Audit/analytics event forwarding
    billing.py        # Anakatech entitlement checks
    branding.py       # Brand overrides
    storage.py        # Shared storage (future)
```

## Design Principles

1. **No imports in core** — Core modules (`api/routes/*`, `services/*`, `models/*`) never import from `authora.integration` directly for business logic. Integration is invoked only at integration points (e.g. `entitlements.py` checks `integration.billing`).
2. **Registry as gate** — All integration checks go through `get_integration_registry()`. The registry reads `DEPLOYMENT_MODE` and `ENABLE_*` flags.
3. **Adapters are no-ops** — When a flag is false, adapters return safe defaults (e.g. `check_shared_entitlement` returns `(True, None)` when disabled).
4. **Placeholder implementations** — Adapters define the interface; actual Anakatech API calls are placeholders until ecosystem APIs exist.

## Registry

```python
from authora.integration.registry import get_integration_registry

registry = get_integration_registry()

registry.is_integration_enabled()   # True when anakatech or white_label
registry.sso_enabled()               # ENABLE_SSO + FEATURE_SSO_READY
registry.shared_nav_enabled()        # ENABLE_SHARED_NAV + FEATURE_EMBEDDABLE_SHELL
registry.shared_notifications_enabled()
registry.shared_analytics_enabled()
registry.shared_billing_enabled()
registry.brand_overrides_enabled()
registry.standalone_auth_allowed()
```

## Adapters

### Identity (`integration/identity.py`)

- `use_sso_login()` — Show SSO button when enabled
- `should_use_local_auth()` — Allow local login when enabled

**Usage**: Auth routes check these before rendering login form.

### Navigation (`integration/navigation.py`)

- `use_embeddable_shell()` — Render without sidebar
- `get_workspace_launcher_entry()` — Entry for portal launcher

**Usage**: `AppShell`, `EmbeddableModule` check `use_embeddable_shell()`.

### Analytics (`integration/analytics.py`)

- `should_forward_audit_events()` — Forward audit to Anakatech
- `forward_audit_event(...)` — POST audit payload (placeholder)
- `forward_analytics_event(...)` — POST analytics (placeholder)

**Usage**: Audit middleware, usage recording call these when enabled.

### Billing (`integration/billing.py`)

- `use_shared_entitlements()` — Use Anakatech for entitlement checks
- `check_shared_entitlement(user_id, feature)` — Returns `(allowed, error)`
- `get_shared_plan(user_id)` — Get plan from Anakatech (placeholder)

**Usage**: `authora.services.entitlements` checks `use_shared_entitlements()` before applying internal limits.

### Branding (`integration/branding.py`)

- Brand overrides from env (`BRANDING_*`) — applied when `ENABLE_BRAND_OVERRIDES=true`

**Usage**: Config endpoint returns branding; frontend applies.

### Notifications (`integration/notifications.py`)

- Placeholder for forwarding notifications to shared center

### Storage (`integration/storage.py`)

- Placeholder for shared storage compatibility (future)

## Integration Points in Core

Core code touches integration only at these points:

| Core Module | Integration Check | Behavior |
|-------------|-------------------|----------|
| `entitlements.py` | `use_shared_entitlements()` | If true, call `check_shared_entitlement` before internal checks |
| `api/routes/auth` | `use_sso_login()`, `should_use_local_auth()` | Conditional SSO vs local form |
| `AppShell.tsx` | `config.is_anakatech`, `integration_flags.enable_shared_nav` | Embeddable shell |
| `middleware/audit` | `should_forward_audit_events()` | Forward to Anakatech |
| `api/routes/config` | `get_integration_flags()` | Expose flags to frontend |

**Rule**: Core never imports Anakatech-specific types or URLs. Integration adapters encapsulate all external calls.

## Adding a New Adapter

1. Create `authora/integration/<adapter>.py`.
2. Implement functions that check the registry and return safe defaults when disabled.
3. Add a method to `IntegrationRegistry` if a new `ENABLE_*` flag is needed.
4. Add the flag to `config.py`.
5. Document in `ANAKATECH_INTEGRATION.md`.

Example:

```python
# authora/integration/my_adapter.py
from authora.config import get_settings
from authora.integration.registry import get_integration_registry

def my_feature_enabled() -> bool:
    return get_integration_registry().is_integration_enabled() and get_settings().enable_my_feature

async def call_external_api(...) -> bool:
    if not my_feature_enabled():
        return False
    # Placeholder: actual API call
    return False
```

## Dependency Rule

**No Anakatech SDK or library in core dependencies.** If an adapter needs an HTTP client, use `httpx` or `requests` (already available). Never add `anakatech-sdk` or similar as a required dependency. Optional dependencies can be added later with `extras` in pyproject.toml if needed.

## Related Documentation

- [ANAKATECH_INTEGRATION_STRATEGY](ANAKATECH_INTEGRATION_STRATEGY.md) — Overall strategy
- [STANDALONE_VS_CONNECTED_MODE](STANDALONE_VS_CONNECTED_MODE.md) — Mode comparison
- [ANAKATECH_INTEGRATION](ANAKATECH_INTEGRATION.md) — Integration guide
