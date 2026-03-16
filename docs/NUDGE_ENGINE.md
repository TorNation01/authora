# Nudge Engine

The nudge engine powers reminders and supportive messages. It respects user preferences, quiet hours, timezone, and accountability level.

## Reminder Styles

| Style | Description | Example |
|-------|-------------|---------|
| gentle | Soft, no pressure | "A gentle nudge: your writing space is waiting today." |
| balanced | Supportive check-ins | "Time to write! Your daily goal is 500 words." |
| firm | Clear expectations | "Daily goal: 500 words. Your commitment is waiting." |
| coach | Motivating, strategic | "Coach check-in: 500 words today. What's your first sentence?" |
| structured | Schedules, milestones | "[2025-03-15] Daily target: 500 words." |
| minimal | Short, low-interruption | "A small session today keeps the book moving." |

## Reminder Types

| Type | When | Purpose |
|------|------|---------|
| daily_reminder | At configured times, goal not met | Nudge toward daily goal |
| weekly_reminder | Monday, weekly goal not met | Weekly check-in |
| milestone_reminder | Close to milestone (≤500 words) | Encourage completion |
| streak_reminder | Streak ≥3, no words today | Preserve streak |
| overdue_nudge | Plan past finish date | Supportive catch-up |
| finish_date_risk | Finish date at risk (≤14 days) | Alert and suggest |
| resume_reminder | 2+ days since last write | Resume last chapter |
| section_reminder | 1 day since last write | "You were working on this" |
| chapter_target_reminder | Chapter target within 300 words | Chapter completion |
| stuck_nudge | 5+ days since last write | Re-engagement |
| missed_goal_recovery | Recovery plan created | Notify about plan |

## Minimal-Style Messages

- "A small session today keeps the book moving."
- "You are closer than you think. Pick up where you left off."
- "One finished section beats another postponed perfect draft."
- "Your manuscript is waiting. Let's move it forward."
- "Even 15 minutes counts today."

## User Controls

- **no_reminder_mode**: Disable all reminders
- **accountability_level**: `off` skips reminders
- **reminder_types**: Whitelist of enabled types; `null` = all
- **quiet_hours_start/end**: No reminders during window
- **timezone**: For scheduling
- **reminder_times**: e.g. `["09:00", "14:00"]`

## Stall Detection

**Triggers**:
- 5+ days since last write
- Missed goals
- Inactivity windows
- (Future) Abandoned chapters, revision looping, high notes vs low draft

**Response**:
- Gentle check-in (stuck_nudge)
- Suggested next step
- Small-win recommendation
- "Resume from here" guidance
- Non-punitive tone

## Finish Mode Nudges

When Finish Mode is enabled:
- Momentum-focused messages
- "Draft now, refine later" prompts
- Project-end countdown
- 7-day, 14-day, 30-day sprint options

## Cron

```
POST /api/v1/accountability/cron/reminders
Header: X-Cron-Secret: <CRON_SECRET>
```

Run hourly. All reminder types are processed in one pass.
