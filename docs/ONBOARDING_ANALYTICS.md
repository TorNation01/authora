# Onboarding Analytics

Production-ready event tracking for onboarding, activation, and drop-off measurement in AUTHORA.

## Overview

Events are recorded to the `analytics_events` table and used by admin dashboards and reporting. All events are idempotent where appropriate (e.g. `first_*` events fire only once per user).

## Event Catalog

### Activation Events (Positive Signals)

| Event | Description | Integration Point |
|-------|-------------|-------------------|
| `onboarding_started` | User began onboarding flow | `POST /journey/onboarding` |
| `onboarding_completed` | User completed onboarding | `POST /journey/onboarding` |
| `project_wizard_started` | User opened project creation wizard | Frontend (optional `POST /api/v1/analytics/events`) |
| `project_wizard_completed` | User completed project wizard | `POST /projects/from-wizard` |
| `first_project_created` | User created first project | `POST /projects`, `POST /projects/from-wizard` |
| `first_chapter_created` | User created first chapter | `POST /projects/{id}/books/{id}/chapters` |
| `first_writing_session_started` | User wrote words (first time) | `record_words` in gamification service |
| `first_milestone_completed` | User hit first word-count milestone | Gamification milestone award |
| `first_export_completed` | User completed first export | Export routes (docx, pdf, epub, etc.) |
| `first_ai_assist_used` | User used first AI action | `POST /ai/actions/run` |
| `first_idea_captured` | User captured first vault idea | `POST /projects/{id}/vault/ideas` |
| `first_streak_started` | User started first writing streak | `record_words` when streak ≥ 1 |

### Drop-off / Abandonment Events

| Event | Description | Detection |
|-------|-------------|-----------|
| `onboarding_abandonment` | Started but did not complete onboarding | Scheduled job |
| `template_selection_abandonment` | Opened wizard but did not select template | Scheduled job |
| `accountability_setup_abandonment` | Started accountability setup but did not finish | Scheduled job |
| `first_chapter_not_created` | Has project but no chapter | Scheduled job |
| `no_writing_within_3_days` | No writing session within 3 days of signup | Scheduled job |
| `no_return_within_7_days` | Did not return within 7 days | Scheduled job |

## Schema

Events are stored in `analytics_events`:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | User (nullable for anonymous) |
| `event_type` | string | Event identifier |
| `resource_type` | string | e.g. `project`, `chapter`, `book` |
| `resource_id` | string | Related resource ID |
| `properties` | JSONB | Event-specific payload |
| `created_at` | timestamptz | Event timestamp |

### Properties by Event

- **project_wizard_completed**: `template_slug`, `guidance_mode`, `starter_slug`, `template_id`
- **first_project_created**: `template_slug`, `from_wizard`
- **first_chapter_created**: `book_id`
- **first_export_completed**: `format`
- **first_ai_assist_used**: `action_slug`
- **first_milestone_completed**: `milestone_id`
- **abandonment events**: `step_index`, custom fields

## Integration Points

### Backend (Automatic)

Events are emitted at these touchpoints:

- **Journey**: `record_onboarding_started`, `record_onboarding_completed` in `submit_onboarding`
- **Projects**: `record_project_wizard_completed`, `record_first_project_created` in `create_project_from_wizard`; `record_first_project_created` in `create_project`
- **Books**: `record_first_chapter_created` in `create_chapter`
- **Export**: `record_first_export_completed` when `ExportJob` is created with `status=completed`
- **AI**: `record_first_ai_assist_used` after `log_ai_action` in `run_action_stream`
- **Vault**: `record_first_idea_captured` in `create_idea`
- **Gamification**: `record_first_writing_session_started`, `record_first_streak_started` in `record_words`; `record_first_milestone_completed` when awarding milestone

### Frontend (Optional)

For events only visible client-side (e.g. `project_wizard_started`), add a lightweight endpoint:

```
POST /api/v1/analytics/events
Body: { "event_type": "project_wizard_started" }
```

Then call it when the user navigates to the wizard. The backend can validate `event_type` against an allowlist.

## Service API

```python
from authora.services.onboarding_analytics import (
    record_onboarding_started,
    record_onboarding_completed,
    record_project_wizard_started,
    record_project_wizard_completed,
    record_first_project_created,
    record_first_chapter_created,
    record_first_writing_session_started,
    record_first_milestone_completed,
    record_first_export_completed,
    record_first_ai_assist_used,
    record_first_idea_captured,
    record_first_streak_started,
    record_abandonment,
)
```

## Idempotency

- `first_*` events: Only recorded once per user (checked before insert).
- `onboarding_started`, `onboarding_completed`: Recorded once per user.
- Other events (e.g. `project_wizard_completed`): Can fire multiple times; use for funnel analysis.

## Related

- [ACTIVATION_METRICS.md](./ACTIVATION_METRICS.md) – Metric definitions and dashboard usage
- [USER_DROP_OFF_SIGNALS.md](./USER_DROP_OFF_SIGNALS.md) – Drop-off detection and remediation
