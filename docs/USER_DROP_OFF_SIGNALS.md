# User Drop-Off Signals

Detection logic and remediation ideas for onboarding and activation drop-off in AUTHORA.

## Drop-Off Signals

### 1. Onboarding Abandonment

**Signal**: `onboarding_abandonment`

**Definition**: User has `onboarding_started` but no `onboarding_completed`, and sufficient time has passed (e.g. 24–48 hours).

**Detection**:

- Query users with `onboarding_started` event and no `onboarding_completed` event.
- Filter by `created_at` older than threshold (e.g. 24h).
- Record `record_abandonment(db, user_id, "onboarding_abandonment", step_index=last_step)`.

**Remediation**:

- Email: “You started setting up AUTHORA. Pick up where you left off.”
- In-app: Resume onboarding from last saved step (`UserPreference.preferences.onboarding_progress`).

---

### 2. Template Selection Abandonment

**Signal**: `template_selection_abandonment`

**Definition**: User has `project_wizard_started` but no `project_wizard_completed` within a window (e.g. 24h).

**Detection**:

- Requires `project_wizard_started` to be emitted (frontend or backend).
- Users with `project_wizard_started` and no `project_wizard_completed` after threshold.

**Remediation**:

- Email: “Choose a template to get started.”
- In-app: Highlight “Create project” and template picker.

---

### 3. Accountability Setup Abandonment

**Signal**: `accountability_setup_abandonment`

**Definition**: User started accountability setup (e.g. opened settings or first step) but did not complete (e.g. no `AccountabilitySettings` or incomplete).

**Detection**:

- Heuristic: User has project, has been shown accountability flow, but `AccountabilitySettings` is missing or incomplete.
- May require a `accountability_setup_started` event if not inferable from existing data.

**Remediation**:

- Nudge: “Set a writing goal to stay on track.”
- Simplify: Reduce steps or make setup optional.

---

### 4. First Chapter Not Created

**Signal**: `first_chapter_not_created`

**Definition**: User has at least one project but no chapter, and project is older than threshold (e.g. 3–7 days).

**Detection**:

- Users with `Project` but no `Chapter` in any of their books.
- Filter by `Project.created_at` older than threshold.

**Remediation**:

- Email: “Your project is ready. Add your first chapter.”
- In-app: Prominent “Add chapter” CTA, optional guided first-chapter flow.

---

### 5. No Writing Within 3 Days

**Signal**: `no_writing_within_3_days`

**Definition**: User registered 3+ days ago but has no `first_writing_session_started` (no `StreakLog` or `record_words` call).

**Detection**:

- Users with `User.created_at` older than 3 days.
- No `first_writing_session_started` event (or no `StreakLog` entries).

**Remediation**:

- Email: “Your first words are waiting. Open a chapter and start writing.”
- In-app: Highlight editor, offer “Start writing” tour.

---

### 6. No Return Within 7 Days

**Signal**: `no_return_within_7_days`

**Definition**: User had activity (e.g. first project or first chapter) but no activity in the last 7 days.

**Detection**:

- Users with `first_project_created` or `first_chapter_created`.
- No `AnalyticsEvent` or `StreakLog` (or similar) in last 7 days.
- Approximate “return” via: new `StreakLog`, new `Chapter` update, new export, new AI action.

**Remediation**:

- Email: “We miss you. Your manuscript is waiting.”
- In-app: Recovery nudge, streak reminder if applicable.

---

## Implementation: Scheduled Job

A cron or background job should run periodically (e.g. daily) to:

1. Query users matching each drop-off condition.
2. Call `record_abandonment(db, user_id, event_type, ...)` for each.
3. Optionally trigger emails or in-app nudges via existing notification system.

**Example job structure**:

```python
# In a scheduled task (e.g. Celery, APScheduler, or cron-invoked script)
async def detect_drop_offs(db: AsyncSession) -> None:
    # 1. Onboarding abandonment
    # 2. Template selection abandonment (if project_wizard_started exists)
    # 3. First chapter not created
    # 4. No writing within 3 days
    # 5. No return within 7 days
    ...
```

## Event Recording

Use the onboarding analytics service:

```python
from authora.services.onboarding_analytics import record_abandonment

await record_abandonment(
    db,
    user_id,
    "first_chapter_not_created",
    step_index=None,
    properties={"project_id": str(project_id), "days_since_project": 5},
)
```

## Dashboard Usage

Drop-off events can be aggregated for admin dashboards:

- Count per signal type over a period.
- List of users per signal for outreach or support.
- Trend over time to measure impact of remediation.

## Related

- [ONBOARDING_ANALYTICS.md](./ONBOARDING_ANALYTICS.md) – Event catalog
- [ACTIVATION_METRICS.md](./ACTIVATION_METRICS.md) – Metric definitions
