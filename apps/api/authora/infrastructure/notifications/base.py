"""Notification service interface."""

from abc import ABC, abstractmethod
from typing import Any


class NotificationChannel(ABC):
    """Abstract notification channel (email, push, in-app)."""

    @abstractmethod
    async def send(
        self,
        to: str,
        subject: str | None,
        body: str,
        template: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> bool:
        """Send notification. Returns success."""
        ...


class NotificationService(ABC):
    """Abstract notification service."""

    @abstractmethod
    async def send_in_app(self, user_id: str, type: str, title: str, body: str) -> bool:
        """Send in-app notification."""
        ...

    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send email."""
        ...
