# Anakatech Connector Audit Report

**Date**: 2025-03-15  
**Scope**: AUTHORA codebase – Anakatech integration layer vs required connector functionality

---

## 1. Connector Capability Already Exists

| Connector | Status | Location |
|-----------|--------|----------|
| **Shared identity / SSO readiness** | ✓ Implemented | `config.py` (sso_issuer_url, sso_client_id, sso_metadata_url, feature_sso_ready); `integration/identity.py` (use_sso_login, should_use_local_auth, resolve_shared_identity); auth routes check `feature_standalone_auth` |
| **Shared nav shell compatibility** | ✓ Implemented | `config.py` (feature_embeddable_shell); `integration/navigation.py` (use_embeddable_shell); `AppShell.tsx`, `EmbeddableModule.tsx` |
| **Shared workspace launcher compatibility** | ✓ Implemented | `integration/navigation.py` (get_workspace_launcher_entry, get_portal_base_url) |
| **Shared notification compatibility** | ✓ Implemented + wired | `integration/notifications.py` (should_forward_to_shared_center, forward_to_shared_center); wired in `DefaultNotificationService.send_reminder` |
| **Shared analytics / audit forwarding hooks** | ✓ Implemented | `integration/analytics.py` (forward_audit_event, should_forward_audit_events); `IntegrationAuditForwardingMiddleware` for request-level forwarding |
| **Shared billing / entitlement compatibility** | ✓ Implemented + wired | `integration/billing.py` (use_shared_entitlements, check_shared_entitlement); wired in `entitlements.py` |
| **Environment-driven app modes** | ✓ Implemented | `config.py` (APP_MODE, DEPLOYMENT_MODE, standalone/anakatech/white_label, effective_app_mode) |
| **Branding override support** | ✓ Implemented | `config.py` (branding_* vars, get_branding); `integration/branding.py`; `BrandedSidebar`, login/register pages |
| **Standalone-safe operation** | ✓ Implemented | Default standalone; all adapters no-op when flags off; integration isolated in `authora/integration/` |

---

## 2. What Was Missing (Before This Audit)

| Gap | Description |
|-----|-------------|
| **Notification forwarding wire** | `forward_to_shared_center` existed but was never called. Reminder service sent only to in-app/email. |
| **Entitlement integration wire** | `check_shared_entitlement` existed but entitlements service used only internal billing. No optional Anakatech entitlement check. |
| **Frontend nav consistency** | AppShell/EmbeddableModule used `embeddable_shell` + `is_anakatech` but did not respect `integration_flags.enable_shared_nav`. |

---

## 3. What Was Added (This Audit)

| Change | File | Description |
|--------|------|--------------|
| Notification forward wire | `infrastructure/notifications/impl.py` | After `send_reminder` in-app/email, call `forward_to_shared_center` when `should_forward_to_shared_center()`. Wrapped in try/except so integration failure does not break reminder delivery. |
| Entitlement shared check | `services/entitlements.py` | Added `_check_shared_entitlement_if_enabled(user_id, feature)`. Each entitlement function (projects, books, ai, export, ghostwriter, storage) calls it first when `use_shared_entitlements()`; on failure returns immediately. |
| Frontend nav consistency | `AppShell.tsx`, `EmbeddableModule.tsx` | Use embeddable shell only when `embeddable_shell` AND `(is_anakatech \|\| is_white_label)` AND `integration_flags?.enable_shared_nav !== false`. Backward compatible when `integration_flags` is absent. |

---

## 4. Confirmation: No Duplicate Connector Systems

- **Single integration layer**: All Anakatech connectors live in `authora/integration/` (registry, identity, navigation, notifications, analytics, billing, branding, storage).
- **Single config source**: `config.py` holds all feature flags and integration toggles; no duplicate flag definitions.
- **Single middleware**: `IntegrationAuditForwardingMiddleware` is the only audit-forwarding middleware.
- **No parallel systems**: No second SSO path, no alternate notification pipeline, no duplicate entitlement logic. The entitlements service and notification service call the integration adapters; they do not implement their own Anakatech logic.

---

## Summary

The Anakatech integration layer already covered all required connector functionality at the adapter level. This audit added only the missing **wires** (notification forwarding, entitlement shared check) and **frontend consistency** (respect `enable_shared_nav`). No duplicate connector systems were created.
