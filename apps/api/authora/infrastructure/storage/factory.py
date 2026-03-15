"""Storage provider factory."""

from functools import lru_cache

from authora.config import get_settings
from authora.infrastructure.storage.base import StorageProvider
from authora.infrastructure.storage.local import LocalStorageProvider
from authora.infrastructure.storage.s3 import S3StorageProvider


@lru_cache
def get_storage_provider() -> StorageProvider:
    """Get configured storage provider."""
    settings = get_settings()
    provider = getattr(settings, "storage_provider", "local") or "local"

    if provider == "local":
        path = getattr(settings, "storage_local_path", "./storage") or "./storage"
        return LocalStorageProvider(base_path=path)
    if provider in ("s3", "r2"):
        bucket = getattr(settings, "s3_bucket", None) or getattr(settings, "r2_bucket", None)
        if not bucket:
            return LocalStorageProvider(base_path="./storage")
        region = getattr(settings, "aws_region", "us-east-1") or "us-east-1"
        endpoint = None
        if provider == "r2":
            account = getattr(settings, "r2_account_id", None) or ""
            endpoint = f"https://{account}.r2.cloudflarestorage.com" if account else None
        return S3StorageProvider(
            bucket=bucket,
            region=region,
            endpoint_url=endpoint,
        )
    return LocalStorageProvider(base_path="./storage")
