# Manuscript Compile Engine

The compile engine assembles manuscript content for export with full control over inclusion, order, and exclusions.

## Compile Types

| Type | Description |
|------|-------------|
| `full` | Full manuscript – all chapters, front/back matter |
| `chapter_only` | Chapters only, no front/back matter |
| `partial` | Selected chapters only |
| `review_copy` | Includes comments and revision marks |
| `submission_copy` | Clean, no notes, excludes unfinished |
| `working_draft` | Full draft with notes for internal use |

## Compile Options

### Content Inclusion

- `include_title_page` – Title page
- `include_toc` – Table of contents
- `include_headings` – Chapter/section headings
- `include_section_titles` – Section titles within chapters
- `exclude_notes_comments` – Strip comments from export
- `exclude_highlights` – Strip highlights
- `exclude_revision_marks` – Strip revision marks

### Chapter Selection

- `chapter_ids` – IDs of chapters to include (null = all)
- `include_archived` – Include archived (deleted_at) chapters
- `include_unfinished` – Include outline/placeholder chapters
- `chapter_order` – Custom sort order by sort_order values

### Section Selection

- `include_sections` – Include chapter sections
- `section_ids` – IDs of sections to include
- `include_archived_sections` – Include archived sections

### Front/Back Matter

- `front_matter_blocks` – Ordered list of `{kind, title, content, sort_order}`
- `back_matter_blocks` – Ordered list of `{kind, title, content, sort_order}`

## Compile Flow

1. Filter chapters by `chapter_ids`, `include_archived`, `include_unfinished`
2. Strip annotations (comments, highlights, revision marks) if `exclude_*` is true
3. Apply custom `chapter_order` if provided
4. Build front matter from `front_matter_blocks`
5. Build back matter from `back_matter_blocks`
6. Return `(chapters_for_export, CompileResult)`

## CompileResult

- `chapters` – List of `CompiledChapter` (included/excluded, word count, reason)
- `total_words` – Total word count
- `total_pages_estimate` – ~250 words/page
- `front_matter_text` – Rendered front matter
- `back_matter_text` – Rendered back matter
- `toc_entries` – TOC entries
- `warnings` – Empty chapters, etc.
- `structure_preview` – Ordered structure for preview

## API

Compile preview: `POST /api/v1/export/books/{book_id}/compile-preview`

Request body:

```json
{
  "compile_type": "full",
  "chapter_ids": null,
  "include_archived": false,
  "include_unfinished": true,
  "exclude_notes_comments": true,
  "exclude_highlights": true,
  "exclude_revision_marks": true
}
```

## Service Usage

```python
from authora.services.compile_engine import compile_manuscript, CompileOptions, CompileType

chapters_data = [{"id": "...", "title": "...", "content": {...}, "sort_order": 0, ...}]
opts = CompileOptions(compile_type=CompileType.SUBMISSION_COPY)
opts.apply_preset("submission_copy")

chapters_for_export, result = compile_manuscript(
    chapters_data, opts,
    book_title="My Book",
    author_name="Author")
```
