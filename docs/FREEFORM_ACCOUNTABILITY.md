# Freeform Accountability

When genre or framework guidance is turned off, the accountability system still works. It uses generic milestones, word-count and timeline-based goals, and avoids framework-specific prompts.

## What Works in Freeform Mode

- **Writing goals**: words_per_day, words_per_week, sessions_per_week, custom
- **Streaks**: Daily and weekly
- **Milestones**: Custom milestones (user-created)
- **Progress tracking**: Word count, chapters, sessions
- **Finish Mode**: Chapter-by-chapter completion
- **Nudges**: Generic encouragement (no framework-stage warnings)
- **Dashboard**: Full progress view

## Custom Milestones

In freeform mode, milestones are user-defined:

- **Title**: e.g. "Chapter 5 drafted"
- **Target words**: Optional
- **Target date**: Optional
- **Type**: `custom`, `chapter_count`, `word_count`, `deadline`

**API**: `POST /api/v1/accountability/milestones/custom`

## Goals

- **words_per_day**: e.g. 500
- **words_per_week**: e.g. 3500
- **sessions_per_week**: e.g. 5
- **chapters_per_month**: e.g. 2
- **custom**: User-defined target

No framework-specific goals (e.g. workbook_modules) unless user explicitly sets them.

## Nudges

- Generic messages: "A small session today keeps the book moving."
- No framework-stage warnings (e.g. "You're behind on Act II")
- Resume reminders: "Pick up where you left off."
- Stall detection: Same logic, generic messaging

## Finish Mode

- Chapter-by-chapter completion
- Word-count and timeline targets
- "Draft now, refine later" prompts
- No framework-specific beat reminders

## Dashboard

- Same structure as framework mode
- `framework_stage`: `null` or omitted
- `next_milestone`: From custom milestones only
- `next_suggested_step`: Based on last chapter, daily goal
