# Similarity Engine

## Purpose

The similarity engine compares text against available corpora to identify likely overlap and paraphrase-like similarity. It is **not** a substitute for institutional plagiarism detection. Results are review aids only; human review is central.

## Algorithm

### N-Gram Fingerprinting

- **N-gram size:** 5 characters (configurable)
- **Normalization:** Lowercase, collapse whitespace, remove punctuation
- **Similarity metric:** Jaccard similarity of n-gram sets

### Comparison Flow

1. **Extract plain text** from TipTap chapters via `tiptap_to_plain_text`
2. **Compare** each query chapter against corpus chapters
3. **Skip** same chapter (self-comparison)
4. **Apply** minimum similarity threshold (default 0.5)
5. **Find overlap regions** using sliding window (min length 20 chars)
6. **Classify** match type: `exact` (sim > 0.9) or `paraphrase_like`

### Overlap Regions

- Sliding window over normalized query text
- Matches found in corpus text
- Returns `(query_start, query_end, matched_substring)` for each region

### Overall Similarity

- Sum of matched character spans / total query characters
- Capped at 100%

## Corpora Types

| Type | Description |
|------|-------------|
| `user_projects` | User-owned projects where permitted |
| `uploaded` | Internal uploaded corpora |
| `course` | Course/class libraries |
| `reference` | Connected source/reference content |

## Excluded Ranges

- Bibliography, quotes, front matter
- Configurable excluded ranges via admin
- Excluded sections are not included in similarity computation

## Limitations

- **Internal-only:** No comparison against external web or institutional databases
- **No perfect detection:** Paraphrasing and semantic similarity may be missed
- **Language:** Optimized for English; normalization may affect other languages
- **Short text:** Minimum match length (20 chars) limits sensitivity for very short passages

## API Usage

- `POST /api/v1/projects/{project_id}/books/{book_id}/originality/scan` – Run scan
- `GET /api/v1/projects/{project_id}/books/{book_id}/originality/scans/{scan_id}/passages` – Get matched passages

## Configuration

- `min_similarity` – Request body parameter (default 0.5)
- `excluded_ranges` – Request body parameter (list of range configs)
- `corpus_ids` – Request body parameter (optional; omit for default corpus)
