# Context Assembly

Intelligent context assembly for AI prompts.

## Principles

- **Do not overload** — Use summaries when full content is too long
- **Prioritize relevance** — Selection and recent context first
- **Distinguish creative vs factual** — Research/source content clearly marked
- **Source-linked research** — Retrieved chunks labeled with source type

## Context Sections

| Section | Max chars | When included |
|---------|-----------|---------------|
| User instruction | 2000 | When user provides custom instruction |
| Selected text | 4000 | When user selects text |
| Workspace context | 6000 | Fiction/nonfiction/general workspace |
| RAG chunks | 4000 total | When embeddings enabled, rag_query provided |
| Project metadata | Compact | Guidance mode, template |
| Style preferences | Compact | When set |

## Workspace Context

- **Fiction**: `build_fiction_context()` — premise, genre, characters, recent chapter
- **Nonfiction**: `build_nonfiction_context()` — topic, structure, recent section
- **General**: Last ~2000 chars of current chapter

## RAG Integration

When `rag_query` and embeddings are configured:

1. `semantic_search(project_id, query, ...)` retrieves relevant chunks
2. Chunks are truncated to 800 chars each
3. Each chunk labeled with `[source_type]` (e.g. [note], [chapter])
4. Total RAG context capped at 4000 chars

## API

```python
from authora.services.ai_context_assembly import assemble_context

context = await assemble_context(
    db,
    selection="...",
    book_id=...,
    book_type=BookType.FICTION,
    chapter_id=...,
    project_id=...,
    user_id=...,
    rag_query="...",
    include_recent_chapter=True,
    include_workspace=True,
    include_rag=True,
    guidance_mode="guided",
    template_slug="novel",
    style_preferences={"voice": "literary"},
    user_instruction="Make it more suspenseful",
)
```
