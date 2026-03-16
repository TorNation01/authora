# Client Review Mode (Ghostwriter)

Client Review Mode supports ghostwriting and commissioned book workflows where a client reviews and approves material without seeing internal drafting clutter.

## Goals

- **Simplified interface** – Client sees approved review material only
- **Chapter approval** – Approve or request changes per chapter
- **Milestone approvals** – Stage-based delivery (draft sent, under review, approved, locked)
- **Client notes** – Clear feedback for author
- **Clear delivery stages** – Draft sent → Under review → Changes requested → Approved → Locked for delivery

## Implementation Status

- **Roles** – `client` role grants view_manuscript, comment, view_notes, approve_chapters, view_activity
- **Chapter approval** – `ChapterApproval` with statuses: pending, approved, rejected, changes_requested
- **Activity audit** – Collaboration activity tracks approvals and changes

## Client Statuses

| Status | Description |
|--------|-------------|
| draft_sent | Sent to client for review |
| under_review | Client is reviewing |
| changes_requested | Client requested changes |
| approved | Client approved |
| locked | Locked for delivery |

## Architecture Notes

- Clients are project members with role `client`
- Share scope can restrict to `review_copy` or `chapters` for partial sharing
- `ChapterApproval` tracks per-chapter status; approved_by and approved_at record signoff
- Ghostwriter workspace already supports ghostwriter-specific flows; client mode integrates with this
