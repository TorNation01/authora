"""Notification service factory."""

from authora.infrastructure.notifications.base import NotificationService
from authora.infrastructure.notifications.impl import DefaultNotificationService


def get_notification_service(db=None) -> NotificationService:
    """Get notification service. Requires db for in-app."""
    return DefaultNotificationService(db=db)
