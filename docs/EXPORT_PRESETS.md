# Export Presets

Export presets define format, compile options, styling, and naming for common export scenarios.

## System Presets

| Key | Name | Format | Purpose |
|-----|------|--------|---------|
| `clean_manuscript` | Clean Manuscript | DOCX | Submission or editing |
| `editor_review_copy` | Editor Review Copy | DOCX | With comments and revision marks |
| `beta_reader_copy` | Beta Reader Copy | ZIP | Manuscript + synopsis + feedback form |
| `submission_copy` | Submission Copy | DOCX | Agent/publisher submission |
| `print_friendly_draft` | Print-Friendly Draft | PDF | Physical review |
| `working_draft` | Working Draft | DOCX | Internal use with notes |
| `ghostwriter_delivery_pack` | Ghostwriter Delivery Pack | ZIP | Manuscript + synopsis + summaries + bio + handoff |
| `workbook_export` | Workbook Export | PDF | Printable prompts and exercises |
| `memoir_review_draft` | Memoir Review Draft | DOCX | Chaptered review copy |
| `sample_chapters_export` | Sample Chapters Export | DOCX | First 3 chapters for proposal |
| `amazon_kdp_paperback` | Amazon KDP Paperback | PDF | Print-ready for KDP paperback interior |
| `amazon_kdp_ebook` | Amazon KDP Ebook | EPUB | EPUB for Kindle Direct Publishing |

## Custom Profiles

Users can create, edit, duplicate, and delete custom profiles. Custom profiles are stored per user and can be based on system presets or built from scratch.

## Profile Fields

- `name` – Display name
- `description` – Optional description
- `format` – docx, pdf, epub, txt, md, html, json, zip
- `compile_type` – full, chapter_only, partial, review_copy, submission_copy, working_draft
- `format_style` – manuscript, print, ebook
- `options` – JSON object with include_title_page, include_toc, exclude_notes_comments, etc.
- `front_matter_blocks` – Ordered front matter
- `back_matter_blocks` – Ordered back matter
- `naming_pattern` – File naming with placeholders
- `project_type` – fiction, nonfiction, memoir, workbook, journal, ghostwritten

## API

- `GET /api/v1/export/profiles` – List system presets and custom profiles
- `POST /api/v1/export/profiles` – Create custom profile
- `GET /api/v1/export/profiles/{id}` – Get by UUID or system key
- `PUT /api/v1/export/profiles/{id}` – Update custom profile
- `DELETE /api/v1/export/profiles/{id}` – Delete custom profile
- `POST /api/v1/export/profiles/{id}/duplicate` – Duplicate as new custom profile

## Project-Type Handling

Presets can target project types:

- **Fiction** – Clean manuscript, beta copy, submission sample
- **Non-fiction** – Chapter headings, workbook prompts, references
- **Memoir** – Chaptered review copy, reflection-friendly
- **Workbook** – Printable sections, prompts, spacing-aware
- **Journal** – Prompt layout, entry spacing
- **Ghostwritten** – Client review package, delivery package
