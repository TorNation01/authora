# Structure Health

Structure Health is the structural dimension of the Story Integrity Engine. It evaluates how well the manuscript is organized at the chapter and scene level.

## Dimensions

### Chapter-Level

- **Purpose clarity** — Each chapter has a clear role
- **Pacing** — Appropriate length and rhythm
- **Transitions** — Smooth flow between chapters
- **Openings and closings** — Strong hooks and satisfying endings
- **Linkage** — Chapters connect to the main thread and each other

### Manuscript-Level

- **Overall arc** — Setup, development, climax, resolution
- **Pacing curve** — Avoids long flat sections or rushed endings
- **Emotional progression** — Movement across the manuscript
- **Plot progression** — Steady advancement without stalls

## Health Indicators

| Indicator | Meaning |
|-----------|---------|
| **Strong** | Structure is clear and effective |
| **Stable** | Solid with minor improvements possible |
| **Needs support** | Several structural areas need attention |
| **Weak** | Multiple structural issues |
| **Critical** | Significant structural problems |

## Chapter Comparison View

The Chapter Health panel includes a comparison view that shows:

- Per-chapter health level
- Key scores (pacing, tension, emotion, opening)
- Side-by-side or list comparison for quick identification of weak chapters

## "Why This Chapter Feels Off" Analysis

When a chapter is not strong or stable, the analyzer generates an explanation that may include:

- Unclear purpose
- Pacing concerns (too slow or rushed)
- Weak opening or closing
- Poor transition from previous chapter
- Repetition diluting impact
- Very short or very long length

## Integration

- Structure health is computed by `chapter_analyzer.analyze_chapters()`
- Stored in `story_map_snapshot.chapter_health`
- Chapter-level issues are converted to `IntegrityIssue` records (category: `structure`)
- Displayed in Story Health panel (Issues tab) and Chapter Health tab
