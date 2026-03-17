# Clutter and Filler Detection

The Story Density Engine detects clutter and filler across project types.

## General Detection

- **repetition_in_chapter** — High word/phrase repetition within a chapter (compress)
- **thin_section** — Very short middle chapter (expand or merge)
- **possible_bloat** — Long chapter with low information density (trim)
- **thin_transition** — Chapter with weak linkage from previous (bridge)
- **repeated_concepts** — Same phrases/concepts across multiple chapters (compress)

## Fiction

- **weak_midpoint** — Midpoint chapters without clear beat or turn
- **exposition_overload** — Long passages with little tension or movement
- **repeated_emotional_beat** — Same emotional beat repeated without progression

## Non-Fiction

- **missing_example** — Concept introduced without concrete example
- **bloated_intro_or_outro** — Overlong introduction or conclusion

## Memoir

- **repeated_reflection** — Multiple similar reflections without deeper meaning
- **emotional_over_explanation** — Over-explaining emotion where action could show it

## Workbook / Guided Book

- **excessive_explanation** — Too much explanation before exercises
- **missing_exercise** — Concept without reflection or exercise prompt

## Issue Categories

- clutter, filler, repetition, drag, over_explanation
- thin_support, rushed_moment, weak_transition, bloated_scene
- underweighted_payoff, instructional_redundancy, practical_support_gap

## Action Categories

- trim, compress, strengthen, expand, bridge, clarify, merge, keep_as_intentional
