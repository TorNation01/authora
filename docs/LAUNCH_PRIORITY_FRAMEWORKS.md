# Launch Priority Frameworks

AUTHORA's first-wave flagship framework pairings. These are the strongest, most polished launch-ready experiences.

## Priority Pairings

### Fiction

| Genre | Primary Framework | Secondary Framework |
|-------|-------------------|---------------------|
| Romance | Romance Beat Structure | Three-Act Structure |
| Fantasy | Hero's Journey | Series Fiction Arc |
| Thriller / Mystery | Mystery / Thriller Structure | Three-Act Structure |
| Sci-fi | Three-Act Structure | Hero's Journey |

### Non-Fiction

| Genre | Framework |
|-------|-----------|
| Memoir | Memoir-Driven Lesson Framework |
| Self-Help | Step-by-Step Transformation |
| Business / Authority | Authority / Credibility Book |
| Workbook / Guided | Workbook / Guided Action Framework |

## What's Polished for Each

For each launch-priority framework:

- **Planning boards**: `planning_stages` with `hint` and `prompt` per stage; `planning_board` in manuscript_scaffolding
- **Chapter scaffolds**: Rich `chapter_skeletons` with beat and summary
- **Scene/section prompts**: Complete `scene_prompts` for every beat
- **Milestone logic**: `milestone_logic` with stages and labels
- **Revision checklist**: Comprehensive `revision_checklist`
- **AI assist suggestions**: Rich `ai_prompt_presets` (brainstorm, scene, continue, strengthen, etc.)
- **Next step guidance**: `next_step_guidance` in `accountability_mapping` per stage

## API Usage

### List launch-priority frameworks

```
GET /api/v1/frameworks?launch_priority=true&book_type=fiction
GET /api/v1/frameworks?launch_priority=true&book_type=nonfiction
```

### Get recommendations (launch-priority frameworks are boosted)

```
GET /api/v1/frameworks/recommend?book_type=fiction&genre=Romance
GET /api/v1/frameworks/recommend?book_type=nonfiction&genre=Memoir
```

## Setup Flow

In the project setup / wizard flow:

1. User selects book type (fiction / nonfiction)
2. User selects genre (Romance, Fantasy, Thriller, Memoir, etc.)
3. Call `GET /api/v1/frameworks/recommend?book_type=X&genre=Y` – launch-priority frameworks appear first
4. Or call `GET /api/v1/frameworks?launch_priority=true&book_type=X` to show only flagship frameworks
5. Display framework cards with name, description, planning stages preview
6. On selection, create project with `framework_id`
