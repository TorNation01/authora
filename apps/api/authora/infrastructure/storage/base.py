"""Storage provider interface."""

from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageProvider(ABC):
    """Abstract storage provider for files (exports, uploads, assets)."""

    @abstractmethod
    async def put(
        self,
        key: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        """Store content and return URL or path."""
        ...

    @abstractmethod
    async def get(self, key: str) -> bytes:
        """Retrieve content by key."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete object by key."""
        ...

    @abstractmethod
    def url_for(self, key: str) -> str:
        """Get URL or path for key (for download links)."""
        ...
