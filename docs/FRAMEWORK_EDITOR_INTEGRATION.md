# Framework-Aware Editor and AI Assist Integration

This document describes how the framework engine integrates with the editor and AI assist tools.

## Current State

- **Book.framework_id**: Links books to their writing framework
- **planner_data**: Stores `framework_slug`, `framework_name`, and `structure_framework` (from wizard)
- **Framework metadata**: `planning_stages`, `beat_stages`, `ai_prompt_presets`, `scene_prompts`, `revision_checklist`

## Integration Points

### 1. Editor Sidebar

**Planned**: Show current act/beat/phase in editor sidebar.

- Use `chapter.content` or `chapter_brief` to infer which beat the chapter belongs to
- Framework `chapter_skeletons` or `beat_stages` define beat mapping
- Display: "Act II: Rising Conflict" or "Beat: Midpoint"

### 2. AI Scene Prompts

**Planned**: Suggest next scene/chapter prompt based on framework stage.

- Use `framework.scene_prompts` (e.g. `{"setup": "Write the opening that establishes...", "midpoint": "Write the midpoint revelation..."}`)
- Use `framework.ai_prompt_presets` for generic prompts
- Substitute `[beat]` or `[genre]` from book context

### 3. Beat Completion Warnings

**Planned**: Warn if major beats are missing.

- Compare `chapter_skeletons` (or chapter beats) against `planning_stages` / `beat_stages`
- Flag chapters with missing or empty content for key beats

### 4. "Help Me Continue" Context

**Planned**: Offer "help me continue this section" based on current framework context.

- Pass `framework_slug`, `current_beat`, `scene_prompts[beat]` to AI prompt
- Example: "You're writing the midpoint of a three-act structure. Continue from here..."

### 5. Framework-Specific Rewrite Prompts

**Planned**: Offer framework-specific rewrite prompts.

- Use `ai_prompt_presets` and `revision_checklist` for rewrite suggestions
- Example: "Strengthen the inciting incident" (three-act)

### 6. "Am I On Track?" Review

**Planned**: Review manuscript against selected structure.

- Compare chapter count and beat coverage to `chapter_skeletons`
- Use `revision_checklist` for qualitative feedback

## Implementation Notes

- **Data source**: `book.framework` relationship loads full framework when needed
- **Chapter beat**: Consider adding `chapter.beat` or `chapter.framework_stage` to store explicit mapping
- **Planner data**: `planner_data.current_beat` or `planner_data.current_act` can be set by user or inferred

## API Usage

- `GET /api/v1/projects/{id}/books/{id}` – book response includes `framework_id`; frontend can fetch framework via `GET /api/v1/frameworks/{id}` for full metadata
- Fiction/Nonfiction workspace endpoints can include framework context when generating AI prompts
