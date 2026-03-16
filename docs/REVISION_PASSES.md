# Revision Pass System

AUTHORA supports structured revision passes for systematic manuscript revision. Each pass focuses on a specific aspect of the draft and can be activated at project or book level.

## Pass Types

| Type | Label | Use |
|------|-------|-----|
| `structural` | Structural pass | Plot, scene structure, pacing of acts |
| `clarity` | Clarity pass | Sentence clarity, POV, transitions |
| `pacing` | Pacing pass | Speed, rhythm, tension |
| `emotional_depth` | Emotional depth pass | Character reactions, reader connection |
| `consistency` | Consistency pass | Character details, timeline, world logic |
| `grammar_polish` | Grammar and polish pass | Spelling, grammar, sentence variety |
| `custom` | Custom pass | User-defined focus |

## Activation

- **Project level**: Create a revision pass for the project. It applies to all chapters in all books in the project. Use `book_id: null` when creating.
- **Chapter level (book level)**: Create a revision pass for a specific book. It applies only to chapters in that book. Use `book_id: <uuid>` when creating.

## Workflow

1. **Create a pass** for the project or book.
2. **Checklist items** are generated automatically from the pass type (or added manually for custom passes).
3. **Work through chapters** one at a time.
4. **Add comments** linked to the pass when you find issues.
5. **Mark chapters complete** when done for that pass.
6. **Mark the pass complete** when all chapters are done.

## Sequential Workflow

Passes have a `sort_order`. Work through them in order for a structured revision process:

1. Structural pass
2. Clarity pass
3. Pacing pass
4. Emotional depth pass
5. Consistency pass
6. Grammar and polish pass

Custom passes can be inserted anywhere.

## API

- `GET /projects/{id}/revision-passes` — List passes (optional `book_id` filter)
- `POST /projects/{id}/revision-passes` — Create pass (body: `pass_type`, `book_id?`, `name?` for custom)
- `GET /projects/{id}/revision-passes/{pass_id}` — Get pass with stats
- `PATCH /projects/{id}/revision-passes/{pass_id}` — Update (name, sort_order, completed)
- `DELETE /projects/{id}/revision-passes/{pass_id}` — Delete pass
- `POST /projects/{id}/revision-passes/{pass_id}/chapters/{chapter_id}/complete` — Mark chapter complete
- `POST /projects/{id}/revision-passes/{pass_id}/chapters/{chapter_id}/incomplete` — Mark chapter incomplete
- `POST /projects/{id}/revision-passes/{pass_id}/checklist-items` — Add checklist item
- `DELETE /projects/{id}/revision-passes/{pass_id}/checklist-items/{item_id}` — Remove checklist item

## Comments and Notes

When creating a comment, pass `revision_pass_id` to link it to a revision pass. The Revision panel can filter by pass type to show only unresolved issues for the active pass.

## Summary

Each pass response includes:

- `chapters_total` — total chapters in scope
- `chapters_completed` — chapters marked complete
- `unresolved_comments` — comments linked to this pass that are not resolved
- `checklist_items` — checklist for this pass
