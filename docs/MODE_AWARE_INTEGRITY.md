# Mode-Aware Integrity

The Story Integrity Engine adapts to project guidance mode and project type.

## Guidance Modes

### Guided Mode

- **Stronger structure checks** — Framework-aware beat detection when framework is available
- **More active suggestions** — Full detector set for project type
- **Framework missing-beat detection** — (Future) Compare against writing framework stages

### Flexible Mode

- **Lighter structure assumptions** — Softer severity for missing framework elements
- **More optional suggestions** — Low-severity issues emphasized as suggestions
- **Stronger cross-thread and consistency help** — Continuity, pacing, unresolved threads

### Freeform Mode

- **No rigid beat enforcement** — No inciting incident, midpoint, climax requirements
- **No genre-pressure warnings** — Unusual structure treated as valid
- **Issue detection focused on** — Continuity, clarity, unresolved threads, pacing, cohesion
- **Treat unusual structure as valid** — Unless clearly broken (empty, placeholder, etc.)

## Project Type Modes

| Mode | Detectors | Priorities |
|------|-----------|------------|
| Fiction | General + Fiction | Plot threads, character arcs, emotional movement, setup/payoff, pacing |
| Non-fiction | General + Nonfiction | Structure, clarity, transitions, takeaway |
| Memoir | General + Memoir | Emotional coherence, reflection depth, thematic throughline |
| Workbook | General + Workbook | Progression, exercises, action steps |
| Hybrid | General + Nonfiction + Memoir | Mixed-weight analysis |
| Freeform | General | Loose continuity, weak sections, no rigid structure |

## User Controls

- **Reduce strictness** — (Future) Per-project setting to soften severity
- **Turn off issue classes** — (Future) Disable specific categories
- **Suppress genre/framework assumptions** — Freeform mode does this
- **Mark as intentional** — Available now; user can mark any issue
- **Disable continuous scanning** — (Future) When continuous mode exists
