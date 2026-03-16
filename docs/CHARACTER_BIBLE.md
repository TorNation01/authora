# Character Bible

The AUTHORA Character Bible stores structured character profiles for fiction and memoir-style people mapping.

## Overview

- **Project-scoped**: Characters belong to a project (optionally a book).
- **Comprehensive fields**: Name, aliases, role, archetype, age, appearance, voice, personality, goals, fears, motivations, conflicts, backstory, secrets, quirks, dialogue patterns, emotional arc.
- **Chapter linking**: Link characters to chapters for appearance history and knowledge panel.
- **Relationship mapping**: Track character-to-character relationships.

## Fields

| Field | Description |
|-------|-------------|
| `full_name` | Primary name |
| `aliases` | Alternative names |
| `role_in_story` | Protagonist, antagonist, etc. |
| `archetype` | Character archetype |
| `age` | Age or stage |
| `appearance_notes` | Physical description |
| `voice_notes` | Voice/speech patterns |
| `personality_traits` | Personality |
| `goals` | Goals |
| `fears` | Fears |
| `motivations` | Motivations |
| `internal_conflict` | Internal conflict |
| `external_conflict` | External conflict |
| `backstory` | Backstory |
| `timeline_notes` | Timeline notes |
| `secrets` | Secrets |
| `quirks` | Quirks |
| `dialogue_patterns` | Dialogue patterns |
| `emotional_arc` | Emotional arc |
| `private_notes` | Author-only notes |
| `status` | active / background / archived |

## API Endpoints

- `GET /api/v1/projects/{project_id}/vault/characters` — List (filter by `book_id`, `status`)
- `POST /api/v1/projects/{project_id}/vault/characters` — Create
- `GET /api/v1/projects/{project_id}/vault/characters/{character_id}` — Get
- `PATCH /api/v1/projects/{project_id}/vault/characters/{character_id}` — Update
- `DELETE /api/v1/projects/{project_id}/vault/characters/{character_id}` — Delete

## Chapter Linking

- `POST /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/characters`

## Chapter Knowledge Panel

Linked characters appear in the chapter knowledge panel:

- `GET /api/v1/projects/{project_id}/vault/books/{book_id}/chapters/{chapter_id}/knowledge`

## Relationships

Use `VaultRelationship` to link characters:

- `GET /api/v1/projects/{project_id}/vault/relationships?character_id=...`
- `POST /api/v1/projects/{project_id}/vault/relationships`

## Non-Fiction / Memoir

For memoir, people mapping, or stakeholders: use the same fields as `people` or `source/interviewee` entries.
