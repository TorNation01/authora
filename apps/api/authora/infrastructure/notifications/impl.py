"""Notification service implementation."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.infrastructure.notifications.base import NotificationService
from authora.models import Notification


class DefaultNotificationService(NotificationService):
    """Default implementation: in-app only; email no-op unless configured."""

    def __init__(self, db: AsyncSession | None = None):
        self._db = db

    async def send_in_app(self, user_id: str, type: str, title: str, body: str) -> bool:
        if not self._db:
            return False
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            body=body,
        )
        self._db.add(notification)
        await self._db.flush()
        return True

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        # No-op unless SMTP/SendGrid configured
        return False
