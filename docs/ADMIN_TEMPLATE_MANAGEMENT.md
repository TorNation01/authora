# Admin Template Management

## Overview

Admins can manage project templates via the admin API. All endpoints require `AdminUser` (admin role).

## Endpoints

### List Templates

```
GET /api/v1/admin/templates?include_disabled=false
```

Returns all templates with id, slug, category, name, sort_order, is_featured, is_disabled.

### Update Template

```
PATCH /api/v1/admin/templates/{template_id}
```

Body (all optional):

```json
{
  "name": "New name",
  "description": "...",
  "who_it_is_for": "...",
  "expected_outcome": "...",
  "suggested_workflow": "...",
  "book_type": "fiction",
  "genre": "Romance",
  "structure_framework": "three_act",
  "sort_order": 10,
  "is_featured": true,
  "is_disabled": false,
  "default_structure": { ... },
  "default_milestones": [ ... ],
  "setup_questions": [ ... ],
  "chapter_skeletons": [ ... ]
}
```

### Duplicate Template

```
POST /api/v1/admin/templates/{template_id}/duplicate
```

Creates a copy with slug `{original}-copy` (or `{original}-copy-{hex}` if slug exists). Name is `{original} (copy)`. `is_featured` and `is_disabled` are reset.

### Reorder Templates

```
POST /api/v1/admin/templates/reorder
Content-Type: application/json

{
  "template_ids": ["uuid1", "uuid2", ...]
}
```

Updates `sort_order` for each template by position in the list.

### Template Usage Analytics

```
GET /api/v1/admin/templates/usage
```

Returns projects and books count per template:

```json
{
  "by_template": {
    "template-uuid-1": { "projects": 5, "books": 5 },
    "template-uuid-2": { "projects": 2, "books": 3 }
  }
}
```

## Operations

| Action | Endpoint |
|--------|----------|
| Create template | Not yet – use seed script + duplicate |
| Edit template | PATCH /admin/templates/{id} |
| Disable template | PATCH with `is_disabled: true` |
| Enable template | PATCH with `is_disabled: false` |
| Feature template | PATCH with `is_featured: true` |
| Reorder | POST /admin/templates/reorder |
| Duplicate | POST /admin/templates/{id}/duplicate |
| View usage | GET /admin/templates/usage |

## Future: User-Created Templates

The schema supports `parent_id` and custom templates. A future feature could allow users to save a project as a personal template (stored with `user_id` or in a separate `user_templates` table).
