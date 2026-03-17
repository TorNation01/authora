# Pacing Analyzer

The Pacing Analyzer evaluates chapter-level pacing to help writers identify slow, rushed, or uneven sections.

## What It Measures

- **Word count** — Per-chapter length
- **Pacing hint** — From story map: `normal`, `very_short`, `very_long`, `slow_opening`, `rushed_ending`
- **Position in manuscript** — Opening, middle, or closing third
- **Relative length** — Compared to adjacent chapters and manuscript average

## Pacing Scores (0–1)

- **High (≥ 0.7)** — Pacing feels appropriate for the chapter's position
- **Medium (0.5–0.7)** — Minor pacing concerns
- **Low (< 0.5)** — Pacing may feel off (too slow or too rushed)

## Heuristics

| Condition | Effect |
|-----------|--------|
| `very_short` | Low pacing score |
| `very_long` | Moderate pacing score (may need trimming) |
| `slow_opening` in first third | Lower score |
| `rushed_ending` in last third | Lower score |
| Normal length, middle chapters | Higher score |

## Pacing Heatmap (Later-Ready)

A pacing heatmap is planned to visualize:

- Per-chapter pacing scores
- Word-count distribution across the manuscript
- Visual identification of slow or rushed sections

The Chapter Health panel includes a placeholder for this feature. Implementation will map chapter index to a color gradient (e.g., green = good, amber = needs attention, red = problematic).

## Integration

- Pacing data comes from `story_map.pacing_by_chapter`
- Used by `chapter_analyzer.analyze_chapters()` to compute `pacing` score
- Exposed in chapter health API and Chapter Health panel
