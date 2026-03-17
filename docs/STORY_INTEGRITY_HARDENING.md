# Story Integrity Engine Hardening

This document describes the hardening pass applied to the AUTHORA Story Integrity Engine to reduce false positives, formulaic bias, and improve trustworthiness.

## Goals

- **Avoid over-policing creative choices** — Literary fiction, experimental structure, and genre conventions vary widely.
- **Avoid punishing unconventional structure** — Fragmented memoir, nonlinear timeline, and delayed reveals are valid.
- **Avoid treating all open questions as errors** — Intentionally unresolved endings and series open threads are deliberate.
- **Avoid genre rigidity** — Flexible and freeform projects should not be held to strict genre templates.
- **Reduce noisy or low-value warnings** — Raise the bar for speculative issues.
- **Improve explanation quality** — Clearer, less prescriptive language.
- **Improve confidence scoring** — Lower confidence for speculative issues; higher for clear gaps.

## Mode-Aware Behavior

| Mode | Behavior |
|------|----------|
| **Guided** | Full detection; standard thresholds; all type-specific detectors run. |
| **Flexible** | Softer thresholds; speculative issues suppressed or downgraded; "mark as intentional" emphasized. |
| **Freeform** | Only GeneralDetector runs; only empty chapters and strong placeholders flagged; chapter analyzer minimal. |

## Scenario Coverage

### Literary fiction with subtle payoff

- **Overreach**: Weak opening/ending flagged for short, spare chapters.
- **Fix**: Flexible uses lower word thresholds (150 opening, 100 ending); guided offers "mark as intentional" for spare openings.

### Intentionally unresolved ending

- **Overreach**: weak_ending as high severity; "tie loose ends" prescriptive.
- **Fix**: Severity reduced in flexible; fix_suggestions include "Mark as intentional (open/unresolved ending)".

### Fragmented memoir structure

- **Overreach**: reflection_missing for immersive, present-tense chapters.
- **Fix**: Flexible suppresses reflection_missing; guided adds "mark as intentional (immersive/fragmentary style)".

### Hybrid genre project

- **Overreach**: Multiple detectors with conflicting expectations.
- **Fix**: Hybrid uses Nonfiction + Memoir detectors; each is mode-aware.

### Nonlinear timeline used deliberately

- **Overreach**: chapter_disconnected_from_main_thread for non-chronological chapters.
- **Fix**: Flexible uses softer transition threshold; higher bar for flagging.

### Poetic or symbolic prose

- **Overreach**: emotionally_flat for prose without explicit emotion markers.
- **Fix**: Chapter analyzer raises word threshold for emotional_flat (400 vs 200); flexible uses 0.35 threshold.

### Workbook with unconventional module sequence

- **Overreach**: exercise_missing for every chapter.
- **Fix**: Flexible suppresses; guided adds "mark as intentional (unconventional module design)"; higher word threshold (300).

### Series book leaving intentional open threads

- **Overreach**: too_many_threads, theme_introduced_not_developed.
- **Fix**: Stricter thresholds (10+ threads, 15+ chapters); flexible suppresses; "mark as intentional (series/open threads)".

### Thriller with delayed reveal structure

- **Overreach**: pacing_trough for slow build.
- **Fix**: Requires 4+ trough chapters and 8+ total; flexible suppresses.

### Romance with slow-burn pacing

- **Overreach**: pacing_trough, pacing_trough.
- **Fix**: Same as thriller; "mark as intentional (slow-burn/deliberate pace)".

## Placeholder Detection

- **Before**: `"..."`, `"?"`, `"["` triggered unresolved_placeholder (ellipsis, rhetorical questions, citations).
- **After**: Only strong markers: `TODO`, `TBD`, `[placeholder]`, `[insert]`, `[xxx]`, `xxx`.

## Confidence Scoring

- **Speculative issues** (weak_ending, character_single_appearance, theme_introduced_not_developed, etc.): confidence capped at 0.6 in flexible, 0.4 in freeform.
- **Clear structural gaps** (empty_section, unresolved_placeholder): confidence 0.9+.

## "Mark as Intentional" Support

- **Every speculative issue** now includes a fix_suggestion: `{"action": "mark_intentional", "label": "..."}`.
- **Context-specific labels** (e.g., "open/unresolved ending", "slow-burn/deliberate pace", "spare opening is deliberate").

## Test Coverage

See `apps/api/tests/test_integrity_hardening.py` for:

- Placeholder false-positive avoidance
- Freeform mode suppression
- Flexible mode softer thresholds
- Guided mode "mark as intentional" presence
- Chapter analyzer mode-aware behavior
- Confidence scoring for speculative issues

## Related Docs

- [FALSE_POSITIVE_REDUCTION.md](./FALSE_POSITIVE_REDUCTION.md) — Specific reductions and thresholds
- [CREATIVE_FREEDOM_SAFEGUARDS.md](./CREATIVE_FREEDOM_SAFEGUARDS.md) — User-facing safeguards
