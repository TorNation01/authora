# AI-Origin Risk Review

## Purpose

Provide a **probabilistic, review-aid-only** assessment of AI-origin risk. This is **not** an AI detector. It does not claim perfect detection. Results are review aids; human review is required.

## Design Principles

- **Probabilistic only** – No certainty; confidence bands and uncertainty are always shown
- **Review aid only** – Never sole proof of misconduct
- **Human review central** – All results require human review
- **No punitive automation** – Never used for automatic punitive decisions

## Signals

1. **content_source** – `user_written`, `ai_assisted`, `ai_generated` per chapter
2. **AIActionLog count** – Number of AI actions in the project/book

## Risk Bands

| Band | Criteria | Confidence Interval |
|------|----------|---------------------|
| `low` | Less AI-generated/assisted content | 0.5–0.75 |
| `medium` | Moderate AI involvement | 0.6–0.85 |
| `high` | High AI involvement | 0.6–0.9 |

## Output

- `risk_band` – low, medium, or high
- `confidence_low`, `confidence_high` – Confidence interval
- `signals_summary` – AI-generated %, AI-assisted %, user-written %, AI action count
- `disclaimer` – Always included: "This is a review aid only. It does not constitute proof of misconduct. Human review is required. Results have inherent uncertainty."

## API

- `GET /api/v1/projects/{project_id}/books/{book_id}/originality/ai-origin-risk` – Get risk review

## Limitations

- Based on internal metadata (content_source, AIActionLog) only
- Does not analyze text for AI-like patterns
- Not a substitute for external AI detection tools
- Should never be used as sole evidence of misconduct
