# Editor Review Mode

Editor Review Mode supports professional editorial workflows with heavy comment usage, revision passes, and chapter review status.

## Goals

- **Clear manuscript display** – Manuscript shown clearly for review
- **Heavy comment usage** – Inline comments, chapter comments, section comments
- **Revision pass support** – Pass-by-pass reviewing (structural, line edit, copy edit)
- **Unresolved issue queues** – Track and resolve comments
- **Chapter review status** – Per-chapter completion status
- **Editor summaries** – Project-level editorial feedback

## Implementation Status

- **Roles** – `editor` role grants view_manuscript, edit_manuscript, comment, view_notes, edit_notes, view_activity
- **Revision passes** – Existing revision pass system supports pass-by-pass review
- **Content comments** – `ContentComment` with `comment_type` (e.g. `rewrite_suggestion`, `clarity_issue`, `pacing_note`, `grammar_spelling`, `consistency`)
- **Chapter approval** – `ChapterApproval` for chapter-level approval status

## Editor Workflows

- **Structural review** – Pass with structural comments
- **Line edit review** – Pass with line-level suggestions
- **Copy-edit notes** – Grammar and consistency
- **Consistency review** – Character voice, plot continuity
- **Manuscript-level summary** – Project-level feedback via notes or comments

## Architecture Notes

- Editors use revision passes to organize feedback by type
- `comment_type` on ContentComment supports tagging (rewrite_suggestion, clarity_issue, pacing_note, etc.)
- `collaboration_role` can store reviewer role for display
