# Reminder & Notification System

AUTHORA's reminder system is fully operational for production. It supports in-app and email reminders, timezone-aware scheduling, quiet hours, and graceful degradation when email is not configured.

## Reminder Types

| Type | When | Purpose |
|------|------|---------|
| `daily_reminder` | At configured times, when daily goal not met | Nudge toward daily word goal |
| `weekly_reminder` | Monday, when weekly goal not met | Weekly check-in |
| `milestone_reminder` | When close to milestone (≤500 words) | Encourage milestone completion |
| `streak_reminder` | When streak ≥3 days and no words today | Preserve streak |
| `overdue_nudge` | When plan past finish date | Supportive catch-up |
| `finish_date_risk` | When finish date at risk (≤14 days) | Alert and suggest adjustment |
| `resume_reminder` | 2+ days since last write | Resume last chapter |
| `section_reminder` | 1 day since last write | "You were working on this" |
| `chapter_target_reminder` | When chapter target within 300 words | Chapter completion nudge |
| `stuck_nudge` | 5+ days since last write | Supportive re-engagement |
| `missed_goal_recovery` | When recovery plan created | Notify about recovery plan |

## UX Principles

- **Motivating tone**: Supportive, never guilt-heavy. Copy aligned with accountability-copy.ts.
- **Not annoying**: Opt-in reminders, quiet hours, per-type toggles, plan pause.
- **Optional controls**: Users choose reminder_enabled, email_reminders_enabled, reminder_types, reminder_times, timezone, quiet hours. Full control in Progress settings.

## Tone Modes

- **Gentle**: Soft nudges, no pressure
- **Balanced**: Supportive check-ins
- **Firm**: Clear expectations
- **Coach**: Motivating and strategic
- **Structured**: Schedules and milestones

## Configuration

### User Settings (AccountabilitySettings)

- `reminder_enabled`: Opt-in; must be true for any reminders
- `reminder_times`: e.g. `["09:00", "14:00"]` in user timezone
- `timezone`: IANA timezone (e.g. `America/New_York`)
- `quiet_hours_start` / `quiet_hours_end`: No reminders during this window
- `email_reminders_enabled`: Opt-in for email (requires admin email config)
- `reminder_cadence`: `daily` | `weekly` | `both`
- `reminder_types`: List of enabled types; `null` = all enabled
- `accountability_style`: Tone mode

### Email Configuration

- `notification_email_provider`: `none` | `smtp` | `sendgrid`
- `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`
- `smtp_from_email` or `from_email` (setup wizard uses `FROM_EMAIL`)

When email is not configured, in-app notifications still work. No silent failures.

## Scheduler

Reminders run via HTTP cron:

```
POST /api/v1/accountability/cron/reminders
Header: X-Cron-Secret: <CRON_SECRET>  (when CRON_SECRET is set)
```

**Recommended schedule**: Every hour (e.g. `0 * * * *`). Daily reminders use the hour to match user times; weekly runs on Monday; others run when conditions are met.

## Delivery & Retry

- **In-app**: Always stored in `notifications` table
- **Email**: Logged in `notification_delivery_logs`
- **Failed email**: Retried automatically (up to 3 times) on next cron run
- **Retry**: Uses matching in-app notification for title/body

## Notification Center

- **Path**: `/dashboard/notifications`
- **Tabs**: Notifications (in-app), Delivery logs
- **Actions**: Mark read, mark all read

## Test Flow

1. Enable reminders in Progress settings
2. Click "Send test notification"
3. Check bell icon for in-app; check inbox if email enabled

## Observability

Cron runs log `reminder_cron_completed` with counts for daily, weekly, section, resume, recovery_plans, email_retries.
