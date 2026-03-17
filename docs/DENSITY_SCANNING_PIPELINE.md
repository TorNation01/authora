# Density Scanning Pipeline

The Story Density Engine scanning pipeline analyzes manuscripts for clutter, filler, repetition, and weak support.

## Scan Types

| Type | Description |
|------|--------------|
| `full_project` | Full manuscript density scan |
| `chapter` | Single chapter scan |
| `section` | Section-level scan |
| `revision_pass` | Scan during revision pass |
| `pre_export` | Pre-export density cleanup check |
| `trim_chapter` | Targeted "trim this chapter" scan |
| `strengthen_targeted` | "What needs strengthening?" targeted scan |

## Pipeline Flow

1. **Load project and book** — Fetch project (vault_characters, vault_themes, timeline_events), book (planner_data), chapters (content, word_count)
2. **Build story map** — `build_story_map()` from Story Integrity Engine (chapter purposes, promises, emotional markers, etc.)
3. **Build density map** — `build_density_map(chapters, story_map)` computes:
   - Per-chapter: information_density, emotional_density, tension_density, movement, purpose_hint, is_midpoint
   - Cross-chapter: repeated_concepts, repeated_beats, thin_transitions, underweighted_payoffs
   - manuscript_density_score (0–100)
4. **Run detectors** — `get_density_detectors_for_project(project_type, guidance_mode)` returns detector classes; each runs `detect()` and returns issues
5. **Persist** — Create DensityScan, create DensityIssue for each detected issue

## Scan Timing

- **On demand** — User clicks "Scan" in Density panel
- **After chapter completion** — (Future: optional hook)
- **During revision pass** — (Future: optional integration)
- **Before export** — (Future: pre-export check)
- **Scheduled** — (Future: optional low-frequency monitoring)

## Caching and Differential Rescans

- Each scan creates a new DensityScan record; issues are linked to that scan
- No automatic differential rescans; full scan runs each time
- Density map snapshot stored in `density_map_snapshot` for debugging/analytics

## Project-Type and Guidance-Mode Awareness

- **Project type** (fiction, nonfiction, memoir, workbook, hybrid) determines which detectors run
- **Guidance mode** (guided, flexible, freeform) affects detector strictness:
  - **Guided** — Stronger checks, framework-aware
  - **Flexible** — Softer assumptions, cross-genre tolerance
  - **Freeform** — GeneralDensityDetector only; no formula enforcement
