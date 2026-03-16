# Finish Mode

Finish Mode is a dedicated completion-focused workflow that helps users actually finish their manuscript.

## Purpose

- Reduce interface clutter
- Focus on remaining chapters only
- Show exact remaining work
- Create daily completion plans
- Break work into small achievable tasks
- Resume directly into the next unfinished section
- Reduce perfectionism paralysis
- Support sprint writing sessions
- Provide encouraging finish-line messaging
- Celebrate final milestones
- Create emotional momentum toward completion

## Activation

### Manual Entry

- **When**: Available when the book has 1+ chapters
- **How**: "Enter Finish Mode" in the manuscript sidebar

### Suggested Entry

- **When**: 70%+ progress, 5 or fewer chapters remaining, Finish Mode not yet on
- **How**: Banner in sidebar: "Enter Finish Mode — you're almost there"

## Features

### Progress & Remaining Work

- Progress bar (chapters done / total)
- Words remaining estimate (based on avg per chapter)
- Days to finish (from target date or pace)

### Daily Plan

- **Today's focus**: Specific chapter + target words
- **"Just finish this section"**: One-click jump to next chapter
- **Suggested session**: 25-minute sprint

### Completion Forecast

- On-track / adjust-pace indicator
- Estimated completion date (from recent writing pace)
- Avg words/day this week

### Final Stretch (Last 1–3 Chapters)

- Celebratory messaging: "One chapter left. This is it."
- Highlighted state in sidebar and panel

### Sprint Sessions

- **Duration options**: 7-day, 14-day, 30-day completion pushes
- **Project-end countdown**: Days until target date
- **5m, 15m, 25m** sprint timer
- Tracks words written during sprint
- Integrates with gamification

### Momentum Messages

- "Draft now, refine later. Keep the momentum."
- "One finished section beats another postponed perfect draft."
- "Your manuscript is waiting. Let's move it forward."
- "Done is better than perfect. Keep going."
- "A small session today keeps the book moving."

### Completion Ceremony

- When all chapters are marked "done"
- Full-screen celebration: "You did it."
- Export manuscript (.docx) or backup
- Exit Finish Mode

## Settings

- **Target finish date** (optional): Drives days-to-finish and daily plan
- **Words per day**: Default 500; used for daily plan and forecast

## API

- `GET /api/v1/projects/:id/books/:bookId/finish-mode` — Stats, forecast, daily plan
- `PATCH /api/v1/projects/:id/books/:bookId/finish-mode` — Enable/disable, update settings

## Data Model

Finish Mode settings live in `book_settings.settings.finish_mode`:

- `enabled`: boolean
- `target_date`: ISO date string (optional)
- `words_per_day`: number (100–5000)

Chapters use `section_status` (`draft` | `revising` | `review` | `done`) to determine completion.
