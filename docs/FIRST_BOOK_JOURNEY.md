# First Book Journey

## Overview

The First Book Journey is a guided path from idea to finished manuscript. It helps beginners feel confident and supported while keeping experienced writers on track.

## Phases

1. **Define the book** — Capture core idea, inspiration, target reader
2. **Build the structure** — Expand concept, outline, key plot points or arguments
3. **Write the opening** — Break into chapters, create first chapter
4. **Keep the draft moving** — Write chapter by chapter, aim for progress
5. **Reach the midpoint** — Milestone checkpoint
6. **Finish the draft** — Complete first draft
7. **Revise with purpose** — Read through, revise, restructure
8. **Prepare for export** — Choose format, add metadata, export

## Journey Engine

- Phases stored in `journey_engine.py`: idea, concept, outline, chapter_planning, drafting, revision, polish, export_prep
- Mapped to user-facing labels from `FIRST_BOOK_JOURNEY` in `onboarding-copy.ts`
- Tasks per phase: checklist, action, milestone

## API

- `GET /api/v1/journey` — Full journey state, next step, nudge
- `GET /api/v1/journey/next-step` — Next recommended task
- `POST /api/v1/journey/tasks/complete` — Mark task complete
- `GET /api/v1/journey/recover` — Recovery nudge and next step

## UI

- `/dashboard/journey` — Journey page with phase progress, next step CTA, roadmap, checklist
- Dashboard card — "Review today's goal" with next step title when journey exists
