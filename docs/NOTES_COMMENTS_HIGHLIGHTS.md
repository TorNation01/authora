# Notes, Comments, and Highlights

AUTHORA supports project notes, inline comments, and content highlights for research, revision, and collaboration.

## Notes

- **Project notes**: Attached to project, optionally linked to book/chapter
- **Note types**: General, research, character, plot, etc.
- **Pinned notes**: Quick access from Notes panel
- **Attachments**: File attachments supported
- **To-draft**: Insert note content into chapter

**API**: `/api/v1/projects/{id}/notes` (CRUD, search, link, pin, attachments)

## Content Comments

- **Inline comments**: Attached to chapter content by character offset
- **Threading**: Replies supported via `parent_id`
- **Resolved state**: Mark comments resolved when addressed
- **Revision queue**: Filter by unresolved in Revision panel

**API**: `/api/v1/projects/{id}/books/{id}/chapters/{id}/comments`

- `GET` — List (optional `unresolved_only`)
- `POST` — Create (start_offset, end_offset, body, parent_id)
- `PATCH` — Update (body, resolved)
- `DELETE` — Delete

## Content Highlights

- **Highlight ranges**: start_offset, end_offset in chapter plain text
- **Colors**: Optional color for highlight type
- **Use cases**: Mark for rewrite, continuity check, research note

**API**: `/api/v1/projects/{id}/books/{id}/chapters/{id}/highlights`

- `GET` — List
- `POST` — Create (start_offset, end_offset, color)
- `DELETE` — Delete

## Offset Handling

Comments and highlights use **character offsets** in the plain-text representation of the chapter. TipTap/ProseMirror uses document positions; conversion between the two is required for editor integration. Editor integration for creating/viewing comments and highlights from the editor is planned.
