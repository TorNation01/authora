"""Feature flag service."""

from functools import lru_cache
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import Setting


class FeatureFlagService:
    """Feature flag service - database-backed with env override."""

    def __init__(self, db: AsyncSession | None = None):
        self.db = db

    async def is_enabled(self, key: str, user_id: UUID | None = None, context: dict[str, Any] | None = None) -> bool:
        """Check if feature is enabled. Context for future per-user/tenant rules."""
        # Env override
        env_key = f"FEATURE_{key.upper().replace('-', '_')}"
        import os
        val = os.environ.get(env_key)
        if val is not None:
            return val.lower() in ("1", "true", "yes")

        # Database
        if self.db:
            result = await self.db.execute(
                select(Setting).where(Setting.key == f"feature.{key}")
            )
            row = result.scalar_one_or_none()
            if row and isinstance(row.value, dict):
                return bool(row.value.get("enabled", False))

        return False


def get_feature_flag_service(db: AsyncSession | None = None) -> FeatureFlagService:
    """Get feature flag service."""
    return FeatureFlagService(db=db)
