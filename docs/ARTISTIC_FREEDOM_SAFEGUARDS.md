# Artistic Freedom Safeguards

The Story Density Engine is designed to support writers without imposing a single notion of "good" prose. This document describes safeguards that protect artistic freedom.

## Principles

1. **Suggest, don't enforce** – All density issues are suggestions. Writers decide.
2. **Respect intentional slowness** – Slow pacing can be deliberate.
3. **Respect voice** – Emotional, reflective, or expansive prose is valid.
4. **Mode-aware** – Flexible and freeform modes reduce prescriptiveness.
5. **Mark as intentional** – First-class option when the writer disagrees.

## Safeguards by Component

### Guidance Modes

| Mode | Behavior |
|------|----------|
| **Guided** | Full detectors, standard thresholds. Most suggestions. |
| **Flexible** | Higher thresholds, intentional-style gates, fewer suggestions. Default for density. |
| **Freeform** | Only GeneralDensityDetector. Minimal suggestions. |

Writers who want less guidance can use **flexible** or **freeform** in project settings.

### Intentional Style Detection

The engine infers when a passage may be **intentionally** reflective, emotional, or thematic:

- **Emotional density** – Markers like "felt", "realized", "reflecting", "meaning", "silence"
- **Purpose hint** – "reflection" when reflective markers present
- **Scene purpose jobs** – reinforce_theme, deliver_reflection, deepen_character, build_setup

When detected, the engine **skips** creating issues for:

- Repetition (may be refrain/motif)
- Exposition overload (may be quiet emotional scene)
- Possible bloat (may be atmospheric/literary)
- Weak midpoint (may be deliberate quiet beat)
- Repeated emotional beat (may be deliberate refrain)

### Project-Type Tolerance

| Type | Safeguards |
|------|------------|
| **Memoir** | Highest drag tolerance (0.80). Reflection count 5 (flexible). Emotion count 25 (flexible). |
| **Fiction** | Literary drag 0.78 in flexible. Intentional gate for exposition, midpoint, repeated beat. |
| **Nonfiction** | Contemplative chapters skip missing_example. Intro/outro 2500 words (flexible). |
| **Workbook** | Reflection pages skip missing_exercise. Explanation count 8 (flexible). |

### Trim-vs-Strengthen: keep_as_intentional

For exposition_overload, possible_bloat, excessive_explanation, bloated_intro_or_outro:

- When `emotional_density >= 0.5` or intentional jobs with good clarity → **recommend keep_as_intentional**
- Alternatives always include "Mark as intentional" with "If this is deliberate"

The UI surfaces "Mark as intentional" as a button. Writers can dismiss the suggestion without changing the prose.

### Chapter Drag

Drag thresholds are **higher** for:

- Memoir (0.80)
- Fiction in flexible (0.78)
- Any project in flexible (0.70)

This reduces false positives for:

- Slow-burn romance
- Poetic memoir
- Literary fiction
- Contemplative nonfiction
- Atmospheric fantasy

## Writer-Facing Copy

The density UI uses supportive, non-judgmental language:

- "This section may be over-explaining" (not "This is filler")
- "Repetition warning" (not "Redundant")
- "Likely compressible" (not "Bloated")
- "Mark as intentional" (not "Ignore")
- "Resolve later" (not "Dismiss")

See `density-copy.ts` for full copy.

## Configuration

- **Project → Guidance mode**: `guided` | `flexible` | `freeform`
- **Book type**: Affects which detectors run (fiction, memoir, nonfiction, workbook)
- Density respects both when building the map and running detectors.

## Related Docs

- [STORY_DENSITY_HARDENING.md](./STORY_DENSITY_HARDENING.md) – Technical hardening details
- [FILLER_FALSE_POSITIVE_REDUCTION.md](./FILLER_FALSE_POSITIVE_REDUCTION.md) – False positive reduction
- [STORY_DENSITY_ENGINE.md](./STORY_DENSITY_ENGINE.md) – Engine overview
- [TRIM_VS_STRENGTHEN_ENGINE.md](./TRIM_VS_STRENGTHEN_ENGINE.md) – Decision engine
