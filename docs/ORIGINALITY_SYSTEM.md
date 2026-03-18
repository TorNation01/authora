# AUTHORA Originality & Integrity Review System

## Overview

The originality and integrity review system helps users, educators, writers, and reviewers assess originality, detect likely similarity against available corpora, and review AI-assisted text responsibly.

**Important product rule:** This system is **not** presented as an infallible detector or as equivalent to third-party institutional integrity platforms (e.g., Turnitin, iThenticate) unless such an external provider is actually licensed and integrated.

## Core Capabilities

1. **Similarity / Originality Review** – Compare text against user-owned projects, internal corpora, course libraries, and connected reference content
2. **AI-Assistance Transparency** – Track and disclose where AI was used in content creation
3. **AI-Origin Risk Review** – Probabilistic, review-aid-only assessment with confidence bands
4. **Matched-Passage Reporting** – Highlight exact overlap regions and paraphrase-like similarity
5. **Educator / Reviewer Workflow** – Review queues, comments, "needs human review" flags

## Design Principles

- **Human review is central** – All results are review aids; no automatic punitive decisions
- **Uncertainty is explicit** – Confidence bands and disclaimers are always shown
- **Privacy preserved** – User data is handled according to configurable retention rules
- **No false certainty** – Never claim perfect plagiarism or AI detection

## System Components

| Component | Purpose |
|-----------|---------|
| Similarity Engine | N-gram fingerprinting for internal comparison |
| Comparison Corpus Manager | Configure and manage corpora (user projects, uploaded, course, reference) |
| Matched Passage Viewer | Side-by-side source comparison |
| Originality Report UI | Summary, matched passages, AI-assistance trace, AI-origin risk |
| AI-Assistance Disclosure | Track and display AI-generated or AI-assisted sections |
| AI-Origin Risk Review | Probabilistic risk bands (low/medium/high) |
| Reviewer Workflow | Review queues, comments, exportable reports |
| Admin Controls | Corpora, exclusions, feature flags, privacy/retention |

## Excluded Sections

The system supports excluding configured ranges from similarity comparison:

- Bibliography
- Quotes (properly attributed)
- Front matter (title, acknowledgments, etc.)
- Custom excluded ranges (e.g., boilerplate, templates)

## Report Outputs

- Originality/similarity summary
- Matched-source view
- Matched-passage view
- Excluded-content settings
- AI-assistance trace summary
- AI-origin risk summary
- Exportable review report

## Related Documentation

- [SIMILARITY_ENGINE.md](./SIMILARITY_ENGINE.md) – Technical details of the similarity algorithm
- [AI_ASSISTANCE_TRANSPARENCY.md](./AI_ASSISTANCE_TRANSPARENCY.md) – AI-assistance tracking
- [AI_ORIGIN_REVIEW.md](./AI_ORIGIN_REVIEW.md) – AI-origin risk review
- [EDUCATOR_REVIEW_WORKFLOWS.md](./EDUCATOR_REVIEW_WORKFLOWS.md) – Educator and reviewer workflows
