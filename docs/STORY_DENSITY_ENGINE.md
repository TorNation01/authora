# Story Density Engine (SDE)

The Story Density Engine is an intelligent manuscript analysis layer that detects clutter, filler, repetition, low-value sections, weak support, overbuilt and underwritten sections, and structural density problems. It helps writers trim, compress, strengthen, or expand with clarity.

## Relationship to Story Integrity Engine

- **Story Integrity Engine (SIE)** asks: *What is missing? What is unresolved? What is broken?*
- **Story Density Engine (SDE)** asks: *What is bloated? What is repetitive? What is dragging? What is too thin? What needs trimming? What needs strengthening?*

The SDE works alongside the SIE as a separate analysis layer. Both engines share the same project and book context but use different tables, scans, and detectors.

## Core Capabilities

- **Density analysis engine** — Chapter and manuscript-level density scoring
- **Clutter detection** — Scene/section purpose clarity, low-value content
- **Filler detection** — Redundant explanation, padding, tangential drift
- **Repetition detection** — Repeated concepts, emotional beats, arguments
- **Weak support detection** — Thin transitions, underdeveloped payoffs, missing examples
- **Trim/compress/strengthen assistant** — Guided fix suggestions per issue
- **Project-type-aware modes** — Fiction, non-fiction, memoir, workbook, hybrid, freeform
- **Mode-aware behaviour** — Guided, flexible, freeform

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Story Density Engine                           │
├─────────────────────────────────────────────────────────────────┤
│  Scanner/Orchestrator                                            │
│    ├── Load chapters, build story map                            │
│    ├── Build density map                                         │
│    ├── Run project-type detectors                                │
│    └── Persist DensityScan + DensityIssue                         │
├─────────────────────────────────────────────────────────────────┤
│  Density Map                                                     │
│    ├── density_by_chapter (info/emotional/tension density)        │
│    ├── repeated_concepts, repeated_beats                          │
│    ├── thin_transitions, underweighted_payoffs                    │
│    └── manuscript_density_score (0–100)                          │
├─────────────────────────────────────────────────────────────────┤
│  Detectors (project-type + guidance-mode aware)                   │
│    ├── GeneralDensityDetector                                    │
│    ├── FictionDensityDetector                                    │
│    ├── NonfictionDensityDetector                                │
│    ├── MemoirDensityDetector                                     │
│    └── WorkbookDensityDetector                                  │
├─────────────────────────────────────────────────────────────────┤
│  Fix Assistant                                                   │
│    └── get_density_fix_guidance(issue_type, issue)               │
└─────────────────────────────────────────────────────────────────┘
```

## Data Model

- **DensityScan** — One scan run per book (full_project, chapter, pre_export, etc.)
- **DensityIssue** — Individual issues with type, category, action_category, severity, fix_suggestions

## API Endpoints

- `POST /api/v1/projects/{id}/books/{id}/density/scan` — Run density scan
- `GET /api/v1/projects/{id}/books/{id}/density/scans` — List scans
- `GET /api/v1/projects/{id}/books/{id}/density/issues` — List issues (filterable)
- `GET /api/v1/projects/{id}/books/{id}/density/health` — Density health summary
- `GET /api/v1/projects/{id}/books/{id}/density/issues/{id}` — Get single issue
- `PATCH /api/v1/projects/{id}/books/{id}/density/issues/{id}` — Update status
- `GET /api/v1/projects/{id}/books/{id}/density/issues/{id}/guidance` — Get fix guidance

## Feature Flag

- `feature_story_density` — Enable/disable SDE (default: true)
- DB override: `Setting.key = "feature.story_density"`, `value = {"enabled": true|false}`

## UX Principles

The SDE must feel:
- Intelligent, supportive, practical, non-judgmental, premium, calm
- Useful in revision and before export
- Trustworthy — helps distinguish filler from necessary setup
- Balanced — helps strengthen weak spots, not only cut

Avoid:
- Over-cut bias
- Punishing subtle or literary writing
- Noisy or shallow warnings
- Formulaic writing pressure
