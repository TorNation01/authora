# AUTHORA Export System

The export system turns manuscript projects into clean, professional outputs for drafting, editing, sharing, submission, publishing prep, printing, ghostwriting delivery, and archival.

## Overview

- **Manuscript compile engine** – Assembles content with full control over inclusion, order, and exclusions
- **Export formats** – DOCX, PDF, EPUB, TXT, Markdown, HTML, JSON
- **Export profiles** – Presets for common scenarios (Clean Manuscript, Beta Reader, Submission, etc.)
- **Front/back matter** – Structured blocks with optional inclusion and ordering
- **Compile preview** – Preview structure, word count, page estimate before export
- **Export readiness checks** – Validation with warnings and suggested fixes

## Supported Formats

| Format | Extension | Purpose |
|--------|-----------|---------|
| DOCX | .docx | Editable, print-ready, industry standard |
| PDF | .pdf | Print-ready, fixed layout |
| EPUB | .epub | E-readers, ebook distribution |
| TXT | .txt | Plain text, universal compatibility |
| Markdown | .md | Version control, conversion pipelines |
| HTML | .html | Web preview, standalone page |
| JSON | .json | Archive, import, programmatic use |

## API Endpoints

- `GET /api/v1/export/books/{book_id}/preview` – Export preview (word count, chapters)
- `GET /api/v1/export/books/{book_id}/validate` – Readiness validation
- `POST /api/v1/export/books/{book_id}/compile-preview` – Compile structure preview
- `GET /api/v1/export/books/{book_id}/{format}` – Export to format (docx, pdf, epub, txt, md, html, json)
- `GET /api/v1/export/profiles` – List system presets and custom profiles
- `POST /api/v1/export/profiles` – Create custom profile
- `GET /api/v1/export/profiles/{id}` – Get profile by ID or system key
- `PUT /api/v1/export/profiles/{id}` – Update custom profile
- `DELETE /api/v1/export/profiles/{id}` – Delete custom profile
- `POST /api/v1/export/profiles/{id}/duplicate` – Duplicate profile

## File Naming

Configurable via `naming_pattern` in export profiles. Placeholders:

- `{project_title}` – Book/project title
- `{profile}` – Export profile name
- `{date}` – YYYY-MM-DD
- `{version}` – Draft version
- `{author}` – Author name

Example: `{project_title}_{profile}_{date}` → `MyNovel_CleanManuscript_2026-03-16.docx`

## Handoff and Publishing Prep

See the handoff and publishing-prep guides:

- [HANDOFF_CHECKLISTS.md](HANDOFF_CHECKLISTS.md) – Overview of all checklists (editor, beta reader, submission, ghostwriter, self-publishing, print-draft)
- [BETA_READER_PREP.md](BETA_READER_PREP.md) – Beta reader copy preparation
- [EDITOR_HANDOFF.md](EDITOR_HANDOFF.md) – Editor handoff checklist
- [GHOSTWRITER_DELIVERY.md](GHOSTWRITER_DELIVERY.md) – Ghostwriter delivery checklist
- [SUBMISSION_PREP.md](SUBMISSION_PREP.md) – Submission sample preparation

## Deployment

Supports standalone and server-hosted deployment. Export limits and billing are configurable via `feature_billing` and plan entitlements.
