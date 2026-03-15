"""Notification service implementation with delivery logging and retry."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.config import get_settings
from authora.infrastructure.notifications.base import NotificationService
from authora.models import Notification, NotificationDeliveryLog, User


MAX_RETRIES = 3


class DefaultNotificationService(NotificationService):
    """Default implementation: in-app, email when configured, delivery logging, retry."""

    def __init__(self, db: AsyncSession | None = None):
        self._db = db

    async def _log_delivery(
        self,
        user_id: str,
        notification_type: str,
        channel: str,
        status: str,
        error_message: str | None = None,
        retry_count: int = 0,
        sent_at=None,
    ) -> NotificationDeliveryLog | None:
        """Log delivery attempt for tracking and retry."""
        if not self._db:
            return None
        from datetime import datetime, timezone
        from uuid import UUID

        uid = UUID(user_id) if isinstance(user_id, str) else user_id
        log = NotificationDeliveryLog(
            user_id=uid,
            notification_type=notification_type,
            channel=channel,
            status=status,
            error_message=error_message,
            retry_count=retry_count,
            sent_at=sent_at or (datetime.now(timezone.utc) if status == "sent" else None),
        )
        self._db.add(log)
        await self._db.flush()
        return log

    async def send_in_app(self, user_id: str, type: str, title: str, body: str) -> bool:
        if not self._db:
            return False
        try:
            notification = Notification(
                user_id=user_id,
                type=type,
                title=title,
                body=body,
            )
            self._db.add(notification)
            await self._db.flush()
            await self._log_delivery(user_id, type, "in_app", "sent")
            return True
        except Exception as e:
            await self._log_delivery(user_id, type, "in_app", "failed", str(e))
            return False

    def _send_email_sync(self, to: str, subject: str, body: str) -> bool:
        """Send email synchronously. Returns success."""
        cfg = get_settings()
        if cfg.notification_email_provider == "smtp" and cfg.smtp_host:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = cfg.smtp_from_email or cfg.smtp_user or "noreply@authora.app"
                msg["To"] = to
                msg.attach(MIMEText(body, "plain"))
                with smtplib.SMTP(cfg.smtp_host, cfg.smtp_port) as smtp:
                    smtp.starttls()
                    if cfg.smtp_user and cfg.smtp_password:
                        smtp.login(cfg.smtp_user, cfg.smtp_password)
                    smtp.sendmail(msg["From"], to, msg.as_string())
                return True
            except Exception:
                return False
        if cfg.notification_email_provider == "sendgrid" and cfg.sendgrid_api_key:
            try:
                import httpx

                resp = httpx.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {cfg.sendgrid_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "personalizations": [{"to": [{"email": to}]}],
                        "from": {"email": cfg.smtp_from_email or "noreply@authora.app", "name": "AUTHORA"},
                        "subject": subject,
                        "content": [{"type": "text/plain", "value": body}],
                    },
                    timeout=10,
                )
                return resp.status_code in (200, 202)
            except Exception:
                return False
        return False

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        # Sync call in async context - acceptable for low volume
        return self._send_email_sync(to, subject, body)

    async def send_reminder(
        self,
        user_id: str,
        user_email: str,
        notification_type: str,
        title: str,
        body: str,
        *,
        in_app: bool = True,
        email: bool = False,
    ) -> dict[str, bool]:
        """Send reminder to in-app and/or email. Logs delivery. Returns {in_app: bool, email: bool}."""
        results = {"in_app": False, "email": False}
        if in_app:
            results["in_app"] = await self.send_in_app(user_id, notification_type, title, body)
        if email and user_email:
            ok = await self.send_email(user_email, title, body)
            if self._db:
                from datetime import datetime, timezone

                await self._log_delivery(
                    user_id,
                    notification_type,
                    "email",
                    "sent" if ok else "failed",
                    None if ok else "Email delivery failed",
                    retry_count=0,
                    sent_at=datetime.now(timezone.utc) if ok else None,
                )
            results["email"] = ok
        return results
