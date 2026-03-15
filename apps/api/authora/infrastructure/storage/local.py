"""Local filesystem storage provider."""

import os
from pathlib import Path
from typing import BinaryIO

from authora.infrastructure.storage.base import StorageProvider


class LocalStorageProvider(StorageProvider):
    """Store files on local filesystem."""

    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.base_path / key.lstrip("/")

    async def put(
        self,
        key: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = content.read() if hasattr(content, "read") else content
        path.write_bytes(data)
        return str(path)

    async def get(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise FileNotFoundError(f"Key not found: {key}")
        return path.read_bytes()

    async def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()

    def url_for(self, key: str) -> str:
        return f"/storage/{key}"
