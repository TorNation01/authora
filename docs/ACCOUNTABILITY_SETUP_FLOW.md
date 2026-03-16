# Accountability Setup Flow

## Overview

Accountability is set during onboarding (pace step) and applied via the accountability API on completion. Users can adjust later in settings.

## Onboarding Options

- **No accountability** — I prefer to work without reminders
- **Gentle** — Soft nudges, no pressure
- **Structured** — Clear goals and check-ins
- **Buddy** — Community and encouragement

## Mapping to API

After onboarding completion:

- `none` → `reminder_enabled: false`
- `gentle` → `accountability_style: gentle`, `reminder_enabled: true`
- `structured` → `accountability_style: structured`, `reminder_enabled: true`
- `buddy` → `accountability_style: coach`, `reminder_enabled: true`

## API

- `PATCH /api/v1/accountability/settings` — Apply style and reminder preference
- `accountability_style` — gentle, balanced, firm, coach, structured
- `reminder_enabled` — boolean

## Full Settings

Users can later configure:

- Daily/weekly goals
- Reminder times
- Timezone
- Quiet hours
- Streak visibility
- Gamification level
- Encouragement preset

## Page

- `/dashboard/accountability` — Full accountability and progress UI
