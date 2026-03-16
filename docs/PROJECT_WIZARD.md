# Project Creation Wizard

## Overview

The project creation wizard guides users through a 7-step flow to create a new project and book from a template.

## Entry Points

- **Dashboard** → New project → Choose "Guided start"
- Direct: `/dashboard/projects/new`

## Wizard Steps

| Step | Title | Content |
|------|-------|---------|
| 1 | Choose project type | Grid of template categories (Fiction, Non-fiction, Memoir, etc.) |
| 2 | Choose genre / Name | If category has children: genre dropdown. Else: project name + book title |
| 3 | Name your project | Project name + book title (when step 2 was genre) |
| 4 | Define your core idea | Textarea for one-sentence premise |
| 5 | Select structure style | Optional dropdown (3-act, hero's journey, etc.) |
| 6 | Set your writing goals | Optional target words, target date |
| 7 | Ready to create | Summary + Create button |

## Step Skipping

- When the selected category has **no children** (e.g. Memoir, Workbook), step 2 shows the name form and step 3 is skipped (Next goes from 2 → 4).
- When the selected category **has children** (e.g. Fiction), step 2 shows genre selection, step 3 shows name.

## API

**Create from wizard**

```
POST /api/v1/projects/from-wizard
Content-Type: application/json

{
  "template_id": "uuid | null",
  "project_name": "My Novel",
  "book_title": "Optional",
  "book_type": "fiction",
  "genre": "Romance",
  "core_idea": "...",
  "structure_framework": "three_act",
  "target_words": 80000,
  "target_date": "2025-12-31"
}

Response:
{
  "project": { "id": "...", "name": "...", ... },
  "book_id": "uuid",
  "book_title": "..."
}
```

## Post-Creation

On success, the user is redirected to:

```
/dashboard/projects/{project_id}/books/{book_id}/plan
```

## Quick Start

Users can choose "Quick start" instead of the wizard:

- Single field: project name
- Creates project only (no book)
- User adds books from project page
