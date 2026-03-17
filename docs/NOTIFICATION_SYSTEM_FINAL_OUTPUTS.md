# Notification System — Final Outputs

## 1. Notification System Summary

AUTHORA provides a full notification system with in-app notifications, email delivery, reminders, and milestone alerts.

### In-App Notifications

- **Storage**: `notifications` table (user_id, type, title, body, read_at, created_at)
- **UI**: NotificationBell in sidebar (unread badge, dropdown), full page at `/dashboard/notifications`
- **API**:
  - `GET /api/v1/accountability/notifications` — List notifications (limit, unread_only)
  - `POST /api/v1/accountability/notifications/{id}/read` — Mark read
  - `POST /api/v1/accountability/notifications/test` — Send test notification

### Email Notifications

- **Providers**: SMTP or SendGrid (configurable via env)
- **Opt-in**: User must enable `email_reminders_enabled` in accountability settings
- **Templates**: HTML and plain-text reminder emails (supportive, clean design)
- **Fallback**: When email is not configured, in-app still works; no silent failures

### Reminders

- **Types**: daily, weekly, milestone, streak, overdue, finish_date_risk, resume, section, chapter_target, stuck, recovery
- **Settings**: `reminder_enabled`, `reminder_times`, `timezone`, `quiet_hours`, `reminder_types`, `reminder_style`
- **Scheduler**: `POST /api/v1/accountability/cron/reminders` (call from cron hourly)
- **Security**: `X-Cron-Secret` header when `CRON_SECRET` is set

### Milestone Alerts

- **Trigger**: When user is within ~500 words of an incomplete milestone
- **Type**: `milestone_reminder`
- **Message**: Encourages completion (e.g. "You're 300 words from your next milestone")
- **Runs**: Via reminder cron (process_milestone_reminders)

---

## 2. Delivery System Summary

### Channels

| Channel | Storage | When |
|---------|---------|------|
| **In-app** | `notifications` table | Always (when reminder sent) |
| **Email** | Optional | When `email_reminders_enabled` and user has email |

### Delivery Logging

- **Table**: `notification_delivery_logs` (user_id, notification_type, channel, status, error_message, retry_count, sent_at)
- **Status**: `sent`, `failed`, `pending`
- **API**: `GET /api/v1/accountability/delivery-logs` — User's delivery history

### Retry

- **Failed email**: Retried automatically (up to 3 times) on next cron run
- **Process**: `process_failed_email_retries` in reminder cron

### Flow

1. Cron calls `POST /accountability/cron/reminders` (hourly)
2. Reminder service evaluates users (timezone, quiet hours, reminder_times, conditions)
3. For each eligible user: `send_reminder(in_app=True, email=settings.email_reminders_enabled)`
4. In-app: Insert into `notifications`, log delivery
5. Email: Send via SMTP/SendGrid, log delivery (success or failure)
6. Failed emails: Queued for retry on next run

### Configuration

| Setting | Purpose |
|---------|---------|
| `notification_email_provider` | `none` \| `smtp` \| `sendgrid` |
| `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password` | SMTP config |
| `sendgrid_api_key` | SendGrid API key |
| `email_from` | From address |
| `CRON_SECRET` | Protects cron endpoint |

---

## 3. Production-Ready Confirmation

### Implemented Features

| Feature | Status | Notes |
|---------|--------|-------|
| In-app notifications | ✅ | Notification model, bell, full page |
| Email notifications | ✅ | SMTP/SendGrid, opt-in per user |
| Reminders | ✅ | 11+ types, timezone-aware, quiet hours |
| Milestone alerts | ✅ | Via milestone_reminder type |

### Components

| Component | Path |
|-----------|------|
| Notification model | `authora.models.notification` |
| NotificationDeliveryLog | `authora.models.notification_delivery_log` |
| DefaultNotificationService | `authora.infrastructure.notifications.impl` |
| Reminder service | `authora.services.reminder_service` |
| NotificationBell | `apps/web/src/components/notifications/NotificationBell.tsx` |
| Notifications page | `apps/web/src/app/dashboard/notifications/page.tsx` |

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/accountability/notifications` | List in-app notifications |
| POST | `/accountability/notifications/{id}/read` | Mark read |
| POST | `/accountability/notifications/test` | Send test |
| GET | `/accountability/delivery-logs` | List delivery logs |
| POST | `/accountability/cron/reminders` | Run reminder jobs (cron) |

### Production Checklist

- [ ] Set `CRON_SECRET` in production
- [ ] Configure cron: `0 * * * * curl -X POST -H "X-Cron-Secret: $CRON_SECRET" https://api.../accountability/cron/reminders`
- [ ] Configure email (SMTP or SendGrid) if email reminders desired
- [ ] Set `email_from` for outbound emails

### Observability

- Cron runs log `reminder_cron_completed` with counts (daily, weekly, section, resume, recovery_plans, email_retries)
- Delivery logs track success/failure per channel

---

## Related Documentation

- [REMINDER-SYSTEM.md](./REMINDER-SYSTEM.md) — Reminder types, configuration, scheduler
- [DEPLOYMENT.md](./DEPLOYMENT.md) — Cron setup and security
- [ENV-MAP.md](./ENV-MAP.md) — Environment variables
