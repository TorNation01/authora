# AUTHORA Framework Engine

The framework engine powers project templates, planning flows, writing prompts, chapter scaffolds, milestone generation, and accountability paths based on the kind of book the user is writing. It makes AUTHORA feel like a guided book-building platform, not just a blank editor with AI attached.

## Overview

- **Fiction frameworks**: Three-Act, Hero's Journey, Save-the-Cat, Romance beats, Mystery/Thriller, Series arc, Character-driven, Custom
- **Non-fiction frameworks**: Problem→Solution→Result, Step-by-Step, Authority, Teaching, Workbook, Memoir-Driven Lesson, Modular, Custom
- **Recommendation engine**: Suggests frameworks based on genre, template, and project type
- **Framework-aware generation**: Planning boards, chapter skeletons, milestones, and AI prompts are derived from the selected framework

## Architecture

```
writing_frameworks (DB)
    ├── planning_stages
    ├── beat_stages
    ├── chapter_skeletons
    ├── milestone_logic
    ├── accountability_mapping
    ├── revision_checklist
    ├── ai_prompt_presets
    ├── scene_prompts
    └── recommendation_rules

books.framework_id → writing_frameworks.id
project_templates.structure_framework → writing_frameworks.slug (via mapping)
```

## Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Framework definitions | `authora/data/framework_definitions.py` | Source of truth for all framework metadata |
| Seed script | `authora/scripts/seed_writing_frameworks.py` | Load definitions into DB |
| Recommendation engine | `authora/services/framework_recommendation.py` | Score and recommend frameworks |
| Framework API | `authora/api/routes/frameworks.py` | List, recommend, get by ID/slug |
| Project wizard | `authora/services/project_wizard.py` | Resolve framework, create book with framework_id, use chapter_skeletons |
| Admin management | `authora/api/routes/admin.py` | CRUD, reorder, duplicate, usage analytics |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/frameworks` | List frameworks (optional book_type, featured_only) |
| GET | `/api/v1/frameworks/recommend` | Recommend frameworks (book_type, genre, template_id, etc.) |
| GET | `/api/v1/frameworks/{id_or_slug}` | Get framework by ID or slug |
| GET | `/api/v1/admin/frameworks` | Admin: list all frameworks |
| PATCH | `/api/v1/admin/frameworks/{id}` | Admin: update framework |
| POST | `/api/v1/admin/frameworks/{id}/duplicate` | Admin: duplicate framework |
| POST | `/api/v1/admin/frameworks/reorder` | Admin: reorder frameworks |
| GET | `/api/v1/admin/frameworks/usage` | Admin: usage analytics |

## Project Wizard Integration

When creating a project via the wizard:

1. **framework_id** (optional): Explicit framework selection overrides template
2. **structure_framework** (optional): Slug or template-style slug (e.g. `emotional_arc` → `memoir_lesson`)
3. **Template**: If no framework_id, framework is resolved from `template.structure_framework`
4. **Recommendation**: If template has no structure_framework, top recommended framework is used

Chapter skeletons are sourced in order: template.chapter_skeletons → framework.chapter_skeletons.

## Template → Framework Mapping

Some templates use slugs that differ from framework slugs. The mapping in `framework_recommendation.py`:

| Template structure_framework | Framework slug |
|-----------------------------|----------------|
| emotional_arc | memoir_lesson |
| module_exercise | workbook |
| prompt_based | workbook |
| section_sequence | custom_fiction |
| collection_sequence | custom_fiction |
| client_workflow | custom_nonfiction |

## Deployment

1. Run migration: `alembic upgrade head` (from `apps/api`)
2. Seed frameworks: `python -m authora.scripts.seed_writing_frameworks` (from `apps/api`)

## Related Documentation

- [FICTION_FRAMEWORKS.md](./FICTION_FRAMEWORKS.md) – Fiction framework details
- [NONFICTION_FRAMEWORKS.md](./NONFICTION_FRAMEWORKS.md) – Non-fiction framework details
- [FRAMEWORK_RECOMMENDATION_RULES.md](./FRAMEWORK_RECOMMENDATION_RULES.md) – Recommendation logic
- [FRAMEWORK_EDITOR_INTEGRATION.md](./FRAMEWORK_EDITOR_INTEGRATION.md) – Editor and AI assist integration
- [ADMIN_FRAMEWORK_MANAGEMENT.md](./ADMIN_FRAMEWORK_MANAGEMENT.md) – Admin operations
