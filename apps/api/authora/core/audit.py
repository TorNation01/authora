"""Audit logging layer."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import AuditLog


class AuditLogger:
    """Audit log writer."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        resource: str,
        resource_id: str | None = None,
        user_id: UUID | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> None:
        """Write audit log entry."""
        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(entry)
        await self.db.flush()
