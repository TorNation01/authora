# AUTHORA Comment Tags

Comment tags provide structured review signals for feedback on manuscript content. Tags help authors and collaborators filter, prioritise, and act on feedback efficiently.

## Available Tags

| Tag | Value | Use case |
|-----|-------|----------|
| **Clarity** | `clarity` | Unclear phrasing, confusing passages |
| **Rewrite** | `rewrite` | Suggestion to rewrite or rephrase |
| **Pacing** | `pacing` | Pacing issues, too fast/slow |
| **Continuity** | `continuity` | Plot, timeline, or consistency issues |
| **Tone** | `tone` | Tone or voice concerns |
| **Emotion** | `emotion` | Emotional impact notes |
| **Grammar** | `grammar` | Grammar corrections |
| **Proofing** | `proofing` | Proofreading, typo, or style notes |
| **Fact check** | `fact_check` | Factual accuracy to verify |
| **Question** | `question` | Question for the author |
| **Approval** | `approval` | Approval note or sign-off |
| **Change request** | `change_request` | Explicit request for change |
| **Idea** | `idea` | Suggestion or idea |
| **Client request** | `client_request` | Client-specified feedback |
| **Beta feedback** | `beta_feedback` | General beta reader feedback |
| **General** | `general` | General comment |
| **Other** | `other` | Other or uncategorised |

## Legacy Tags (backwards compatible)

For backward compatibility, the following legacy tags are also accepted:

- `rewrite_suggestion`
- `clarity_issue`
- `pacing_note`
- `grammar_spelling`
- `consistency`
- `character_voice`
- `plot_continuity`

## Usage

### API

- **Create**: Set `comment_type` when creating a comment.
- **Update**: Update `comment_type` to change the tag (author only).
- **Filter**: Use `?comment_type=clarity` (or `?tag=clarity`) when listing comments.

### Filtering

Comments can be filtered by tag when listing:

```
GET /api/v1/projects/{id}/books/{book_id}/chapters/{chapter_id}/comments?comment_type=clarity
```

## See Also

- [REVIEW_SIGNAL_SYSTEM.md](REVIEW_SIGNAL_SYSTEM.md) – Status and workflow
- [COLLABORATION_SYSTEM.md](COLLABORATION_SYSTEM.md) – Collaboration overview
