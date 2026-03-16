# Genre Guide Settings

Genre guidance is controlled at the project level via `guidance_mode`. It affects planning, writing, accountability, milestones, and Finish Mode.

## Project-Level Control

- **Location**: Project settings (`/dashboard/projects/{id}/settings`)
- **Scope**: Applies to all books in the project
- **Persistence**: Stored in `projects.guidance_mode`

## Mode Behavior

| Feature | Guided | Flexible | Freeform |
|---------|--------|----------|----------|
| Template | Full | Optional, lighter | None |
| Framework | Full | Optional | None |
| Chapter skeletons | Full from template | Reduced (max 5) | One blank |
| Milestones | Template/framework | Template or generic | Generic only |
| Framework stage in dashboard | Yes | No | No |
| Genre-specific prompts | Yes | Mixed | No |
| Beat/structure warnings | Yes | No | No |

## UI Copy

- "You can change this later."
- "Choose the amount of guidance that helps you write best."
- "Structure is here to support your process, not limit it."
- "Freeform mode keeps the tools, without the genre rails."

## Badge

Projects display a guidance mode badge (Guided / Flexible / Freeform) in the project header.
