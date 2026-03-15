"""S3-compatible storage provider (AWS S3, Cloudflare R2)."""

import os
from typing import BinaryIO

from authora.infrastructure.storage.base import StorageProvider


class S3StorageProvider(StorageProvider):
    """Store files in S3 or R2."""

    def __init__(
        self,
        bucket: str,
        region: str = "us-east-1",
        endpoint_url: str | None = None,
        public_base_url: str | None = None,
    ):
        self.bucket = bucket
        self.region = region
        self.endpoint_url = endpoint_url
        self.public_base_url = public_base_url

    def _client(self):
        try:
            import boto3
        except ImportError:
            raise ImportError("boto3 required for S3 storage. pip install boto3")
        kwargs = {
            "region_name": self.region,
            "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
        }
        if self.endpoint_url:
            kwargs["endpoint_url"] = self.endpoint_url
        return boto3.client("s3", **kwargs)

    async def put(
        self,
        key: str,
        content: bytes | BinaryIO,
        content_type: str | None = None,
    ) -> str:
        import asyncio

        client = self._client()
        data = content.read() if hasattr(content, "read") else content
        extra = {"ContentType": content_type} if content_type else {}
        await asyncio.to_thread(
            client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=data,
            **extra,
        )
        return self.url_for(key)

    async def get(self, key: str) -> bytes:
        import asyncio

        client = self._client()
        resp = await asyncio.to_thread(client.get_object, Bucket=self.bucket, Key=key)
        return resp["Body"].read()

    async def delete(self, key: str) -> None:
        import asyncio

        client = self._client()
        await asyncio.to_thread(client.delete_object, Bucket=self.bucket, Key=key)

    def url_for(self, key: str) -> str:
        if self.public_base_url:
            return f"{self.public_base_url.rstrip('/')}/{key}"
        client = self._client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=3600,
        )
