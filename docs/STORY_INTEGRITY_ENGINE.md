# Story Integrity Engine (SIE)

The Story Integrity Engine is an intelligent manuscript analysis and assistance system that detects incomplete, weak, unresolved, inconsistent, underdeveloped, or broken story elements across a writing project and helps the writer understand and fix them.

## Architecture

### Core Components

| Component | Purpose |
|-----------|---------|
| **Scanner/Orchestrator** | Runs scans, coordinates detectors, persists results |
| **Project-type adapter** | Selects detectors based on `knowledge_mode` (fiction, nonfiction, memoir, workbook, hybrid) |
| **Story map** | Internal map of threads, characters, themes, chapter purposes |
| **Issue detectors** | Rule-based detectors per project type |
| **Recommendation engine** | Guided fix suggestions for each issue |
| **Issue registry** | Persisted issues with status (open, resolved, ignored, intentional) |

### Data Flow

1. User triggers scan (manual or scheduled)
2. Scanner loads chapters, vault data, project metadata
3. Story map is built from content + metadata
4. Detectors run based on project type and guidance mode
5. Issues are stored with severity, category, fix suggestions
6. User views issues in Story Health panel, resolves or marks intentional

## Project-type-aware Modes

| Mode | Priorities |
|------|------------|
| **Fiction** | Plot threads, character arcs, emotional movement, setup/payoff, pacing, climax/resolution |
| **Non-fiction** | Structural clarity, chapter logic, argument flow, transitions, takeaway |
| **Memoir** | Emotional coherence, reflection depth, thematic throughline |
| **Workbook** | Progression logic, exercises/prompts, action steps |
| **Hybrid** | Mixed-weight analysis |
| **Freeform** | Loose continuity, weak section detection, no rigid structure enforcement |

## Guidance Mode Behaviour

- **Guided**: Stronger structure checks, framework-aware detection
- **Flexible**: Lighter assumptions, softer severity for missing framework elements
- **Freeform**: No rigid beat enforcement, focus on continuity and clarity

## API Endpoints

- `POST /api/v1/projects/{id}/books/{id}/integrity/scan` — Run scan
- `GET /api/v1/projects/{id}/books/{id}/integrity/scans` — List scans
- `GET /api/v1/projects/{id}/books/{id}/integrity/issues` — List issues (filterable)
- `GET /api/v1/projects/{id}/books/{id}/integrity/health` — Story health summary
- `GET /api/v1/projects/{id}/books/{id}/integrity/chapter-health` — Chapter health, pacing, and structure analysis
- `GET /api/v1/projects/{id}/books/{id}/integrity/issues/{id}` — Get issue
- `PATCH /api/v1/projects/{id}/books/{id}/integrity/issues/{id}` — Update status
- `GET /api/v1/projects/{id}/books/{id}/integrity/issues/{id}/guidance` — Get fix guidance

## UX Principles

- Non-judgmental, supportive language
- Clear explanations and practical fix suggestions
- Writer remains in control; system guides, does not take over
- No auto-rewriting; analysis and suggestions only
