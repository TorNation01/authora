# Source / Reference Manager

The AUTHORA Source Manager stores sources for non-fiction, memoir, research-heavy fiction, and ghostwriting.

## Overview

- **Project-scoped**: Sources belong to a project.
- **Rich metadata**: Title, author, type, publication date, URL, usage notes, topic tags, quote extracts, citation notes.
- **Verification workflow**: verified / unverified / needs_review
- **Chapter linking**: Mark sources as used in chapters.

## Source Types

| Type | Description |
|------|-------------|
| `book` | Book |
| `article` | Article |
| `website` | Website |
| `interview` | Interview |
| `document` | Document |
| `video` | Video |
| `podcast` | Podcast |
| `other` | Other |

## Statuses

| Status | Description |
|--------|-------------|
| `verified` | Verified |
| `unverified` | Unverified |
| `needs_review` | Needs review |

## Fields

| Field | Description |
|-------|-------------|
| `title` | Title |
| `author` | Author/source name |
| `source_type` | Type |
| `publication_date` | Publication date |
| `url` | URL |
| `usage_notes` | Usage notes |
| `topic_tags` | Topic tags |
| `quote_extracts` | Extracted quotes |
| `citation_notes` | Citation notes |
| `reliability_note` | Reliability/confidence |
| `status` | Verification status |

## API Endpoints

- `GET /api/v1/projects/{project_id}/vault/sources` — List (filter by `source_type`, `status`)
- `POST /api/v1/projects/{project_id}/vault/sources` — Create
- `GET /api/v1/projects/{project_id}/vault/sources/{source_id}` — Get
- `PATCH /api/v1/projects/{project_id}/vault/sources/{source_id}` — Update
- `DELETE /api/v1/projects/{project_id}/vault/sources/{source_id}` — Delete

## Chapter Linking (Used-in-Chapter)

- `POST /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/sources`

## Research Entry Linking

Research entries can link to a source via `source_id` in the research entry.

## Bibliography

The architecture supports bibliography-ready export later (citation format, used-in-chapter markers).
