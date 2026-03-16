# Timeline and Event Tracker

The AUTHORA Timeline system stores event cards for story chronology, backstory, memoir life-stages, and historical reference.

## Overview

- **Project-scoped**: Events belong to a project (optionally a book).
- **Dated or undated**: Use `event_date` or `date_label` for ambiguous dates.
- **Sequence ordering**: `sequence_order` for drag-and-drop ordering.
- **Filtering**: By storyline, time period, event type.
- **Chapter linking**: Link events to chapters.

## Event Types

| Type | Description |
|------|-------------|
| `story_event` | Story event |
| `chapter_event` | Chapter event |
| `backstory` | Backstory |
| `life_event` | Life event |
| `memoir_stage` | Memoir life-stage |
| `historical_reference` | Historical reference |

## Fields

| Field | Description |
|-------|-------------|
| `title` | Event title |
| `description` | Description |
| `event_type` | Type |
| `event_date` | Date (if known) |
| `date_label` | "Summer 1942", "Before the war" |
| `sequence_order` | Order for undated events |
| `storyline` | Storyline filter |
| `time_period` | Time period filter |

## API Endpoints

- `GET /api/v1/projects/{project_id}/vault/timeline` — List (filter by `book_id`, `event_type`, `storyline`)
- `POST /api/v1/projects/{project_id}/vault/timeline` — Create
- `GET /api/v1/projects/{project_id}/vault/timeline/{event_id}` — Get
- `PATCH /api/v1/projects/{project_id}/vault/timeline/{event_id}` — Update (including `sequence_order` for drag reorder)
- `DELETE /api/v1/projects/{project_id}/vault/timeline/{event_id}` — Delete

## Chapter Linking

- `POST /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/events`

## Chapter Knowledge Panel

- `GET /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/knowledge`
