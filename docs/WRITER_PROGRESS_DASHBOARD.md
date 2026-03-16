# Writer Progress Dashboard

The progress dashboard is a unified view of writing progress, goals, streaks, milestones, and next actions.

## Endpoints

### GET /api/v1/accountability/progress

**Query params**: `project_id`, `book_id` (optional)

**Response**:
```json
{
  "current_project": { "id": "...", "name": "..." },
  "current_book": { "id": "...", "title": "..." },
  "goals": {
    "daily": 500,
    "weekly": 3500,
    "words_today": 200,
    "words_this_week": 1200
  },
  "streaks": { "current": 3, "longest": 7 },
  "consistency_score": 75.0,
  "milestones_reached": [
    { "id": "...", "title": "Outline complete", "completed_at": "..." }
  ],
  "next_milestone": { "id": "...", "title": "Act I draft", "target_words": 15000 },
  "framework_stage": "framework_enabled",
  "next_suggested_step": {
    "message": "Resume where you left off...",
    "chapter_id": "...",
    "chapter_title": "...",
    "target_words": 500
  },
  "finish_risk": "deadline_approaching",
  "stuck": false,
  "plan_paused": false,
  "writing_history": [
    { "date": "2025-03-15", "words": 500 },
    ...
  ],
  "gamification": { "xp": 1200, "level": 2, "total_words": 25000 }
}
```

### GET /api/v1/accountability/progress/weekly

**Response**:
```json
{
  "week_start": "2025-03-10",
  "words_this_week": 2500,
  "days_written": 4
}
```

### GET /api/v1/accountability/progress/monthly

**Response**:
```json
{
  "month": "2025-03",
  "words_this_month": 8500,
  "days_written": 12
}
```

## Finish Risk

- **deadline_approaching**: Target date within 7 days
- **stall_detected**: Stuck (5+ days no write)
- **null**: No risk

## Next Suggested Step

- **With Finish Mode**: `daily_plan_today` (chapter, target words, session minutes)
- **Without**: `{ "message": "Resume where you left off..." }`

## Gamification

When `gamification_enabled` in settings:
- `xp`, `level`, `total_words` included
- Otherwise `gamification: null`

## Streak Visibility

When `streak_visible` is false:
- `streaks.current` and `streaks.longest` are `null`
