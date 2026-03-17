# Template Marketplace System — Final Outputs

## 1. Template System Summary

AUTHORA provides a template marketplace for manuscript structure and project setup.

### Template Library

- **Location**: `/dashboard/templates`
- **Navigation**: Sidebar → Templates (LayoutTemplate icon)
- **Content**: Browse templates by category; each template includes name, description, book type, genre, and featured badge.

### Categories

- **Source**: `GET /api/v1/templates/categories` returns top-level templates with children.
- **Filtering**: Sidebar filter by category (fiction, nonfiction, memoir, workbook, etc.).
- **Structure**: Each category has a parent template and optional child templates (e.g. Fiction → Romance, Fantasy, Thriller).

### Template Preview

- **Trigger**: Click "Preview" on any template card.
- **Content**: Modal with full details: description, best for, what you get, suggested workflow, structure (chapter count).
- **API**: `GET /api/v1/templates/{id}` for full template data.

### Apply Template

- **Flow**: Click "Use template" → redirects to `/dashboard/projects/new?templateId={id}`.
- **Behavior**: Project creation wizard opens with template pre-selected; user completes wizard to create project + book from template.
- **API**: `POST /api/v1/projects/from-wizard` with `template_id`.

---

## 2. Category Structure

### Top-Level Categories (from `template_definitions.py`)

| Category | Description |
|----------|-------------|
| **fiction** | Build stories with structure, character, tension, and momentum. |
| **nonfiction** | Turn expertise, ideas, or message into a clear and compelling book. |
| **memoir** | Shape lived experience into a story with meaning, emotion, and reflection. |
| **workbook** | Create guided content with prompts, exercises, and action-oriented structure. |
| **journal** | Design reflective writing experiences with prompts, rhythms, and themes. |
| **poetry** | Organize a collection with flow, sequence, and emotional shape. |
| **short_story_collection** | Build a cohesive set of stories with shared themes and strong structure. |
| **series_project** | Plan connected books with continuity, lore, and long-form story arcs. |
| **ghostwritten_book** | Capture a client's message, voice, and source material in a structured flow. |
| **custom** | Start from scratch with full creative control. |

### Sub-Templates (Examples)

- **Fiction**: Romance, Fantasy, Thriller, Sci-Fi, Horror, Historical, Literary, YA, Contemporary, Short Story, Series, General.
- **Nonfiction**: Self-Help, Business, Finance, Health, Parenting, Relationships, Educational, Thought Leadership, How-To, Personal Story, Faith, Professional, General.

### API Response Shape

```json
{
  "category": "fiction",
  "name": "Fiction Novel",
  "slug": "fiction",
  "template": { "id": "...", "name": "...", "description": "...", ... },
  "children": [
    { "id": "...", "name": "Romance", "slug": "fiction-romance", ... },
    ...
  ]
}
```

---

## 3. Production-Ready Confirmation

### Implemented Features

| Feature | Status | Notes |
|---------|--------|-------|
| Template library | ✅ | `/dashboard/templates` with category filter |
| Categories | ✅ | Fiction, nonfiction, memoir, etc. with sub-templates |
| Template preview | ✅ | Modal with full details |
| Apply template | ✅ | Redirect to project wizard with `?templateId=` |

### Future-Ready (Schema)

| Field | Purpose |
|-------|---------|
| `price_cents` | Paid template pricing (nullable; null = free) |
| `is_paid` | Boolean flag for paid templates |
| `creator_id` | Creator attribution (admin-controlled initially) |

Migration: `037_add_template_marketplace_fields.py`

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/templates` | List templates (filter: category, parent_id, featured) |
| GET | `/api/v1/templates/categories` | Categories with parent + children |
| GET | `/api/v1/templates/featured-launch` | Featured premium templates |
| GET | `/api/v1/templates/{id}` | Full template details |
| GET | `/api/v1/templates/slug/{slug}` | Template by slug |
| POST | `/api/v1/projects/from-wizard` | Create project + book from template |

### Components

- **Template marketplace page** (`/dashboard/templates/page.tsx`): Library, category filter, preview dialog.
- **TemplateLibraryCard**: Card for each template with Use template / Preview.
- **TemplatePreviewCard** (onboarding): Reusable preview; marketplace uses inline dialog.

### Production Readiness

- **Auth**: All template endpoints require authenticated user.
- **Disabled templates**: Excluded from list and get (404).
- **Apply flow**: Uses existing wizard; no new project-creation logic.
- **Future**: Schema supports paid templates and creator uploads; UI and payment logic to be added later.

---

## Related Documentation

- [PROJECT_CREATION_WIZARD.md](./PROJECT_CREATION_WIZARD.md) — Wizard flow and template selection
- [ONBOARDING_FLOW_SUMMARY.md](./ONBOARDING_FLOW_SUMMARY.md) — Onboarding and template usage
