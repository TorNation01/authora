# Repetition Health

The Repetition Health subsystem analyzes repetition across the manuscript with per-chapter heat indicators and repeated point detection.

## Metrics

### In-Chapter Repetition

- **0–1** — Fraction of words that are repeated within the same chapter (common words weighted)
- High score = many repeated phrases or ideas within one chapter

### Cross-Chapter Overlap

- **0–1** — Fraction of chapter's distinct words that appear in other chapters
- High score = chapter reuses phrasing from elsewhere in the manuscript

### Repetition Heat

- **0–1** — Combined score: `in_chapter * 0.6 + cross_chapter * 0.4`
- **Heat level** — low, moderate, high, very_high

### Manuscript Repetition Score

- **0–100** — Inverse of average heat; higher = less repetition (healthier)
- `100 - avg_heat * 60`

## Repeated Points

- Phrases (3-word sequences) that appear in 2+ chapters
- Each point includes: phrase, occurrences, chapter_indices

## API

- Repetition data is in `density_map_snapshot` after a scan
- `GET /density/analysis` returns `repetition_analysis` with chapter_repetition_heat, repeated_points, manuscript_repetition_score
- `GET /density/chapters/{id}/summary` returns `which_parts_feel_repetitive` for the active chapter

## UI

- **Repetition Heat Panel** — Tab in Story Density panel with:
  - Manuscript repetition score
  - Per-chapter heat indicators (colored blocks: darker = more repetition)
  - Per-chapter heat level and percentage
  - List of repeated phrases
- **"Which parts feel repetitive"** — Quick action when a high-heat chapter is selected
