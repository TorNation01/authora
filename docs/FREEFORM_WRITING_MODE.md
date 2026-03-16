# Freeform Writing Mode

Freeform mode disables genre-specific and framework-specific guidance while keeping all core writing tools.

## What Works

- **Planning**: Minimal structure (one blank chapter by default)
- **Writing**: Full editor, notes, search
- **Accountability**: Goals, streaks, reminders, Finish Mode
- **Milestones**: Custom milestones only (user-created)
- **Progress dashboard**: Word count, consistency, next step
- **Export**: Full export support

## What's Disabled

- Genre-specific AI prompts
- Framework beat/stage tracking
- Template-driven chapter structure
- Framework-stage warnings in dashboard
- Genre-aware milestone generation

## Project Creation

- **Wizard**: Select "Freeform" at step 1; template selection is skipped (template_id=null)
- **Quick create**: Defaults to freeform (minimal structure)

## Milestones

In freeform mode, milestone generation uses generic defaults:

- Outline complete
- First draft complete
- First revision pass
- Final polish

Users can create custom milestones via `POST /api/v1/accountability/milestones/custom`.

## Switching to Freeform

- **From Guided/Flexible**: PATCH project with `guidance_mode: "freeform"`
- **Content preserved**: Manuscript, notes, chapters unchanged
- **Framework/template references**: Kept in DB but not used for prompts or milestones
