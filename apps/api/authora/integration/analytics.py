"""Analytics / audit integration adapter.

Preserves AUTHORA internal analytics and audit logs. Adds optional
shared audit event forwarding and analytics event forwarding.
"""

from typing import Any

from authora.integration.registry import get_integration_registry


def should_forward_audit_events() -> bool:
    """True when audit events should be forwarded to Anakatech."""
    return get_integration_registry().shared_analytics_enabled()


def should_forward_analytics_events() -> bool:
    """True when analytics events should be forwarded to Anakatech."""
    return get_integration_registry().shared_analytics_enabled()


async def forward_audit_event(
    action: str,
    resource: str,
    resource_id: str | None = None,
    user_id: str | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None,
) -> bool:
    """Forward audit event to Anakatech when enabled. Returns success."""
    if not should_forward_audit_events():
        return False
    # Placeholder: would POST to Anakatech audit API
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
