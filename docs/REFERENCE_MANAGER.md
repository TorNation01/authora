# Reference Manager

AUTHORA integrates a reference manager for sources, citations, and bibliographies.

## Overview

- **Vault Sources** — Central source library (manual or Zotero-synced)
- **Project-linked** — Sources belong to projects; link to chapters
- **Reference manager UI** — Filter, search, tag, notes

## Features

### Source Library

- **Source types**: book, article, website, interview, document, video, podcast, other
- **Status**: verified, unverified, needs_review
- **Used in manuscript**: Mark sources cited in the project

### Filtering & Search

- Filter by source type
- Filter by tags (`topic_tags`)
- Search by title, author
- Filter by status (verified, needs_review)

### Source Notes

- Add annotations to sources
- Note types: annotation, summary, quote
- Page references for print sources
- Supports annotated bibliography workflows

### Project Linking

- Sources are project-scoped
- `ChapterSourceLink` — mark source as used in chapter
- `ChapterCitation` — in-editor citation markers linked to sources

## API

Sources are managed via the existing Vault API:

- `GET/POST /api/v1/projects/{id}/vault/sources`
- `PATCH/DELETE /api/v1/projects/{id}/vault/sources/{source_id}`

Reference-specific:

- `POST /api/v1/projects/{id}/references/source-notes` — Add note to source
- `POST /api/v1/projects/{id}/references/citations` — Add chapter citation

## Manual Entry

When Zotero is not connected, users add sources manually:

1. Vault → Sources → Add source
2. Enter title, author, type, publication date, URL
3. Optional: citation notes, quote extracts
4. Source is used for citations and bibliography
