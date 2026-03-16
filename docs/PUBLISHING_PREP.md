# Publishing Prep

Publishing prep tools generate content for submission, marketing, and handoff.

## Prep Types

| Type | Output | Description |
|------|--------|-------------|
| `synopsis` | Text | Book synopsis |
| `blurb` | Text | Back cover blurb |
| `chapter_summaries` | List | Chapter summaries |
| `beta_pack` | Object | Beta reader package (synopsis, feedback questions, summaries) |
| `author_bio` | Text | Author bio draft |
| `handoff_pack` | Object | Ghostwriter handoff (synopsis, blurb, summaries, bio, handoff notes) |

## API

`GET /api/v1/export/books/{book_id}/publishing-prep/{prep_type}`

Query: `extra_context` – Optional additional context for AI generation.

## Publishing Packages

| Package | Endpoint | Contents |
|---------|----------|----------|
| Beta Reader | `GET /books/{book_id}/packages/beta-reader` | ZIP: manuscript, synopsis, feedback form, chapter summaries |
| Ghostwriter Handoff | `GET /books/{book_id}/packages/ghostwriter-handoff` | ZIP: manuscript, synopsis, blurb, summaries, bio, handoff notes |
| Chapter Summary Sheet | `GET /books/{book_id}/packages/chapter-summary-sheet` | DOCX |

## Standalone Exports

- `GET /books/{book_id}/packages/blurb` – Back cover blurb as TXT
- `GET /books/{book_id}/packages/synopsis` – Synopsis as DOCX

## AI Requirements

Publishing prep requires OpenAI or Anthropic API key. Returns 503 if not configured.
