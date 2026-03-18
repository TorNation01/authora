# Poetry Template Library

## Overview

12 poetry templates expand AUTHORA's creative writing support for poets. Each includes structure, prompts, guidance text, AI hooks, export suggestions, and project-type-appropriate modules.

## Template List

| Slug | Name | Purpose |
|------|------|---------|
| `poetry-single` | Single Poem Drafting | Draft and revise a single poem |
| `poetry-free-verse` | Free Verse | Unmetered, unrhymed. Line breaks, image, sound |
| `poetry-sonnet` | Sonnet | 14 lines. Petrarchan or Shakespearean. Volta |
| `poetry-haiku` | Haiku / Short Form | 5-7-5 or variants. Moment. Seasonal |
| `poetry-spoken-word` | Spoken Word / Performance | Written for the ear. Pace, rhythm, punch |
| `poetry-lyric` | Lyric Poem | First-person. Musical. Concentrated feeling |
| `poetry-narrative` | Narrative Poem | Tells a story in verse |
| `poetry-thematic-collection` | Thematic Poetry Collection | Organize by theme. Flow, sequence |
| `poetry-chapbook` | Chapbook | Short collection (20–40 pages). Cohesive |
| `poetry-revision` | Poetry Revision | Structured revision. Line breaks, word choice |
| `poetry-ekphrastic` | Ekphrastic Poem | Poem in response to art |
| `poetry-devotional` | Devotional / Meditative Poetry | Spiritual, contemplative |

## Parent Template

All poetry templates are children of `poetry` (Poetry Collection), which provides the base category and collection workflow.

## Planning Sections

**Single poems:** Subject/Trigger, Tone & Voice, Form Notes, Draft, Revision Notes

**Collections:** Collection Theme, Poem List, Section Grouping, Sequence Planning, Revision Tracking

## AI Prompt Hooks

| Hook | Purpose |
|------|---------|
| `imagery` | Strengthen imagery in a passage |
| `rhythm` | Feedback on rhythm and line breaks |
| `word_choice` | Suggest alternatives that maintain tone |
| `feedback` | Feedback on imagery and rhythm |

## Export Recommendations

- DOCX
- PDF
- EPUB

## Chapter/Section Skeletons

- **Single poem:** Draft → Revision 1 → Revision 2 → Final
- **Free verse:** Subject & Trigger → Draft → Line Breaks → Revision
- **Sonnet:** Volta → Quatrain 1–3 → Couplet
- **Haiku:** Moment → Line 1 (5) → Line 2 (7) → Line 3 (5) → Variants
- **Spoken word:** Performance Notes → Draft → Punch Lines → Revision
- **Chapbook:** Opening Poem → Poems 2–9 → Closing Poem

## Visibility

Templates are visible in the template library under category `poetry`. Searchable and previewable via `GET /api/v1/templates?category=poetry`.
