# Indexing and Reindexing

How content is indexed for semantic search and when to reindex.

## Indexed Content

| Source | When indexed |
|--------|--------------|
| Notes | On create/update (future) or manual reindex |
| Chapters | On create/update (future) or manual reindex |
| Chapter briefs | Manual reindex |
| Outline chapters | Manual reindex |

## Chunking Strategy

- **Chunk size**: 800 chars (configurable via `RAG_CHUNK_SIZE`)
- **Overlap**: 100 chars (`RAG_CHUNK_OVERLAP`)
- **Boundaries**: Prefer paragraph, then sentence breaks

## Reindexing

**Manual**: POST `/api/v1/projects/{id}/rag/reindex` or click "Reindex project" in the search UI.

**Behavior**:
1. Deletes existing embeddings for the project's content
2. Re-chunks notes, chapters, briefs, outlines
3. Embeds each chunk via Ollama
4. Stores in `content_embeddings`

## Partial Reindex (Future)

On save of a note or chapter, delete embeddings for that source and reindex. Not yet implemented; use full project reindex.

## Index Health

- Admin → AI providers shows embeddings status
- Failed indexing: check Ollama connectivity and model availability
