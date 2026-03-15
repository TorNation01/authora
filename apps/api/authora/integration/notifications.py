"""Notifications integration adapter.

Preserves AUTHORA's own reminder/notification system. Adds optional
compatibility hooks for shared Anakatech notification center.
Avoids duplicating notifications when integrated.
"""

from typing import Any

from authora.integration.registry import get_integration_registry


def should_forward_to_shared_center() -> bool:
    """True when notifications should also be sent to Anakatech shared center."""
    return get_integration_registry().shared_notifications_enabled()


async def forward_to_shared_center(
    user_id: str,
    notification_type: str,
    title: str,
    body: str,
    metadata: dict[str, Any] | None = None,
) -> bool:
    """Forward notification to shared Anakatech center when enabled. Returns success."""
    if not should_forward_to_shared_center():
        return False
    # Placeholder: would POST to Anakatech notification API
    # to avoid duplicate in-app notifications, AUTHORA may skip local in_app
    # when this returns True (configurable)
    return False  # No-op until integration implemented


def skip_local_in_app_when_forwarded() -> bool:
    """True when we should skip local in-app notification if forwarding to shared center."""
    return should_forward_to_shared_center()
    # Could be a separate flag: ENABLE_SHARED_NOTIFICATIONS_EXCLUSIVE
