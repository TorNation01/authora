# Guidance Mode Setup

## Overview

Guidance mode defines how much structure AUTHORA provides. Users choose during onboarding and project creation. They can change it later in project settings.

## Modes

### Guided

- Clear structure. Strong momentum.
- Let AUTHORA guide the path while you shape the voice.
- Framework as support, not a cage.

### Flexible

- A little structure, without the squeeze.
- Keep guidance where it helps.
- Let the project evolve as you write.

### Freeform

- Write your way. Keep the tools. Lose the rails.
- Structure is optional.
- Process flexible.

## Key Points

- **None of these options are wrong** — Copy explicitly states this
- **Change this later** — Users can adjust in project settings
- **Structure is here to help, not trap** — Reassuring tone

## Where It's Set

1. **Onboarding** — Step "How much guidance do you want?"
2. **Project wizard** — Step 1 "Choose project type"
3. **Project settings** — `guidance_mode` on project

## API

- Stored in `Project.guidance_mode` (or `knowledge_mode` for vault)
- Passed to `POST /api/v1/projects` and `POST /api/v1/projects/from-wizard`
