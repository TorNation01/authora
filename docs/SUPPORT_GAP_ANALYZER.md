# Support Gap Analyzer

The Story Density Engine includes weak-support detection so it does not over-encourage cutting when the real issue is missing depth.

## Thin-Support Issues

Detectors flag where material is **too thin** rather than too bloated:

- **thin_section** — Very short chapter (expand or merge)
- **thin_transition** — Weak bridge from previous chapter (add bridge paragraph)
- **missing_example** — Concept without example (non-fiction)
- **missing_exercise** — Concept without exercise (workbook)

## Under-Support Patterns (Future Enhancement)

Planned detection for:

- Emotional moment lacks support
- Reveal lacks setup weight
- Conflict escalation too brief
- Concept explanation too thin
- Practical takeaway missing
- Relationship beat too compressed
- Lesson lands too quickly
- Ending resolves too abruptly

## Balance

The engine recommends both:

- **Trim/compress** — For clutter, filler, repetition
- **Strengthen/expand/bridge** — For thin support, rushed moments, weak transitions

Users can mark issues as **intentional** when the choice is deliberate.
