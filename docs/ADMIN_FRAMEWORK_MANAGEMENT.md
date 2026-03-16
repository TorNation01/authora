# Admin Framework Management

Admin endpoints for managing the writing framework library.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/admin/frameworks` | List all frameworks (optional include_disabled, book_type) |
| PATCH | `/api/v1/admin/frameworks/{id}` | Update framework |
| POST | `/api/v1/admin/frameworks/{id}/duplicate` | Duplicate framework (creates new slug) |
| POST | `/api/v1/admin/frameworks/reorder` | Reorder by id list |
| GET | `/api/v1/admin/frameworks/usage` | Usage analytics (books per framework) |

## Permissions

All endpoints require `AdminUser` (admin role).

## Update Payload (PATCH)

```json
{
  "name": "string",
  "description": "string",
  "ideal_use_cases": "string",
  "ideal_genres": ["string"],
  "planning_stages": [...],
  "beat_stages": [...],
  "chapter_structure": {...},
  "manuscript_scaffolding": {...},
  "chapter_skeletons": [...],
  "milestone_logic": {...},
  "accountability_mapping": {...},
  "revision_checklist": [...],
  "ai_prompt_presets": {...},
  "recommendation_rules": {...},
  "scene_prompts": {...},
  "sort_order": 0,
  "is_featured": false,
  "is_disabled": false
}
```

All fields are optional. Only provided fields are updated.

## Duplicate

Creates a new framework with:
- `slug`: `{original}-copy` or `{original}-copy-{hex8}` if conflict
- `name`: `{original} (copy)`
- `is_featured`: false
- `is_disabled`: false
- All other fields copied from source

## Reorder

```json
{
  "framework_ids": ["uuid1", "uuid2", ...]
}
```

Sort order is set to index in the list for each framework.

## Usage Analytics

Returns:
```json
{
  "by_framework": {
    "framework-uuid": 42,
    ...
  }
}
```

Count of books per framework_id.

## Seeding

Frameworks are seeded from `authora/data/framework_definitions.py` via:

```bash
cd apps/api && python -m authora.scripts.seed_writing_frameworks
```

The script upserts by slug: existing frameworks are updated, new ones are created.
