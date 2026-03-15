"""Notification service abstraction."""

from authora.infrastructure.notifications.base import NotificationChannel, NotificationService
from authora.infrastructure.notifications.factory import get_notification_service

__all__ = ["NotificationChannel", "NotificationService", "get_notification_service"]
