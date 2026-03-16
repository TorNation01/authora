# AUTHORA Review Signal System

The review signal system adds structured review workflows to comments and feedback. It supports statuses, tags, and filtering so authors and collaborators can track and act on feedback.

## Comment Statuses

| Status | Description |
|--------|-------------|
| **Open** | New or unresolved feedback |
| **In review** | Being reviewed by the author |
| **Resolved** | Addressed or accepted |
| **Deferred** | Postponed for later |
| **Needs decision** | Requires author decision |

## Workflow

1. **Open** – Comment is created or left unresolved.
2. **In review** – Author or editor is working through it.
3. **Resolved** – Feedback has been addressed or accepted.
4. **Deferred** – Feedback is noted but not acted on yet.
5. **Needs decision** – Author needs to decide how to proceed.

When status is set to **Resolved**, `resolved_at` is set automatically. When status changes from **Resolved** to another status, `resolved_at` is cleared.

## Filtering

Comments can be filtered by:

| Filter | Query param | Description |
|--------|-------------|-------------|
| **Tag** | `comment_type` or `tag` | Comment tag (e.g. clarity, rewrite, pacing) |
| **User** | `user_id` | User who wrote the comment |
| **Role** | `role` | Collaboration role at comment time |
| **Chapter** | Path (chapter_id) | Chapter (implicit in path) |
| **Status** | `status` | open, in_review, resolved, deferred, needs_decision |
| **Unresolved** | `unresolved_only` | Only comments without resolved_at |
| **Revision pass** | `revision_pass_id` | Revision pass |

### Example

```
GET /api/v1/projects/{id}/books/{book_id}/chapters/{chapter_id}/comments?status=open&comment_type=clarity&user_id={user_id}
```

## API

### List comments

```
GET /projects/{id}/books/{book_id}/chapters/{chapter_id}/comments
```

Query params:

- `unresolved_only` (bool)
- `revision_pass_id` (UUID)
- `user_id` (UUID)
- `comment_type` or `tag` (string)
- `status` (string)
- `role` (string)

### Update comment

```
PATCH /projects/{id}/books/{book_id}/chapters/{chapter_id}/comments/{comment_id}
```

Body:

- `body` (string) – Author only
- `comment_type` (string) – Author only
- `status` (string)
- `resolved` (bool)

**Status** and **resolved** can be updated by any collaborator with project access. **Body** and **comment_type** can only be updated by the comment author.

## Section Filtering

Section-level filtering (e.g. by offset range or content block) can be added in a future enhancement. The current model supports `start_offset` and `end_offset` for inline comments.

## See Also

- [COMMENT_TAGS.md](COMMENT_TAGS.md) – Tag reference
- [EDITOR_REVIEW_MODE.md](EDITOR_REVIEW_MODE.md) – Editor workflows
- [COLLABORATION_SYSTEM.md](COLLABORATION_SYSTEM.md) – Collaboration overview
