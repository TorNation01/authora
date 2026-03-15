"""Identity / access integration adapter.

Preserves standalone auth. Adds optional Anakatech SSO readiness and
shared identity compatibility. Local auth is used when SSO is disabled.
"""

from typing import Any
from uuid import UUID

from authora.integration.registry import get_integration_registry


def use_sso_login() -> bool:
    """True when SSO login should be offered (Anakatech SSO ready)."""
    return get_integration_registry().sso_enabled()


def get_sso_login_url(redirect_uri: str | None = None) -> str | None:
    """Return SSO login URL when SSO is enabled; otherwise None."""
    if not use_sso_login():
        return None
    # Placeholder: actual SSO URL would come from Anakatech identity service
    # e.g. ANAKATECH_SSO_URL or api_gateway_url + /auth/sso
    return None


def resolve_shared_identity(user_id: UUID) -> dict[str, Any] | None:
    """Resolve user to shared identity when integration enabled. Returns None when standalone."""
    if not get_integration_registry().sso_enabled():
        return None
    # Placeholder: would call Anakatech identity service to get shared user context
    return None


def should_use_local_auth() -> bool:
    """True when local (standalone) auth should be used."""
    reg = get_integration_registry()
    if reg.is_integration_enabled() and reg.sso_enabled():
        return reg.standalone_auth_allowed()  # Allow local as fallback
    return True  # Standalone: always local auth
