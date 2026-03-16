# Approval Workflows

## Chapter Approval

Each chapter can have a single `ChapterApproval` record with status:

| Status | Description |
|--------|-------------|
| `pending` | Awaiting review |
| `approved` | Approved by reviewer |
| `rejected` | Rejected |
| `changes_requested` | Changes requested by reviewer |

## API

- `GET /projects/{id}/books/{book_id}/chapters/{chapter_id}/approval` – Get approval (view_manuscript or approve_chapters)
- `POST /projects/{id}/books/{book_id}/chapters/{chapter_id}/approval` – Create approval (approve_chapters)
- `PATCH /projects/{id}/books/{book_id}/chapters/{chapter_id}/approval` – Update status (approve_chapters)

## Update Payload

```json
{
  "status": "approved",
  "notes": "Optional notes from reviewer"
}
```

When status is `approved`, `rejected`, or `changes_requested`, `approved_by` and `approved_at` are set automatically.

## Activity

- `approval_created` – When approval record is created
- `approval_updated` – When status changes

## Future Enhancements

- **Section approval** – Per-section approval
- **Manuscript stage approval** – Draft/revised/final approval
- **Revision pass completion** – Approval when pass is complete
- **Configurable statuses** – Not started, in review, ready for export, etc.
