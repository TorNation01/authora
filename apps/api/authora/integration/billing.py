"""Billing / entitlement integration adapter.

Preserves AUTHORA's internal plan/entitlement model. Adds optional
compatibility hooks for Anakatech-wide entitlement checking.
Plan gating remains functional when external billing integration is absent.
"""

from uuid import UUID

from authora.integration.registry import get_integration_registry


def use_shared_entitlements() -> bool:
    """True when Anakatech-wide entitlement checks should be used."""
    return get_integration_registry().shared_billing_enabled()


async def check_shared_entitlement(
    user_id: UUID,
    feature: str,
) -> tuple[bool, str | None]:
    """Check entitlement via Anakatech when enabled. Returns (allowed, error_message)."""
    if not use_shared_entitlements():
        return True, None  # No external check; internal entitlements apply
    # Placeholder: would call Anakatech entitlement API
    return True, None


async def get_shared_plan(user_id: UUID) -> str | None:
    """Get plan from Anakatech when enabled; None when using internal plans."""
    if not use_shared_entitlements():
        return None
    # Placeholder: would call Anakatech billing/plan API
    return None
