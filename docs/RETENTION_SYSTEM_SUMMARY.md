# Retention and Momentum System — Summary

The AUTHORA retention system keeps users coming back and finishing their books through goals, streaks, daily prompts, reminders, Finish Mode, and progress visualization. This document summarizes the implemented features and confirms production readiness.

---

## 1. Goals System

**Implemented**:
- **Daily goals**: User-configurable word count target per day
- **Weekly goals**: User-configurable word count target per week
- **Project goals**: Book-specific goals with deadlines (via `/api/v1/goals`)

**Settings**:
- Goals stored in `AccountabilitySettings` (`daily_word_goal`, `weekly_word_goal`)
- **Presets** (Gentle / Balanced / Structured):
  - **Gentle**: 250 words/day, 1,750 words/week
  - **Balanced**: 500 words/day, 3,500 words/week
  - **Structured**: 1,000 words/day, 7,000 words/week

**Presets** are available in Settings (Accountability page) as one-click buttons.

---

## 2. Streak System

**Implemented**:
- **Writing streaks**: Consecutive days with words written
- **Activity streaks**: Tracked via `UserStats` and `StreakLog`

**Display**:
- Non-gamified, motivating copy: “X days of writing” (not “X days”)
- “Keep going.” as encouragement
- Shown on dashboard (`RetentionProgressWidget`) and accountability page

**API**:
- `GET /api/v1/accountability/overview` returns `current_streak`

---

## 3. Daily Prompts

**Implemented**:
- **Daily writing prompts**: Date-seeded prompt shown on dashboard
- **Template-aware**: When user has a project with a template, prompts prefer that genre (romance, thriller, memoir, etc.)
- **Motivating tone**: Prompts are suggestive, not prescriptive; optional to use

**Display**:
- `DailyPromptCard` on dashboard above progress widget
- Copy: "Today's prompt" with optional hint ("Ignore if you're already in the flow")

**API**:
- `GET /api/v1/accountability/daily-prompt?date=YYYY-MM-DD&project_id=...` returns `{ prompt, date, source }`

---

## 4. Reminders

**Implemented**:
- **Daily reminders**: Configurable times (e.g. 9:00, 14:00)
- **Flexible scheduling**: `reminder_times`, `timezone`, `quiet_hours`, `reminder_cadence`, `reminder_types`
- **Pause/resume**: `plan_paused` to pause all reminders
- **Test notification**: In-app and email test sends

**Settings**:
- `reminder_enabled`, `reminder_times`, `timezone`, `quiet_hours_start`, `quiet_hours_end`
- `email_reminders_enabled`, `reminder_cadence`, `reminder_types`

---

## 5. Finish Mode

**Implemented**:
- **Focused completion mode**: Dedicated UI for finishing manuscripts
- **Milestone tracking**: Chapters done vs total, progress per chapter
- **Structured push to finish**: Next suggested step, words-per-day estimate

**Components**:
- `FinishModePanel`, `FinishModeSidebar`, `FinishModeCompletionCeremony`, `FinishModeSettingsDialog`
- `FinishModeStats`: `chapters_done`, `chapters_total`, `progress_pct`, `milestone_message`

**API**:
- Finish Mode logic in `authora.services.finish_mode`

---

## 6. Progress Visualization

**Implemented**:

| Location | Widget | Data |
|----------|--------|------|
| **Dashboard** | `DailyPromptCard`, `RetentionProgressWidget` | Daily prompt, Today, This week, Streak, Consistency |
| **Project page** | `ProjectProgressCard` | Total words, chapters done/total, % complete (from `/api/v1/projects/{id}/progress`) |
| **Accountability page** | Today, This week, Consistency, Streak cards | Same overview |
| **Finish Mode** | `FinishModePanel` | Chapters progress, milestones, next step |

**APIs**:
- `GET /api/v1/accountability/overview` — daily, weekly, streak, consistency
- `GET /api/v1/projects/{project_id}/progress` — total words, chapters, progress %

---

## 7. Progress Tracking Summary

| Metric | Source | Display |
|--------|--------|---------|
| Words today | `accountability/overview` | Dashboard, Accountability |
| Words this week | `accountability/overview` | Dashboard, Accountability |
| Words per project | `projects/{id}/progress` | Project page |
| Chapters done | `projects/{id}/progress` | Project page |
| Chapters total | `projects/{id}/progress` | Project page |
| % complete | Derived (chapters_done / total) | Project page, Finish Mode |
| Current streak | `accountability/overview` | Dashboard, Accountability |
| Consistency (4 weeks) | `accountability/overview` | Dashboard, Accountability |

---

## 8. Production Readiness

**Production-ready**:
- [x] Goals system with presets
- [x] Streak system (non-gamified display)
- [x] Daily prompts (date-seeded, template-aware)
- [x] Reminders with flexible scheduling
- [x] Finish Mode with milestone tracking
- [x] Progress visualization (dashboard, project, accountability)
- [x] API endpoints for overview and project progress
- [x] Error handling and graceful fallbacks (widgets return null on failure)

**Integration**:
- Dashboard: `DailyPromptCard` (optional prompt), `RetentionProgressWidget` links to `/dashboard/accountability`
- Project page: `ProjectProgressCard` shows above books list
- Accountability page: Settings, goals, streaks, reminders, recovery plans

**Tone**:
- Supportive, motivating, premium, calm
- No guilt-heavy or childish gamification
- Copy aligned with `accountability-copy.ts` (GOALS_COPY, STREAK_COPY, etc.)

---

## Related Documentation

- [ACCOUNTABILITY_ENGINE.md](./ACCOUNTABILITY_ENGINE.md) — Goals, streaks, milestones, Finish Mode
- [FINISH-MODE.md](./FINISH-MODE.md) — Finish Mode details
- [REMINDER-SYSTEM.md](./REMINDER-SYSTEM.md) — Reminders and scheduling
