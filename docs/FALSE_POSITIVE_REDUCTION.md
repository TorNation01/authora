# False Positive Reduction

Concrete changes made to reduce false positives in the Story Integrity Engine.

## Placeholder Detection

| Before | After | Rationale |
|--------|-------|-----------|
| `"..."` | Excluded | Ellipsis is valid in prose |
| `"?"` | Excluded | Rhetorical questions |

| Marker | Before | After |
|--------|--------|-------|
| `TODO` | ✓ | ✓ |
| `TBD` | ✓ | ✓ |
| `[placeholder]` | ✓ | ✓ |
| `[insert` | ✓ | ✓ |
| `XXX` | ✓ | ✓ |
| `...` | ✓ | ✗ |
| `?` | ✓ | ✗ |
| `[` | ✓ | ✗ |

## Word Count Thresholds

### Chapter analyzer

| Issue | Before | After (guided) | After (flexible) |
|-------|--------|---------------|------------------|
| chapter_underwritten | < 50 | < 40 | < 40 |
| chapter_placeholder_heavy | < 100 | < 80 | < 80 |
| chapter_overlong | > 5000 | > 6000 | > 6000 |
| chapter_emotionally_flat | > 200 words | > 400 words | > 400 words |
| chapter_weak_opening | > 100 words | > 150 words | > 150 words |

### Fiction detector

| Issue | Before | After (guided) | After (flexible) |
|-------|--------|---------------|------------------|
| weak_opening | < 200 | < 200 | < 150 |
| weak_ending | < 150 | < 150 | < 100 |

### General detector

| Issue | Before | After |
|-------|--------|-------|
| placeholder_heavy | < 50 | < 40 (guided), < 50 (flexible) |

## Suppression Thresholds

### Fiction detector

| Issue | Before | After (guided) | After (flexible) |
|-------|--------|----------------|------------------|
| character_single_appearance | total > 3 | total > 5 | Suppressed |
| too_many_threads | threads > 8, ch < 20 | threads > 10, ch < 15 | Suppressed |
| pacing_trough | 3+ trough, 5+ ch | 4+ trough, 8+ ch | Suppressed |
| theme_introduced_not_developed | total > 4 | total > 6 | Suppressed |

### Memoir detector

| Issue | Before | After |
|-------|--------|-------|
| reflection_missing | > 300 words | > 300 (guided), suppressed (flexible) |

### Nonfiction detector

| Issue | Before | After |
|-------|--------|-------|
| missing_transition | > 200 words, no markers | > 200 (guided), suppressed (flexible) |
| weak_chapter_length | < 100 | < 100 (guided), < 80 (flexible) |

### Workbook detector

| Issue | Before | After |
|-------|--------|-------|
| exercise_missing | > 200 words | > 200 (guided), suppressed (flexible) |

## Score Thresholds (Chapter Analyzer)

| Dimension | Before | After (guided) | After (flexible) |
|-----------|--------|----------------|------------------|
| purpose_clarity | 0.4 | 0.4 | 0.35 |
| pacing | 0.4 | 0.4 | 0.35 |
| opening_strength | 0.4 | 0.4 | 0.35 |
| closing_strength | 0.4 | 0.4 | 0.35 |
| transition_quality | 0.4 | 0.4 | 0.35 |
| emotional_movement | 0.4 | 0.4 | 0.35 |
| repetition | > 0.6 | > 0.6 | > 0.7 |

## Freeform Mode

- **Detectors**: Only GeneralDetector.
- **GeneralDetector**: Only empty_section and unresolved_placeholder (strong markers).
- **Chapter analyzer**: Only chapter_underwritten for < 30 words.

## Confidence Caps

| Mode | Speculative issues |
|------|--------------------|
| Guided | 0.6–0.8 (unchanged) |
| Flexible | ≤ 0.6 |
| Freeform | ≤ 0.4 (for any that slip through) |
