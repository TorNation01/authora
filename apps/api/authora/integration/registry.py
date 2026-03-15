"""Integration registry - central access to optional Anakatech adapters."""

from authora.config import get_settings


def get_integration_registry() -> "IntegrationRegistry":
    """Return the integration registry (singleton)."""
    return IntegrationRegistry()


class IntegrationRegistry:
    """Central registry for optional Anakatech integration adapters.

    All adapters are no-ops when integration flags are disabled.
    """

    def __init__(self):
        self._settings = get_settings()

    def is_integration_enabled(self) -> bool:
        """True when app is in anakatech or white_label mode."""
        return self._settings.is_anakatech() or self._settings.is_white_label()

    def sso_enabled(self) -> bool:
        """True when SSO integration is enabled."""
        return (
            self.is_integration_enabled()
            and self._settings.enable_sso
            and self._settings.feature_sso_ready
        )

    def shared_nav_enabled(self) -> bool:
        """True when shared navigation shell integration is enabled."""
        return (
            self.is_integration_enabled()
            and self._settings.enable_shared_nav
            and self._settings.feature_embeddable_shell
        )

    def shared_notifications_enabled(self) -> bool:
        """True when shared notification center integration is enabled."""
        return (
            self.is_integration_enabled()
            and self._settings.enable_shared_notifications
            and self._settings.feature_shared_notifications
        )

    def shared_analytics_enabled(self) -> bool:
        """True when shared analytics/audit forwarding is enabled."""
        return self.is_integration_enabled() and self._settings.enable_shared_analytics

    def shared_billing_enabled(self) -> bool:
        """True when Anakatech-wide entitlement checking is enabled."""
        return (
            self.is_integration_enabled()
            and self._settings.enable_shared_billing
            and self._settings.feature_billing
        )

    def brand_overrides_enabled(self) -> bool:
        """True when branding overrides are enabled."""
        return (
            self.is_integration_enabled()
            and self._settings.enable_brand_overrides
        )

    def standalone_auth_allowed(self) -> bool:
        """True when local/standalone auth is allowed (even when SSO is available)."""
        return self._settings.feature_standalone_auth
