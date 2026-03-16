"""Analytics / audit integration adapter.

Preserves AUTHORA internal analytics and audit logs. Adds optional
shared audit event forwarding and analytics event forwarding.
Events follow ecosystem convention: app, timestamp, source.
"""

from datetime import datetime, timezone
from typing import Any

from authora.integration.registry import get_integration_registry

APP_ID = "authora"


def should_forward_audit_events() -> bool:
    """True when audit events should be forwarded to Anakatech."""
    return get_integration_registry().shared_analytics_enabled()


def should_forward_analytics_events() -> bool:
    """True when analytics events should be forwarded to Anakatech."""
    return get_integration_registry().shared_analytics_enabled()


def _audit_payload(
    action: str,
    resource: str,
    resource_id: str | None = None,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> dict[str, Any]:
    """Build ecosystem-standard audit payload."""
    payload: dict[str, Any] = {
        "app": APP_ID,
        "source": APP_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "resource": resource,
    }
    if resource_id is not None:
        payload["resource_id"] = resource_id
    if user_id is not None:
        payload["user_id"] = user_id
    if details is not None:
        payload["details"] = details
    if ip_address is not None:
        payload["ip_address"] = ip_address
    return payload


async def forward_audit_event(
    action: str,
    resource: str,
    resource_id: str | None = None,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> bool:
    """Forward audit event to Anakatech when enabled. Returns success.
    Payload follows ecosystem convention (app, timestamp, source)."""
    if not should_forward_audit_events():
        return False
    # Placeholder: would POST _audit_payload(...) to Anakatech audit API
    _ = _audit_payload(action, resource, resource_id, user_id, details, ip_address)
    return False


async def forward_analytics_event(
    event_name: str,
    properties: dict[str, Any] | None = None,
    user_id: str | None = None,
) -> bool:
    """Forward analytics event to Anakatech when enabled. Returns success."""
    if not should_forward_analytics_events():
        return False
    # Placeholder: would POST to Anakatech analytics API
    return False
