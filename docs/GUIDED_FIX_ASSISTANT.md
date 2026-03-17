# Guided Fix Assistant

The Story Integrity Engine provides guided fix suggestions for every detected issue.

## For Each Issue

1. **Plain-English explanation** — What the issue is
2. **Why it matters** — Impact on reader or manuscript quality
3. **Where it appears** — Chapter, section, or location hint
4. **Practical fix suggestions** — Actionable steps
5. **Optional actions** — Resolve, mark as intentional, ignore

## Fix Templates

| Issue type | Key suggestion |
|------------|----------------|
| empty_section | Add content or remove if intentionally empty |
| placeholder_heavy | Expand or merge with adjacent chapter |
| unresolved_placeholder | Replace TODO/TBD with actual content |
| weak_opening | Strengthen inciting incident or hook |
| weak_ending | Add resolution, tie loose ends |
| missing_transition | Add bridging paragraph |
| reflection_missing | Add present perspective or meaning |

## API

`GET /api/v1/projects/{id}/books/{id}/integrity/issues/{id}/guidance` returns:

```json
{
  "explanation": "...",
  "why_it_matters": "...",
  "suggestions": ["...", "..."],
  "fix_suggestions": [{"action": "...", "label": "..."}]
}
```

## User Actions

- **Resolve** — Mark as fixed; clears from open list
- **Mark intentional** — Writer chose to keep as-is
- **Ignore** — Dismiss without resolving
- **Go to chapter** — Navigate to affected chapter
