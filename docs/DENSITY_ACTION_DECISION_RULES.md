# Density Action Decision Rules

Rules used by the Trim-vs-Strengthen Engine to recommend actions.

## Repetition

| Condition | Action | Confidence |
|-----------|--------|------------|
| repetition_in_chapter OR (category=repetition AND heat=high/very_high) | compress | 0.85 |
| repeated_concepts, repeated_reflection, repeated_emotional_beat OR (repetition + has_related) | compress | 0.8 |

**Rationale**: Repeated content with little new movement → compress. State the point once clearly.

## Transitions

| Condition | Action | Confidence |
|-----------|--------|------------|
| thin_transition OR category=weak_transition | bridge | 0.8 |

**Rationale**: Chapter opens abruptly after major scene → add bridging paragraph or beat.

## Thin Support

| Condition | Action | Confidence |
|-----------|--------|------------|
| thin_section AND purpose_clarity < 0.4 | expand | 0.75 |
| thin_section | expand | 0.7 |

**Rationale**: Very short section → expand or merge. If purpose unclear, expand to develop.

## Practical Support Gaps

| Condition | Action | Confidence |
|-----------|--------|------------|
| missing_example, missing_exercise OR category=practical_support_gap | strengthen | 0.85 |

**Rationale**: Concept without example or exercise → add practical support.

## Bloat and Over-Explanation

| Condition | Action | Confidence |
|-----------|--------|------------|
| reinforce_theme in jobs AND purpose_clarity ≥ 0.7 | keep_as_intentional | 0.6 |
| exposition_overload, possible_bloat, excessive_explanation AND is_dragging | trim | 0.8 |
| exposition_overload, possible_bloat, excessive_explanation | compress | 0.75 |

**Rationale**: Literary reflective passage with strong theme → consider keeping. Long + dragging → trim. Long + low tension → compress.

## Payoffs and Midpoints

| Condition | Action | Confidence |
|-----------|--------|------------|
| weak_midpoint OR category=underweighted_payoff | strengthen | 0.75 |
| category=rushed_moment | strengthen | 0.8 |

**Rationale**: Reveal lands too fast → strengthen with setup, consequence, or emotional weight.

## Merge Candidates

| Condition | Action | Confidence |
|-----------|--------|------------|
| has_related AND (repetition OR instructional_redundancy) | merge | 0.7 |

**Rationale**: Two similar sections → merge into one.

## Intro/Outro

| Condition | Action | Confidence |
|-----------|--------|------------|
| bloated_intro_or_outro | trim | 0.8 |

**Rationale**: Intro/outro chapters often benefit from trimming to essentials.

## Fallback

| Condition | Action | Confidence |
|-----------|--------|------------|
| No rule matched | current_action (from detector) | 0.65 |

**Rationale**: Use detector's action_category; provide alternatives for user to consider.

## Examples (from spec)

- Repeated internal thought with little new movement → **compress**
- Reveal lands too fast → **strengthen**
- Chapter opens abruptly after major scene → **bridge**
- Two similar explanation sections → **merge**
- Literary reflective passage with strong theme value → **keep as intentional**
- Workbook explanation block with no exercise support → **strengthen** with practical action
