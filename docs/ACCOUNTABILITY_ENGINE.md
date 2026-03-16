# Accountability Engine

The AUTHORA accountability engine helps writers finish books through goals, streaks, milestones, nudges, stall detection, and Finish Mode. It supports both gentle and high-accountability writers and works for fiction, nonfiction, and freeform projects.

## Core Principles

- Support motivation without becoming annoying
- Encourage consistency without guilt-heavy pressure
- Support both gentle and high-accountability writers
- Make finishing feel achievable
- Work for fiction and non-fiction
- Adapt to project type, framework, and writing pace
- Remain optional and user-adjustable

## Components

### 1. Writing Goals System

**Target types**: `words_per_day`, `words_per_week`, `sessions_per_week`, `chapters_per_month`, `scenes_per_month`, `workbook_modules`, `memoir_sections`, `custom`

**Presets**:
- **Gentle**: 250 words/day, 1500 words/week, 3 sessions/week
- **Balanced**: 500 words/day, 3500 words/week, 5 sessions/week
- **Aggressive**: 1000 words/day, 7000 words/week, 6 sessions/week

**Features**:
- Project-specific or book-specific goals
- Pause/resume goals
- Low-energy mode
- Holiday/reset modes
- Fallback defaults from template/framework

**API**:
- `GET /api/v1/goals` — List goals (filter by project_id, book_id, active_only)
- `POST /api/v1/goals` — Create goal (preset or custom)
- `PATCH /api/v1/goals/{id}` — Update goal
- `POST /api/v1/goals/{id}/pause` — Pause goal
- `POST /api/v1/goals/{id}/resume` — Resume goal
- `DELETE /api/v1/goals/{id}` — Delete goal

### 2. Streak System

- **Daily writing streak**: Consecutive days with words written
- **Longest streak**: All-time best
- **Grace days**: Optional buffer (0–7) for missed days
- **Flexible streak mode**: Weekly consistency instead of strict daily
- **Streak visibility**: Can be hidden for users who find it stressful

**Settings** (`AccountabilitySettings`):
- `streak_visible`: Show/hide streak
- `grace_days`: Number of grace days
- `flexible_streak_mode`: Use weekly consistency logic

### 3. Milestone Engine

**Framework-aware milestones** (from template):
- Fiction: premise, outline, act I/II/III, first draft, revision, beta, export
- Nonfiction: outline, intro, core chapters, conclusion, revision, expert review, export

**Freeform milestones**:
- Custom title and target
- Chapter-count or word-count based
- Deadline-based

**API**:
- `GET /api/v1/accountability/milestones` — List milestones (book_id optional)
- `POST /api/v1/accountability/milestones/generate` — Generate from template
- `POST /api/v1/accountability/milestones/custom` — Create custom milestone
- `POST /api/v1/accountability/milestones/{id}/complete` — Mark complete

### 4. User Preference Controls

**Accountability level**: `off` | `light` | `standard` | `strong`

**Encouragement presets**:
- Gentle Encouragement
- Steady Coach
- Finish Strong
- Minimal Interruption

**Settings** (`AccountabilitySettings`):
- `accountability_level`
- `encouragement_preset`
- `reminder_style`
- `streak_visible`
- `gamification_enabled`
- `no_reminder_mode`
- `grace_days`
- `flexible_streak_mode`

### 5. Progress Dashboard

Unified view aggregating:
- Current project/book
- Goals (daily, weekly, words today/this week)
- Streaks (current, longest)
- Consistency score
- Milestones reached / next milestone
- Framework stage (if enabled)
- Next suggested step
- Finish risk indicator
- Writing history (last 14 days)
- Gamification (if enabled)

**API**:
- `GET /api/v1/accountability/progress` — Full dashboard (project_id, book_id optional)
- `GET /api/v1/accountability/progress/weekly` — Weekly summary
- `GET /api/v1/accountability/progress/monthly` — Monthly summary

## Data Model

- **AccountabilitySettings**: User preferences (goals, reminders, streaks, gamification)
- **Goal**: Writing goals (target_type, target_value, project_id, book_id, is_paused)
- **Milestone**: Plan milestones (milestone_type, framework_stage, sort_order)
- **UserStats**: Streaks, XP, total words (grace_days_used)
- **StreakLog**: Daily word counts
- **WritingPlan**, **ChapterTarget**, **RecoveryPlan**: Plan and recovery data

## Integration

- **Gamification**: XP, badges, quests when `gamification_enabled`
- **Reminders**: Nudges respect `no_reminder_mode`, `accountability_level`
- **Finish Mode**: Uses progress dashboard for next step and finish risk
