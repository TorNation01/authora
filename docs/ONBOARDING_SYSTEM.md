# AUTHORA Onboarding System

## Overview

The onboarding system guides new users from signup to their first writing step. It is designed to feel **calm, premium, and exciting**—reducing overwhelm while helping users start fast.

## Flow

1. **Welcome** — Warm introduction, set expectations
2. **Writer type** — first_time, experienced, fiction, nonfiction, memoir, workbook, ghostwriter, collaborative, not_sure
3. **Book type** — Fiction or Non-fiction
4. **Guidance mode** — Guided, Flexible, Freeform
5. **Work style** — Solo, Co-write with AI, Ghostwriter
6. **Pace** — Timeline, schedule, accountability (none, gentle, structured, buddy)
7. **Complete** — Summary and redirect to project creation

## Key Features

- **Resume support** — Progress saved to localStorage and server (`/api/v1/journey/onboarding/progress`)
- **Skip option** — Users can skip and configure later
- **Accountability integration** — On completion, applies accountability style to settings
- **Preferences** — Stores `onboarding_completed`, `onboarding_writer_type`, `onboarding_guidance_mode`

## API

- `POST /api/v1/journey/onboarding` — Submit answers, create journey
- `POST /api/v1/journey/onboarding/progress` — Save progress for resume
- `GET /api/v1/journey/onboarding/progress` — Load saved progress
- `PATCH /api/v1/auth/me/preferences` — Store completion and preferences

## Dashboard Integration

- **Resume setup** — Shown when user has `onboarding_progress` but not `onboarding_completed`
- **Start the tour** — Shown when user has no journey
- **Quick start** — Continue writing, Focus mode, Notes, Revision, Export, New project

## Admin

- `/dashboard/admin/onboarding` — View onboarding configuration and experiment readiness
