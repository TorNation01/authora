# Collaboration Audit Log

## Activity Model

`CollaborationActivity` records timestamped collaboration events:

- `project_id` – Project
- `user_id` – User who performed the action (nullable for system events)
- `action` – Action type (e.g. `invite_created`, `invite_accepted`, `member_removed`, `approval_created`, `approval_updated`)
- `entity_type` – Entity type (e.g. `invite`, `member`, `chapter_approval`)
- `entity_id` – Entity ID (string)
- `extra_data` – JSONB metadata (e.g. `{"email": "...", "role": "..."}`)
- `created_at` – Timestamp

## Action Types

| Action | Entity Type | Description |
|--------|-------------|-------------|
| invite_created | invite | Invite created |
| invite_accepted | invite | Invite accepted |
| member_removed | member | Member removed |
| approval_created | chapter_approval | Chapter approval created |
| approval_updated | chapter_approval | Chapter approval status updated |

## API

- `GET /projects/{id}/activity` – List activity feed (view_activity permission)
- Query params: `limit` (default 50, max 200), `offset` (default 0)

## Use Cases

- **Accountability** – Who invited, who approved, who removed
- **Clarity** – Audit trail for client and editor workflows
- **Security** – Detect unauthorized access changes

## Future Enhancements

- **Export tracking** – Who exported
- **Comment resolution** – Who resolved comments
- **Edit tracking** – Who edited (chapter-level)
