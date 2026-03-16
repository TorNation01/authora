# Chapter-Linked Knowledge

The AUTHORA Chapter-Linked Knowledge system surfaces relevant vault material (characters, locations, events, themes, sources, research) while writing a chapter.

## Overview

- **Knowledge panel**: Aggregated view of all linked material for a chapter.
- **Attach actions**: Link characters, locations, events, themes, sources, research to a chapter.
- **View related**: Retrieve linked material without leaving the editor context.

## API Endpoints

### Get Chapter Knowledge Panel

```
GET /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/knowledge
```

Returns a `ChapterKnowledgePanel` with:

- `characters` — Linked characters
- `locations` — Linked locations
- `events` — Linked timeline events
- `themes` — Linked themes
- `sources` — Linked sources
- `research_entries` — Linked research entries

### Attach to Chapter

| Entity | Endpoint |
|--------|----------|
| Character | `POST .../chapters/{chapter_id}/characters` |
| Location | `POST .../chapters/{chapter_id}/locations` |
| Event | `POST .../chapters/{chapter_id}/events` |
| Theme | `POST .../chapters/{chapter_id}/themes` |
| Source | `POST .../chapters/{chapter_id}/sources` |
| Research | `POST .../chapters/{chapter_id}/research` |

Request bodies include the entity ID and optional notes.

## Usage

1. **Side-by-side editor**: Show the knowledge panel while editing the chapter.
2. **Quick attach**: From the vault, use "Attach to chapter" to link.
3. **Context retrieval**: Surface relevant info (character details, setting details) without leaving the editor.

## Unlink

To remove a link, delete the corresponding `Chapter*Link` record. (Delete endpoints for links can be added.)
