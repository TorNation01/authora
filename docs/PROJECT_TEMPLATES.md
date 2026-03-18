# AUTHORA Project Templates

## Overview

The project template system lets users create new book projects from guided templates tailored to fiction, non-fiction, memoir, workbook, journal, poetry, short story collection, series writing, ghostwritten books, and custom projects.

Templates reduce blank-page paralysis by providing structure, planning sections, milestones, and AI prompts from the start.

## Template Categories

| Category | Slug | Description |
|----------|------|-------------|
| Fiction | `fiction` | Novels with genre sub-templates (Romance, Fantasy, Thriller, etc.) |
| Non-fiction | `nonfiction` | Expert/thought-leader books with sub-templates (Self-help, Business, etc.) |
| Memoir | `memoir` | Personal memoir with emotional arc and timeline |
| Workbook | `workbook` | Interactive workbook with exercises and worksheets |
| Journal | `journal` | Guided journal with prompts |
| Poetry | `poetry` | Poetry collection with sections |
| Short Story Collection | `short-story-collection` | Cohesive short story collection |
| Series Project | `series-project` | Multi-book series with continuity |
| Ghostwritten Book | `ghostwritten-book` | Client book with voice capture and approval workflow |
| Custom / Blank | `custom-blank` | Minimal structure, full creative control |

## Template Structure

Each template includes:

- **Metadata**: name, description, who it's for, expected outcome, suggested workflow
- **Book type**: fiction | nonfiction
- **Genre**: e.g. Romance, Self-Help
- **Structure framework**: e.g. three_act, problem_solution_result
- **Default structure**: planning sections (JSON)
- **Default milestones**: planning → draft → revision
- **Default planning prompts**: key questions to answer
- **Default accountability**: reminder frequency, goal type
- **AI prompts**: brainstorm, character, scene, etc.
- **Export recommendations**: docx, pdf, epub
- **Setup questions**: guided wizard questions
- **Chapter skeletons**: initial chapter list

## Sub-templates

Parent templates (e.g. Fiction, Non-fiction) can have child sub-templates for genre-specific setup:

- **Fiction**: Romance, Fantasy, Thriller, Sci-Fi, Horror, Historical, Literary, YA, Contemporary, Short/Novella, Series, General
- **Non-fiction**: Self-help, Business, Finance, Health, Parenting, Relationships, Educational, Thought Leadership, How-to, Faith, Professional, General

## Database Schema

Templates are stored in `project_templates`:

- `id`, `slug`, `category`, `parent_id` (for sub-templates)
- `name`, `description`, `who_it_is_for`, `expected_outcome`, `suggested_workflow`
- `book_type`, `genre`, `structure_framework`
- `default_structure`, `default_milestones`, `default_planning_prompts`, `default_accountability` (JSONB)
- `ai_prompts`, `export_recommendations`, `setup_questions`, `chapter_skeletons` (JSONB)
- `sort_order`, `is_featured`, `is_disabled`

## API Endpoints

- `GET /api/v1/templates` – List templates (filter by category, parent, featured)
- `GET /api/v1/templates/categories` – Categories with children
- `GET /api/v1/templates/all` – All templates for wizard
- `GET /api/v1/templates/{id}` – Full template by ID
- `GET /api/v1/templates/slug/{slug}` – Full template by slug

## Seed Data

Templates are seeded from `authora/data/template_definitions.py`. They are included in the main seed:

```bash
npm run db:seed
```

This seeds users, project templates (35), and writing frameworks (16). To seed templates only:

```bash
npm run db:seed:templates
```

Re-running the seed updates existing templates by slug.
