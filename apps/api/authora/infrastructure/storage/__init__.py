"""Storage abstraction - local, S3, R2."""

from authora.infrastructure.storage.base import StorageProvider
from authora.infrastructure.storage.factory import get_storage_provider

__all__ = ["StorageProvider", "get_storage_provider"]
