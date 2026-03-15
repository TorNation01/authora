"""Branding integration adapter.

Preserves Authora branding in standalone mode. Adds environment-driven
overrides for logos, app name, accent colors, product text, and portal labels.
"""

from authora.config import get_settings
from authora.integration.registry import get_integration_registry


def get_effective_branding() -> dict:
    """Return branding config. Uses overrides when brand_overrides_enabled."""
    settings = get_settings()
    branding = settings.get_branding()
    if get_integration_registry().brand_overrides_enabled():
        # Overrides already applied via env (branding_* vars)
        return branding
    return branding


def product_name() -> str:
    """Return effective product name."""
    return get_effective_branding().get("product_name", "AUTHORA") or "AUTHORA"


def primary_color() -> str | None:
    """Return effective primary/accent color."""
    return get_effective_branding().get("primary_color")
