# RAG Architecture Summary

## 1. How RAG Works in AUTHORA

AUTHORA uses Retrieval-Augmented Generation to make AI assistance more context-aware:

- **Indexing**: Notes, chapters, outlines, and chapter briefs are chunked, embedded via Ollama, and stored in PostgreSQL with pgvector.
- **Retrieval**: When a user runs an AI action (e.g. rewrite, expand), the selection or context is used as a semantic query. Top-k relevant chunks are retrieved from the project.
- **Augmentation**: Retrieved chunks are appended to the workspace context (fiction/nonfiction metadata, characters, etc.) before the AI generates.
- **Generation**: The AI model receives the enriched context and produces more consistent, relevant output.

## 2. How Ollama Embeddings Are Used

- **Provider**: `OllamaEmbeddingProvider` calls Ollama `/api/embed` with `nomic-embed-text` (or configured model).
- **Flow**: Text → Ollama API → 768-dim vector
- **Storage**: Vectors stored in `content_embeddings.embedding` (pgvector)
- **Search**: Query embedded → cosine similarity (`<=>`) → ranked results

## 3. How Multiple Embedding Models Can Be Selected

- **Config**: `OLLAMA_EMBEDDING_MODEL` (default `nomic-embed-text`)
- **Admin**: `GET /api/v1/admin/ai/embeddings/ollama/models` lists available embedding models
- **Future**: `EMBEDDINGS_PROVIDER` supports `ollama` now; `openai` can be added without major rewrite

## 4. How Semantic Search Works for Users

- **UI**: Project → Search → enter query → results with source labels (note, chapter, outline, brief)
- **API**: `GET /api/v1/projects/{id}/rag/search?q=...&book_id=...&source_types=...`
- **Reindex**: Users click "Reindex project" to refresh the index after adding/changing content

## 5. How AI Uses Retrieved Context

- **Trigger**: `build_workspace_context()` receives `rag_query` (selection or context) when provided
- **Retrieval**: `semantic_search()` returns top `rag_max_chunks` (default 5)
- **Injection**: Chunks appended as "RELEVANT CONTEXT FROM YOUR PROJECT" in the system prompt
- **Scope**: Project-only; no cross-project leakage

## 6. Server-Hosted Deployment

- **Ollama** runs on the same server as AUTHORA or another reachable host
- **Remote users** access AUTHORA in the browser; no local install required
- **Embeddings** run server-side; all vector operations happen on the API server
- **Confirmation**: Server-hosted deployment does **not** require Ollama on every client device
