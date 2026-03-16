# Template Creation Flow

## User Flow

1. **Choose mode**: Quick start (name only) or Guided start (wizard)
2. **Guided wizard steps**:
   - Step 1: Choose project type (template category)
   - Step 2: Choose genre/sub-type (if category has children)
   - Step 3: Name project and book
   - Step 4: Define core idea
   - Step 5: Select structure framework (optional)
   - Step 6: Set writing goals (optional)
   - Step 7: Review and create

3. **Creation**: `POST /api/v1/projects/from-wizard` creates:
   - Project (with `template_id`)
   - Book (with `template_id`, `planner_data`, `genre`, `type`)
   - Chapters from template `chapter_skeletons`
   - FictionWorkspace or NonfictionWorkspace

## Wizard Payload

```json
{
  "template_id": "uuid | null",
  "project_name": "My Novel",
  "book_title": "Optional - defaults to project name",
  "book_type": "fiction | nonfiction",
  "genre": "Romance",
  "core_idea": "One sentence premise",
  "structure_framework": "three_act",
  "target_words": 80000,
  "target_date": "2025-12-31"
}
```

## Template Application

When a template is selected, the wizard service:

1. Resolves `book_type` and `genre` from template
2. Builds `planner_data` from wizard answers and template defaults
3. Creates chapters from `chapter_skeletons`
4. Creates FictionWorkspace or NonfictionWorkspace with premise/core_message

## Custom / Blank

When `template_id` is null or user selects Custom/Blank:

- Minimal structure (single Notes section)
- Single chapter skeleton
- No genre or structure framework
- User defines everything
