# Chapter Drag Analyzer

The Chapter Drag Analyzer detects consecutive sections/chapters that drag — low movement for their size — and identifies merge and compression candidates.

## What Is "Drag"?

A chapter drags when it has:

- **Low movement** — Few plot/narrative advancement markers
- **Low information density** — Long sentences, repetitive structure, or thin content
- **High word count** — Especially in the middle third of the manuscript

## Drag Score

- **0–1** — Higher = more drag
- Formula: `(1 - movement) * 0.4 + (1 - info_density) * 0.3` plus penalties for length and midpoint position
- **is_dragging** — True when drag_score > 0.6

## Outputs

### Drag Runs

Consecutive chapters (2+) that are all dragging. Suggestion: "Consider trimming or tightening these consecutive chapters."

### Merge Candidates

Pairs of consecutive short chapters (< 800 words each, combined < 2500) with thematic overlap. Suggestion: "These short chapters may work better merged."

### Compression Candidates

Chapters that are long (> 2500 words), have low information density (< 0.55), and high drag. Suggestion: "This chapter may benefit from compression."

### Chapter Drag Scores

Per-chapter: word_count, movement, information_density, drag_score, is_dragging.

## API

- Chapter drag data is in `density_map_snapshot` after a scan
- `GET /density/analysis` returns `chapter_drag_analysis` with drag_runs, merge_candidates, compression_candidates, chapter_drag_scores
- `GET /density/chapters/{id}/summary` returns `where_this_chapter_is_dragging` for the active chapter

## UI

- **Chapter Drag Panel** — Tab in Story Density panel showing drag runs, merge candidates, and per-chapter drag status
- **"Where this chapter is dragging"** — Quick action/summary when a dragging chapter is selected
