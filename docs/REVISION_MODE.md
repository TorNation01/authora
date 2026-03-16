# Revision Mode

Revision Mode helps authors work through revision passes by surfacing comments, highlights, and pending notes.

## Overview

- **Revision panel**: Lists chapters with unresolved comments
- **Filter**: Unresolved only or all comments
- **Navigation**: Click a chapter to jump to it and address notes
- **Status**: Chapter status (Draft, Revising, Review, Done) visible in sidebar

## Revision Workflow

1. **Add comments** as you read through your draft (via comments API; editor integration in progress)
2. **Open Revision panel** from the toolbar
3. **Filter** by unresolved only to focus on work remaining
4. **Click a chapter** to open it and address the notes
5. **Resolve comments** when addressed (via API)

## Chapter Status

- **Draft**: Initial writing
- **Revising**: Active revision pass
- **Review**: Ready for review
- **Done**: Complete

Status is set per chapter via the toolbar dropdown or (future) sidebar context menu.

## Revision Pass Types

Comments can be used to tag revision focus:

- Structural revision
- Clarity revision
- Pacing revision
- Emotional depth revision
- Grammar/polish revision
- Consistency revision

(Comment categories/tags are planned for a future release.)

## API

- `GET /projects/{id}/books/{id}/chapters/{id}/comments` — List comments (optional `unresolved_only=true`)
- `POST /projects/{id}/books/{id}/chapters/{id}/comments` — Create comment
- `PATCH /projects/{id}/books/{id}/chapters/{id}/comments/{id}` — Update (body, resolved)
- `DELETE /projects/{id}/books/{id}/chapters/{id}/comments/{id}` — Delete comment
