"""Optional Anakatech integration layer.

This package provides adapters for integrating AUTHORA into the broader
Anakatech ecosystem. All integration is optional and environment-driven.
Standalone operation is fully preserved when integration flags are disabled.
"""

from authora.integration.registry import get_integration_registry

__all__ = ["get_integration_registry"]
