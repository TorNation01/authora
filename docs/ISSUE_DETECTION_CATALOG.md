# Story Integrity Engine — Issue Detection Catalog

## General Issues (all project types)

| Issue type | Category | Severity | Description |
|------------|----------|----------|-------------|
| `empty_section` | structure | moderate | Chapter has no content |
| `placeholder_heavy` | structure | low | Chapter very short (<50 words) |
| `unresolved_placeholder` | revision_blocker | moderate | TODO, TBD, [placeholder] markers in text |

## Fiction Issues

| Issue type | Category | Severity | Description |
|------------|----------|----------|-------------|
| `weak_opening` | structure | moderate | First chapter may be too short |
| `weak_ending` | structure | high | Final chapter may be incomplete |
| `character_single_appearance` | character | low | Character appears in only one chapter |

## Non-fiction Issues

| Issue type | Category | Severity | Description |
|------------|----------|----------|-------------|
| `weak_chapter_length` | structure | low | Chapter very short |
| `missing_transition` | clarity | low | Possible missing transition between chapters |

## Memoir Issues

| Issue type | Category | Severity | Description |
|------------|----------|----------|-------------|
| `reflection_missing` | emotional_arc | low | Long chapter without reflection markers |

## Workbook Issues

| Issue type | Category | Severity | Description |
|------------|----------|----------|-------------|
| `exercise_missing` | progression | low | Chapter may benefit from exercise/prompt |

## Severity Levels

- **low**: Minor suggestion; writer may choose to ignore
- **moderate**: Worth addressing; affects reader experience
- **high**: Significant gap; may affect completion
- **critical**: Blocker for export or quality

## Categories

- structure, continuity, pacing, character, emotional_arc
- setup_payoff, theme, clarity, progression, promise_fulfillment
- revision_blocker, export_readiness_blocker
