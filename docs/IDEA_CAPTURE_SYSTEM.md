# Idea Capture System

The AUTHORA Idea Capture system stores quick notes, scene ideas, plot twists, dialogue snippets, and thematic notes with flexible linking and status tracking.

## Overview

- **Project-scoped**: Ideas belong to a project.
- **Rich types**: Quick notes, idea cards, scene/chapter/title ideas, plot twists, dialogue, thematic notes, save-for-later.
- **Status workflow**: raw_idea → maybe_later → planned → used → archived
- **Linking**: Assign to project, book, chapter, character, location, timeline event.
- **Pinned & starred**: Surface important ideas quickly.

## Idea Types

| Type | Description |
|------|-------------|
| `quick_note` | Fast capture |
| `idea_card` | Structured idea |
| `scene_idea` | Scene concept |
| `chapter_idea` | Chapter concept |
| `title_idea` | Title option |
| `plot_twist` | Plot twist idea |
| `dialogue_snippet` | Dialogue line |
| `thematic_note` | Theme-related note |
| `save_for_later` | Deferred idea |

## Statuses

| Status | Description |
|--------|-------------|
| `raw_idea` | Just captured |
| `maybe_later` | Might use later |
| `planned` | Planned for use |
| `used` | Already used |
| `archived` | No longer relevant |

## API Endpoints

- `GET /api/v1/projects/{project_id}/vault/ideas` — List (filter by `idea_type`, `status`, `book_id`, `chapter_id`, `pinned`, `starred`, `q`)
- `POST /api/v1/projects/{project_id}/vault/ideas` — Create
- `GET /api/v1/projects/{project_id}/vault/ideas/{idea_id}` — Get
- `PATCH /api/v1/projects/{project_id}/vault/ideas/{idea_id}` — Update
- `DELETE /api/v1/projects/{project_id}/vault/ideas/{idea_id}` — Delete

## Convert to Chapter/Scene/Note

Ideas can be converted into chapters, scenes, or notes via the UI or workflow logic. The `status` field tracks when an idea is `used`.

## Search

- `GET /api/v1/projects/{project_id}/vault/search?q=...&entity_types=idea&status=raw_idea` — Find unused ideas
