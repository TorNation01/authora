# Trim / Compress / Strengthen Assistant

The fix assistant provides guided suggestions for each density issue type.

## API

```
GET /api/v1/projects/{id}/books/{id}/density/issues/{issue_id}/guidance
```

Returns:
- `explanation` — Plain-English description of the issue
- `why_it_matters` — Why addressing it helps
- `suggestions` — General repair suggestions (list of strings)
- `fix_suggestions` — Issue-specific actions (e.g. compress, mark_intentional)

## Fix Templates by Issue Type

| Issue Type | Suggested Actions |
|------------|-------------------|
| repetition_in_chapter | Compress repeated points; mark as intentional |
| thin_section | Expand or merge; mark as intentional |
| possible_bloat | Trim; compress exposition; mark as intentional |
| thin_transition | Add bridge paragraph; mark as intentional |
| repeated_concepts | Consolidate; mark as intentional |
| weak_midpoint | Add midpoint beat; mark as intentional |
| exposition_overload | Trim; convert to scene; mark as intentional |
| repeated_emotional_beat | Vary or deepen; mark as intentional |
| missing_example | Add example; mark as intentional |
| bloated_intro_or_outro | Trim; mark as intentional |
| repeated_reflection | Consolidate; deepen; mark as intentional |
| emotional_over_explanation | Trim; trust reader; mark as intentional |
| excessive_explanation | Trim; move to appendix; mark as intentional |
| missing_exercise | Add prompt; mark as intentional |

## User Actions

- **Resolve** — User addressed the issue
- **Intentional** — User chose to keep as-is
- **Ignore** — User deferred

No auto-delete or auto-rewrite. All assistance is guided only.
