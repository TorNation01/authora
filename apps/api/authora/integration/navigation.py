"""Navigation / launcher integration adapter.

Preserves standalone navigation. Adds optional shared Anakatech nav shell
compatibility and workspace launcher entry support.
"""

from authora.config import get_settings
from authora.integration.registry import get_integration_registry


def use_embeddable_shell() -> bool:
    """True when AUTHORA should render inside Anakatech shared nav shell."""
    return get_integration_registry().shared_nav_enabled()


def get_workspace_launcher_entry() -> dict | None:
    """Return workspace launcher entry config when integrated; None when standalone."""
    if not use_embeddable_shell():
        return None
    # Placeholder: would return { "label": "AUTHORA", "href": "/authora", "icon": "..." }
    return {
        "label": "AUTHORA",
        "href": "/authora",
        "icon": None,
    }


def get_portal_base_url() -> str | None:
    """Return Anakatech portal base URL when integrated; None when standalone."""
    if not use_embeddable_shell():
        return None
    return get_settings().api_gateway_url  # Upstream gateway; portal URL may differ
