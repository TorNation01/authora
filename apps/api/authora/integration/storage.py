"""Storage / ecosystem interoperability adapter.

Preserves AUTHORA storage behavior in standalone mode. Adds optional
shared storage adapter compatibility where useful.
"""

from typing import BinaryIO

from authora.config import get_settings
from authora.integration.registry import get_integration_registry


def use_shared_storage() -> bool:
    """True when shared Anakatech storage should be used (when configured)."""
    if not get_integration_registry().is_integration_enabled():
        return False
    # Placeholder: ENABLE_SHARED_STORAGE or similar env
    return False


def get_storage_prefix() -> str:
    """Return storage key prefix for namespacing (e.g. authora/ or tenant/authora/)."""
    if not get_integration_registry().is_integration_enabled():
        return "authora/"
    # Placeholder: tenant-aware prefix when multi-tenant
    return "authora/"


class SharedStorageAdapter:
    """Optional adapter for Anakatech shared storage. No-op when disabled."""

    async def put(
        self,
        key: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        """Store in shared storage when enabled. Raises if not configured."""
        if not use_shared_storage():
            raise RuntimeError("Shared storage not enabled")
        # Placeholder: delegate to Anakatech storage API
        raise NotImplementedError("Shared storage not implemented")

    async def get(self, key: str) -> bytes:
        """Retrieve from shared storage when enabled."""
        if not use_shared_storage():
            raise RuntimeError("Shared storage not enabled")
        raise NotImplementedError("Shared storage not implemented")

    async def delete(self, key: str) -> None:
        """Delete from shared storage when enabled."""
        if not use_shared_storage():
            raise RuntimeError("Shared storage not enabled")
        raise NotImplementedError("Shared storage not implemented")
