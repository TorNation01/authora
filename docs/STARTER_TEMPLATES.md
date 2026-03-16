# Starter Templates System

A premium starter template and quick-start project system for AUTHORA that helps users begin with confidence by offering high-quality starting paths for common book types.

## Overview

The starter system provides 14 preconfigured paths, each with:

- **Who it's for** – Target audience description
- **Guidance level** – `guided` (full structure), `flexible` (lighter), or `freeform` (minimal)
- **Preconfigured milestones** – From the underlying template
- **Workspace modules** – Via `knowledge_mode` (fiction, nonfiction, memoir, workbook, hybrid)
- **Suggested exports** – docx, epub, pdf, etc.
- **AI assist defaults** – Prompt suggestions for the book type
- **Accountability suggestions** – Milestone and goal ideas

## Starter Paths

| Starter | Template Slug | Guidance | Knowledge Mode |
|---------|---------------|----------|----------------|
| Fiction Novel | fiction | guided | fiction |
| Romance Novel | fiction-romance | guided | fiction |
| Fantasy / Speculative | fiction-fantasy | guided | fiction |
| Thriller / Mystery | fiction-thriller | guided | fiction |
| Literary Fiction | fiction-literary | flexible | fiction |
| Memoir | memoir | guided | memoir |
| Personal Story / Life Lessons | nonfiction-personal-story | flexible | memoir |
| Business / Authority Book | nonfiction-business | guided | nonfiction |
| How-to Non-fiction | nonfiction-howto | guided | nonfiction |
| Self-help | nonfiction-selfhelp | guided | nonfiction |
| Workbook | workbook | guided | workbook |
| Guided Journal | journal | flexible | workbook |
| Ghostwritten Book | ghostwritten-book | guided | hybrid |
| Blank Project | (none) | freeform | fiction |

## User Actions

- **Use this starter** – Quick create: name project (and optional book title), then create with template preconfigured
- **Customize** – Open the guided wizard with this template pre-selected for full setup
- **Start blank instead** – Create a minimal project with no template
- **Save as template** – (Coming soon) Save a customized project as a reusable template

## Implementation

### Frontend

- `apps/web/src/content/starter-templates.ts` – Starter metadata (who, guidance, exports, etc.)
- `apps/web/src/components/onboarding/StarterTemplateCard.tsx` – Single starter card
- `apps/web/src/components/onboarding/StarterTemplateSelector.tsx` – Grid with search and grouping

### Backend

- `apps/api/authora/data/starter_definitions.py` – Starter ID → template slug mapping
- `apps/api/authora/data/template_definitions.py` – Template definitions (includes `nonfiction-personal-story`)
- `GET /api/v1/templates/starters` – Returns `{ id, template_id }[]` for slug resolution

### Project Creation Flow

1. User lands on `/dashboard/projects/new` → sees starter grid
2. Clicks **Use this starter** → quick form (name, optional book title) → `POST /api/v1/projects/from-wizard`
3. Clicks **Customize** → guided wizard with template pre-selected
4. Clicks **Start blank instead** → quick form → from-wizard with `template_id: null`, `guidance_mode: freeform`

## Adding a New Starter

1. Add template to `template_definitions.py` if it doesn't exist
2. Add entry to `starter_definitions.py` with `id` and `template_slug`
3. Add full metadata to `starter-templates.ts` in `STARTER_TEMPLATES`
4. Run `python -m apps.api.authora.scripts.seed_project_templates` to seed new templates
