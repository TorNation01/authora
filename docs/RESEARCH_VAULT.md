# Research Vault

The AUTHORA Research Vault stores and organizes support material for writing projects: research notes, clipped snippets, summaries, topic folders, and source-linked entries.

## Overview

- **Project-scoped**: All research lives under a project.
- **Flexible entry types**: Notes, clipped snippets, summaries, documents, topic folders, fact-check entries.
- **Source linking**: Link research entries to sources for citation and verification.
- **Chapter linking**: Attach research to chapters for context while writing.
- **Verification workflow**: Mark entries as needing verification.

## Entry Types

| Type | Description |
|------|-------------|
| `note` | General research note |
| `clipped_snippet` | Clipped text from external sources |
| `summary` | Summary of longer material |
| `document` | Document-style research entry |
| `topic_folder` | Container for organizing by topic |
| `fact_check` | Fact-check note with verification status |

## API Endpoints

- `GET /api/v1/projects/{project_id}/vault/research` — List research entries (filter by `entry_type`, `topic`, `needs_verification`, `parent_id`)
- `POST /api/v1/projects/{project_id}/vault/research` — Create entry
- `GET /api/v1/projects/{project_id}/vault/research/{entry_id}` — Get entry
- `PATCH /api/v1/projects/{project_id}/vault/research/{entry_id}` — Update entry
- `DELETE /api/v1/projects/{project_id}/vault/research/{entry_id}` — Delete entry

## Chapter Linking

Link research to chapters for the knowledge panel:

- `POST /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/research`

## Use Cases

- **Fiction research**: Historical accuracy, setting details, technical facts
- **Non-fiction**: Subject research, methodology notes, case studies
- **Memoir**: Memory gathering, timeline verification
- **Workbook**: Methodology notes, exercise references
- **Ghostwriting**: Client material summaries, interview notes

## Search

Use vault search for retrieval:

- `GET /api/v1/projects/{project_id}/vault/search?q=...&entity_types=research`
