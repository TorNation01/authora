# Trim-vs-Strengthen Decision Engine

The Trim-vs-Strengthen Decision Engine helps writers decide whether a weak section should be cut, compressed, expanded, bridged, clarified, or left alone.

## Actions

| Action | Description |
|--------|-------------|
| trim | Cut redundant or low-value material |
| compress | Tighten without cutting; state once clearly |
| strengthen | Add support, consequence, or depth |
| expand | Add more content to develop the idea |
| bridge | Add transition or connective material |
| merge | Combine with another section |
| clarify | Make purpose or meaning clearer |
| keep_as_intentional | Leave as-is; mark as deliberate |

## Outputs

For each detected density issue, the engine returns:

- **recommended_action** — Best likely action
- **confidence** — 0–1 score for how confident the recommendation is
- **explanation** — Plain-English rationale
- **alternatives** — Other viable actions with "when to consider"
- **revision_task_suggestion** — Suggested title for a revision checklist item

## Signals Used

- **Section purpose clarity** — From scene purpose analyzer
- **Narrative/instructional value** — Primary jobs (move_plot, explain_concept, etc.)
- **Repeated content** — Repetition heat, cross-chapter overlap
- **Emotional weight** — Emotional contribution, thematic reinforcement
- **Payoff importance** — Underweighted payoff, weak midpoint
- **Transition quality** — Thin transition, abrupt opening
- **Uniqueness of material** — Reinforce_theme, deliberate refrain
- **Project mode** — fiction, nonfiction, memoir, workbook, hybrid
- **Guidance mode** — guided, flexible, freeform
- **Chapter role** — Opening, midpoint, ending, body
- **Related sections** — Whether merge is possible

## API

- `GET /density/issues/{id}/guidance` — Returns guidance with recommended_action, confidence, alternatives when context is available
- `GET /density/issues/{id}/decision` — Full decision (recommended_action, confidence, explanation, alternatives, revision_task_suggestion)
- `GET /density/issues/{id}/alternatives` — Compare alternative repair paths
- `POST /density/issues/{id}/create-revision-task` — Create a revision checklist item from the recommendation

## Create Revision Task

- **Body**: `revision_pass_id` (optional), `title` (optional override)
- If `revision_pass_id` is omitted, creates a new "Density cleanup" custom revision pass
- Uses `revision_task_suggestion` from the decision as the checklist item title unless overridden

## Mode Behaviour

- **Freeform** — Lower confidence; suggests detected action but emphasises user choice
- **Flexible** — Standard rules with softer assumptions
- **Guided** — Stronger rules, framework-aware when available
