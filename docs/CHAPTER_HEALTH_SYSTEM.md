# Chapter Health System

The Chapter Health System is part of the AUTHORA Story Integrity Engine. It helps writers see which chapters are strong, weak, slow, overloaded, disconnected, repetitive, or structurally unclear.

## Overview

For each chapter, the system analyzes:

- **Purpose clarity** — How clear is the chapter's role in the manuscript?
- **Relationship to manuscript** — How connected is it to characters, themes, and the main thread?
- **Tension level** — Stakes and conflict markers
- **Emotional movement** — Character reflection and emotional beats
- **Plot movement** — Narrative advancement
- **Information density** — Balance of content (avoid overload or thinness)
- **Pacing** — Appropriateness of length and rhythm
- **Transition quality** — Link to previous chapter
- **Opening strength** — Hook and first-paragraph impact
- **Closing strength** — Punch and transition to next chapter
- **Chapter linkage** — Connection to adjacent chapters
- **Repetition** — Redundant phrasing or repeated ideas
- **Unresolved internal** — Placeholders, TODOs, incomplete content

## Chapter Health Levels

| Level | Meaning |
|-------|---------|
| **Strong** | Well-structured, purposeful, no significant issues |
| **Stable** | Solid with minor room for improvement |
| **Needs support** | Several areas could be strengthened |
| **Weak** | Multiple structural issues need attention |
| **Critical** | Significant structural problems |

## Chapter-Level Issues Detected

- `chapter_lacks_clear_purpose` — Chapter's role is unclear
- `chapter_repeats_prior_content` — Possible redundancy
- `chapter_stalls_momentum` — Pacing may stall the story
- `chapter_overlong` — Consider splitting or trimming
- `chapter_ends_without_effective_transition` — Weak bridge to next chapter
- `chapter_emotionally_flat` — Lacks emotional beats
- `chapter_disconnected_from_main_thread` — Feels disconnected
- `chapter_placeholder_heavy` — Little content; expand or merge
- `chapter_underwritten` — Very short; add content or remove
- `chapter_weak_opening` — Opening could hook more strongly

## Outputs

- **What this chapter is doing** — Short summary of the chapter's role
- **Why this chapter feels off** — Analysis when health is not strong/stable
- **Suggested fixes** — Actionable recommendations
- **Issues** — Specific detected problems with suggestions

## Integration

- Chapter health is computed during each integrity scan
- Stored in `story_map_snapshot.chapter_health`
- Exposed via `GET /api/v1/projects/{id}/books/{id}/integrity/chapter-health`
- Displayed in the Story Health panel under the "Chapter Health" tab

## See Also

- [PACING_ANALYZER.md](./PACING_ANALYZER.md) — Pacing analysis details
- [CHAPTER_PURPOSE_TRACKER.md](./CHAPTER_PURPOSE_TRACKER.md) — Purpose tracking
- [STRUCTURE_HEALTH.md](./STRUCTURE_HEALTH.md) — Overall structure health
