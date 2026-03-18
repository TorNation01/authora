# AI-Assistance Transparency

## Purpose

Track and disclose where AI was used in content creation, supporting academic and institutional policy workflows and user transparency.

## Data Sources

1. **Chapter.content_source** – `user_written`, `ai_assisted`, `ai_generated`
2. **AIActionLog** – Records of AI actions (generate, rewrite, etc.) within AUTHORA workflows
3. **User disclosures** – Explicit user-provided disclosures

## Disclosure Types

| Type | Description |
|------|-------------|
| `user_disclosed` | User explicitly disclosed AI assistance |
| `system_tracked` | System inferred from AIActionLog or content_source |

## Content Source Values

| Value | Meaning |
|-------|---------|
| `user_written` | User-authored content |
| `ai_assisted` | AI-assisted (e.g., suggestions, edits) |
| `ai_generated` | AI-generated content |

## Storage

- **AIAssistanceDisclosure** – Stores `project_id`, `book_id`, `chapter_id`, `user_id`, `disclosure_type`, `content_source`, `ai_action_id`, `section_hint`, `notes`
- Linked to `AIActionLog` when `ai_action_id` is set

## Visibility

- Shown where AI assistance was used **if** user/admin workflow permits
- Supports academic/institutional policy workflows
- User can disclose AI-assisted sections explicitly

## API

- `GET /api/v1/projects/{project_id}/books/{book_id}/originality/ai-assistance` – List disclosures
- `POST /api/v1/projects/{project_id}/books/{book_id}/originality/ai-assistance` – Create disclosure

## Report Integration

- AI-assistance trace summary included in originality report
- Exportable as part of review report
