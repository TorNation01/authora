# Educator Reviewer Workflows

## Overview

The integrity review system supports educator and reviewer workflows for essay/research paper checks, lecture/course submissions, and source-by-source inspection.

## Supported Workflows

- **Essay / research paper checks** – Run originality scan, review matched passages
- **Lecture / course submissions** – Support for course-level corpora

## Review Queue

- List integrity review reports per book
- Filter by status
- Sort by `created_at` / `updated_at`

## Report Status

- `draft` – Initial state
- `updated` – Modified after creation
- `reviewed` – Reviewer has completed review (can be extended)

## Review Actions

1. **Create report** – Link to originality scan
2. **Set needs_human_review** – Flag for human review
3. **Add reviewer notes** – Notes on the report
4. **Add comments** – Per matched passage or general

## Comment Types

- `general` – General comment on report
- `source` – Comment on specific source
- `note` – Reviewer note

## Source-by-Source Inspection

- **Matched passage viewer** – Side-by-side query vs. matched text
- **Source label** – Identifies source (e.g., chapter title, project name)
- **Comments** – Attach comments to specific matched passages

## API Endpoints

- `GET /api/v1/projects/{project_id}/books/{book_id}/originality/reports` – List reports
- `POST /api/v1/projects/{project_id}/books/{book_id}/originality/reports` – Create report
- `PATCH /api/v1/projects/{project_id}/books/{book_id}/originality/reports/{report_id}` – Update report
- `POST /api/v1/projects/{project_id}/books/{book_id}/originality/reports/{report_id}/comments` – Add comment

## Export

- Report export is configurable via admin
- Export includes: originality summary, matched passages, AI-assistance trace, AI-origin risk, reviewer notes

## Admin Controls

- **originality_enabled** – Enable/disable originality features
- **ai_review_enabled** – Enable/disable AI-origin risk review
- **report_export_enabled** – Enable/disable report export
