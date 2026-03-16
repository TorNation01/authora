# Themes / Motifs / Symbols Tracker

The AUTHORA Theme Tracker stores themes, motifs, symbols, emotional threads, and recurring ideas with chapter linking.

## Overview

- **Project-scoped**: Themes belong to a project (optionally a book).
- **Types**: theme, motif, symbol, emotional_thread, recurring_idea
- **Central flag**: Mark themes as central to the story
- **Chapter linking**: Track where themes appear

## Theme Types

| Type | Description |
|------|-------------|
| `theme` | Central theme |
| `motif` | Recurring motif |
| `symbol` | Symbol |
| `emotional_thread` | Emotional thread |
| `recurring_idea` | Recurring idea |

## API Endpoints

- `GET /api/v1/projects/{project_id}/vault/themes` — List (filter by `book_id`, `theme_type`, `is_central`)
- `POST /api/v1/projects/{project_id}/vault/themes` — Create
- `GET /api/v1/projects/{project_id}/vault/themes/{theme_id}` — Get
- `PATCH /api/v1/projects/{project_id}/vault/themes/{theme_id}` — Update
- `DELETE /api/v1/projects/{project_id}/vault/themes/{theme_id}` — Delete

## Chapter Linking

- `POST /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/themes`

## Tracking

- **Central themes**: Use `is_central` to mark primary themes
- **Where they show up**: Chapter links show which chapters use each theme
- **Underused**: Compare linked chapters vs total chapters
- **Symbol recurrence**: Use `theme_type=symbol` and chapter links to track
