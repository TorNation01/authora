# Chapter Purpose Tracker

The Chapter Purpose Tracker infers and tracks what each chapter is intended to accomplish within the manuscript.

## Purpose Hints

From the story map and content analysis, chapters are assigned purpose hints:

| Hint | Meaning |
|------|---------|
| `opening` | First chapter; sets up story and reader expectations |
| `ending` | Final chapter; brings narrative to resolution |
| `body` | Middle chapter; advances the narrative |
| `short_section` | Bridge or transition section |
| `placeholder_or_empty` | Empty or placeholder content |

## How Purpose Is Used

- **Purpose clarity score** — Higher when purpose hint is clear and content matches (e.g., opening/ending with sufficient word count)
- **"What this chapter is doing"** — Summary generated from purpose hint and position
- **Health computation** — Unclear purpose contributes to lower health

## Data Sources

- `story_map.chapter_purposes` — Per-chapter purpose hints from planner or inference
- Chapter index and total chapter count
- Word count and content length

## Example Outputs

- *"Opening chapter (1,200 words). Sets up the story and reader expectations."*
- *"Body chapter (800 words). Advances the narrative."*
- *"Closing chapter (1,500 words). Brings the narrative to resolution."*
- *"This chapter is empty or placeholder content."*

## Integration

- Purpose data is built in `story_map.build_story_map()`
- Consumed by `chapter_analyzer._assess_purpose_clarity()` and `_summarize_what_chapter_is_doing()`
- Displayed in the Chapter Health panel under "What this chapter is doing"
