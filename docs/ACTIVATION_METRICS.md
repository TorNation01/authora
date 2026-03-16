# Activation Metrics

Definitions, formulas, and usage for AUTHORA activation analytics.

## Core Metrics

### Activation Rate

**Definition**: Percentage of users (in period) who created at least one project.

**Formula**: `(distinct users with first_project_created) / (total users created in period) × 100`

**Use**: Primary indicator of whether users reach core value. Target: improve over time; benchmark against similar products.

### Onboarding Completion Rate

**Definition**: Of users who started onboarding, the percentage who completed it.

**Formula**: `(users with onboarding_completed) / (users with onboarding_started) × 100`

**Use**: Funnel health. Low completion suggests friction in onboarding steps.

### Time to First Project

**Definition**: Hours from user registration to first project created.

**Metrics**: Median, P90 (90th percentile).

**Use**: Speed-to-value. Shorter is better; long delays suggest confusion or drop-off.

### Time to First Chapter

**Definition**: Hours from first project created to first chapter created.

**Metrics**: Median, P90.

**Use**: Measures how quickly users move from setup to actual writing.

### First-Week Retention

**Definition**: Of users who created a first project, the percentage who also created a first chapter or completed a first export within the period (proxy for “returned and engaged”).

**Formula**: `(users with first_chapter or first_export) / (users with first_project) × 100`

**Use**: Early retention signal. Users who write or export in week one are more likely to stick.

## Template Usage

**Definition**: Count of projects created per template (from `project_wizard_completed` and `projects.template_id`).

**Use**: Which templates drive adoption; which to promote or deprecate.

## Mode Selection Rates

**Definition**: Count of project creations per guidance mode (`guided`, `flexible`, `freeform`).

**Use**: Product-market fit for guidance options; informs default recommendations.

## Starter Path Usage

**Definition**: Count of project creations per starter slug (from `project_wizard_completed.properties.starter_slug`).

**Use**: Which starter paths resonate; optimize onboarding flows.

## Admin Dashboard

**Location**: `/dashboard/admin/activation`

**API**: `GET /api/v1/admin/activation?days=30`

**Response**:

```json
{
  "period_days": 30,
  "summary": {
    "total_users": 150,
    "activation_rate_pct": 62.0,
    "onboarding_completion_rate_pct": 78.5,
    "event_counts": { ... }
  },
  "time_to_first_project": [...],
  "time_to_first_chapter": { "count": 80, "median_hours": 2.1, "p90_hours": 24.5 },
  "template_usage": [...],
  "mode_selection_rates": [...],
  "starter_path_usage": [...],
  "first_week_retention": { "total": 93, "returned_within_7_days": 45, "retention_pct": 48.4 }
}
```

## Aggregation Logic

- **Period**: Configurable `days` (7–90). Events and users are filtered by `created_at >= now - days`.
- **Event counts**: Distinct users per event type in period.
- **Time-to-value**: Joins `analytics_events` with `users` or other events; computes deltas in Python for clarity.

## Related

- [ONBOARDING_ANALYTICS.md](./ONBOARDING_ANALYTICS.md) – Event catalog and integration
- [USER_DROP_OFF_SIGNALS.md](./USER_DROP_OFF_SIGNALS.md) – Drop-off signals and remediation
