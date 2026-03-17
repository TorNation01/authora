# Story Density Engine Hardening

This document describes the hardening pass applied to the AUTHORA Story Density Engine to reduce false positives and protect artistic freedom.

## Goals

- Avoid over-cutting thoughtful or literary writing
- Avoid punishing intentional slowness
- Avoid punishing quiet emotional scenes
- Avoid punishing reflective memoir passages that carry meaning
- Avoid flattening voice in the name of efficiency
- Avoid telling every writer to "make it faster"
- Improve discrimination between true filler and intentional atmosphere

## Architecture Overview

The Story Density Engine consists of:

1. **Density map** – Builds per-chapter metrics (information density, emotional density, tension, movement, purpose hints)
2. **Detectors** – General, Fiction, Nonfiction, Memoir, Workbook (mode-aware)
3. **Chapter drag analyzer** – Flags consecutive dragging chapters, merge candidates
4. **Trim-vs-strengthen engine** – Recommends action (trim, compress, strengthen, keep_as_intentional)
5. **Guidance modes** – `guided`, `flexible`, `freeform`

## Hardening Changes

### 1. Tolerance Constants (`constants.py`)

| Constant | Guided | Flexible | Purpose |
|----------|--------|----------|---------|
| Repetition threshold | 0.30 | 0.38 | Higher = less sensitive to refrains, motifs |
| Thin section words | 80 | 120 | Brief bridges tolerated in flexible |
| Bloat words | 5000 | 6500 | Longer chapters before flagging |
| Exposition words min | — | 1200 | Must be substantial before flagging |
| Memoir reflection count | 3 | 5 | Layered reflection tolerated |
| Memoir emotion count | 15 | 25 | Authentic voice protected |
| Intro/outro words | 1500 | 2500 | Contemplative nonfiction |
| Drag score threshold | 0.60 | 0.70 | Memoir: 0.80, Literary fiction: 0.78 |

### 2. Intentional Style Detection (`detectors/base.py`)

`_is_likely_intentional_style()` returns `True` when:

- `emotional_density >= 0.5`
- `purpose_hint` is `"reflection"` or `"bridge"`
- `primary_jobs` includes `reinforce_theme`, `deliver_reflection`, `deepen_character`, or `build_setup`

Used to **skip** flagging:

- Repetition in chapters with high emotional density
- Possible bloat in atmospheric/literary chapters
- Exposition overload in quiet emotional scenes
- Weak midpoint in reflective/thematic chapters
- Repeated emotional beat when thematic

### 3. Detector-Specific Hardening

**General**

- Repetition: uses threshold, skips if intentional style
- Thin section: flexible threshold 120 words
- Possible bloat: flexible threshold 6500, skips if intentional
- Repeated concepts: flexible requires 5+ (guided: 3)

**Fiction**

- Exposition overload: min 1200 words, skips if intentional, tension threshold 0.22 (flexible)
- Weak midpoint: skips if intentional (reflective/thematic)
- Repeated emotional beat: skips if intentional

**Memoir**

- Repeated reflection: threshold 5 (flexible) vs 3 (guided)
- Emotional over-explanation: threshold 25 (flexible) vs 15 (guided)

**Nonfiction**

- Missing example: skips contemplative chapters (reflect, consider, meaning) in flexible
- Intro/outro: threshold 2500 (flexible) vs 1500 (guided)

**Workbook**

- Excessive explanation: threshold 8 (flexible) vs 5 (guided)
- Missing exercise: skips short reflection pages (<600 words with reflect/journal) in flexible

### 4. Chapter Drag Analyzer

- Accepts `guidance_mode` and `project_type`
- `_drag_threshold()`: memoir 0.80, fiction+flexible 0.78, flexible 0.70, guided 0.60
- Higher threshold = more tolerant of slow pacing

### 5. Trim-vs-Strengthen Engine

- Added `emotional_density` from `density_by_chapter`
- **keep_as_intentional** preferred when:
  - `(has_intentional_job and purpose_clarity >= 0.6) or emotional_density >= 0.5`
  - For exposition_overload, possible_bloat, excessive_explanation
- **bloated_intro_or_outro**: prefers keep_as_intentional when `has_intentional_job or emotional_density >= 0.4`

### 6. Density Map Enhancements

- `_assess_emotional_density`: added markers (reflecting, looking back, meaning, silence, quiet)
- `_infer_section_purpose`: returns `"reflection"` when reflective markers present

## Test Coverage

See `apps/api/tests/test_density_hardening.py`:

- Mode-aware tolerance (flexible vs guided)
- Intentional style detection
- Freeform mode (only GeneralDetector)
- Trim engine keep_as_intentional for reflective passages
- Workbook reflection pages
- Nonfiction contemplative chapters
- Constants defined

## Trust-Improvement Notes

1. **Flexible mode** is the default for density; it applies higher thresholds and more intentional-style checks.
2. **Freeform mode** runs only GeneralDensityDetector; project-specific detectors are suppressed.
3. **Memoir** and **literary fiction** receive the highest drag tolerance.
4. **Mark as intentional** is surfaced as a first-class alternative in the trim engine for reflective/emotional passages.
5. Writers can always override; the engine suggests, it does not enforce.
