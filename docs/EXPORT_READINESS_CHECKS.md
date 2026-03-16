# Export Readiness Checks

The export readiness checker validates content before export and returns warnings, errors, and suggested fixes.

## Checks Performed

| Check | Type | Description |
|-------|------|-------------|
| Missing title | Warning | Book title is empty |
| Missing author | Warning | Author name empty (when required) |
| Empty chapters | Warning | Chapters with no content |
| Placeholder text | Warning | Possible placeholder (lorem ipsum, [TBD], etc.) |
| Duplicate headings | Warning | Duplicate chapter titles |
| Unresolved comments | Warning | Comments not resolved (optional) |
| No chapters | Error | No chapters to export (blocks export) |

## Placeholder Patterns

- lorem ipsum
- [placeholder]
- [todo]
- [tbd]
- [insert
- xxx
- placeholder text
- add content here
- write here

## API

`GET /api/v1/export/books/{book_id}/validate`

Query params:

- `author_name` – Author name for validation
- `require_author` – Treat missing author as warning
- `check_placeholders` – Check for placeholder text
- `check_unresolved_comments` – Check for unresolved comments

## Response

```json
{
  "valid": true,
  "warnings": ["Empty or placeholder chapters: Chapter 3"],
  "errors": [],
  "fixes": [
    {"issue": "empty_chapters", "suggestion": "Add content or exclude these chapters"}
  ]
}
```

- `valid` – false if any errors block export
- `warnings` – Do not block export
- `errors` – Block export
- `fixes` – Suggested actions for issues

## User Override

Users can proceed with export despite warnings. Only errors block export. The UI should surface warnings clearly and allow override.
