# Filler False Positive Reduction

This document details how the Story Density Engine reduces false positives when distinguishing true filler from intentional prose.

## Problem

Heuristic-based density analysis can misclassify:

- **Refrains and motifs** as repetition
- **Quiet emotional scenes** as exposition overload
- **Atmospheric worldbuilding** as bloat
- **Layered reflection** as repeated reflection
- **Intentional pacing** as chapter drag
- **Contemplative passages** as missing support

## Strategy

### 1. Raise Thresholds in Flexible Mode

| Issue Type | Guided | Flexible | Rationale |
|------------|--------|----------|-----------|
| Repetition score | 0.30 | 0.38 | Refrains, motifs need higher repeat density |
| Thin section | 80 words | 120 words | Brief bridges common in literary fiction |
| Bloat | 5000 words | 6500 words | Fantasy, literary can be long |
| Repeated concepts | 3+ | 5+ | Cross-chapter repetition needs more evidence |
| Memoir reflection | 3+ | 5+ | Poetic memoir uses layered reflection |
| Memoir emotion | 15+ | 25+ | Authentic memoir voice is emotional |
| Intro/outro | 1500 | 2500 | Contemplative nonfiction |
| Workbook explanation | 5+ | 8+ | Setup before exercise can be intentional |

### 2. Intentional Style Gate

Before flagging, the engine checks `_is_likely_intentional_style()`:

- **Emotional density ≥ 0.5** – passage carries emotional weight
- **Purpose hint "reflection"** – inferred from reflective markers
- **Primary jobs** – reinforce_theme, deliver_reflection, deepen_character, build_setup

If true, the detector **skips** creating the issue. This prevents:

- Flagging repetition in a chapter that is deliberately building theme
- Flagging exposition overload in a quiet emotional scene
- Flagging possible bloat in atmospheric fantasy
- Flagging weak midpoint in a reflective chapter
- Flagging repeated emotional beat when it's a deliberate refrain

### 3. Project-Type Awareness

- **Memoir**: Highest drag threshold (0.80), highest reflection/emotion counts
- **Fiction + flexible**: Literary threshold (0.78) for drag
- **Nonfiction**: Contemplative markers (reflect, consider, meaning) skip missing_example
- **Workbook**: Short reflection pages (<600 words + reflect/journal) skip missing_exercise

### 4. Exposition Overload Specifics

Previously: 800+ words, tension < 0.3, movement < 0.3 → flag.

Now:

- **Min words**: 1200 (avoids flagging shorter reflective scenes)
- **Tension threshold**: 0.22 in flexible (stricter – need lower tension to flag)
- **Intentional gate**: Skip if emotional density high or intentional jobs present

### 5. Trim Engine: Prefer keep_as_intentional

When the trim-vs-strengthen engine evaluates exposition_overload, possible_bloat, excessive_explanation, or bloated_intro_or_outro:

- If `(has_intentional_job and purpose_clarity >= 0.6) or emotional_density >= 0.5` → recommend **keep_as_intentional**
- If `has_intentional_job or emotional_density >= 0.4` for intro/outro → recommend **keep_as_intentional**

This surfaces "Mark as intentional" as the primary suggestion for reflective, thematic, or emotional passages instead of trim/compress.

## Scenarios Covered

| Scenario | Overreach Before | Reduction |
|----------|------------------|-----------|
| Literary fiction, quiet reflective scene | exposition_overload | Intentional gate + higher word min |
| Slow-burn romance | chapter drag | Literary drag threshold 0.78 |
| Poetic memoir | repeated_reflection, emotional_over_explanation | Higher counts, intentional gate |
| Intentionally fragmented structure | thin_section | Flexible threshold 120 |
| Atmospheric fantasy worldbuilding | possible_bloat | Intentional gate, 6500 word threshold |
| Contemplative nonfiction | missing_example, bloated_intro | Contemplative skip, 2500 intro |
| Workbook reflection pages | missing_exercise | Short + reflect/journal skip |
| Minimalist vs expansive prose | Various | Mode-aware thresholds, intentional gate |
| Chapter slow but thematically necessary | exposition_overload, drag | reinforce_theme → keep_as_intentional |

## Verification

Run: `pytest apps/api/tests/test_density_hardening.py -v`

Key tests:

- `test_flexible_memoir_reflection_tolerance`
- `test_workbook_flexible_skips_short_reflection_page`
- `test_nonfiction_flexible_skips_contemplative_chapter`
- `test_trim_engine_prefers_keep_intentional_for_reflective`
