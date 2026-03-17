"""Storage / ecosystem interoperability adapter.

Preserves AUTHORA storage behavior in standalone mode. Adds optional
shared storage adapter compatibility when DEPLOYMENT_MODE=anakatech.

In standalone mode, use_shared_storage() returns False and SharedStorageAdapter
is never used. The NotImplementedError paths are only reachable when Anakatech
integration is enabled and ENABLE_SHARED_STORAGE is set (future).
"""

from typing import BinaryIO

from authora.config import get_settings
from authora.integration.registry import get_integration_registry


def use_shared_storage() -> bool:
    """True when shared Anakatech storage should be used (when configured)."""
    if not get_integration_registry().is_integration_enabled():
        return False
    return False  # Set ENABLE_SHARED_STORAGE=true when implementing Anakatech storage API


def get_storage_prefix() -> str:
    """Return storage key prefix for namespacing (e.g. authora/ or tenant/authora/)."""
    if not get_integration_registry().is_integration_enabled():
        return "authora/"
    return "authora/"


class SharedStorageAdapter:
    """Adapter for Anakatech shared storage. Only used when use_shared_storage() is True."""

    async def put(
        self,
        key: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        """Store in shared storage when enabled."""
        if not use_shared_storage():
            raise RuntimeError("Shared storage not enabled")
        raise NotImplementedError(
            "Shared storage requires Anakatech integration. "
            "Implement via ENABLE_SHARED_STORAGE and storage API."
        )

    async def get(self, key: str) -> bytes:
        """Retrieve from shared storage when enabled."""
        if not use_shared_storage():
            raise RuntimeError("Shared storage not enabled")
        raise NotImplementedError(
            "Shared storage requires Anakatech integration. "
            "Implement via ENABLE_SHARED_STORAGE and storage API."
        )

    async def delete(self, key: str) -> None:
        """Delete from shared storage when enabled."""
        if not use_shared_storage():
            raise RuntimeError("Shared storage not enabled")
        raise NotImplementedError(
            "Shared storage requires Anakatech integration. "
            "Implement via ENABLE_SHARED_STORAGE and storage API."
        )
