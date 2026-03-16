# RAG Architecture in AUTHORA

Retrieval-Augmented Generation (RAG) and semantic search in AUTHORA.

## Overview

AUTHORA uses RAG to make AI assistance more context-aware by retrieving relevant project content before generating output. Semantic search lets users find content by meaning, not just keywords.

## Components

| Component | Purpose |
|-----------|---------|
| **Embedding provider** | Converts text to vectors (Ollama now, OpenAI future) |
| **Content embeddings** | Vector storage (pgvector) with project isolation |
| **Chunker** | Splits long documents into overlapping chunks |
| **Indexer** | Embeds chunks and stores in `content_embeddings` |
| **Search service** | Cosine similarity search within a project |
| **RAG integration** | Injects retrieved chunks into AI workspace context |

## Data Flow

1. **Indexing**: Notes, chapters, briefs, outlines → chunked → embedded → stored
2. **Search**: User query → embedded → similarity search → ranked results
3. **RAG**: AI action (selection/context) → embedded → retrieve top-k chunks → append to workspace context → AI generates

## Project Isolation

- All embeddings are scoped by `project_id`
- Search and RAG only return chunks from the user's project
- No cross-project leakage

## Vector Storage

- **Table**: `content_embeddings`
- **Extension**: pgvector
- **Dimension**: 768 (nomic-embed-text)
- **Index**: IVFFlat for cosine similarity

## Configuration

| Env | Purpose |
|-----|---------|
| `EMBEDDINGS_ENABLED` | Enable embeddings |
| `EMBEDDINGS_PROVIDER` | ollama \| openai (future) |
| `OLLAMA_EMBEDDING_MODEL` | nomic-embed-text |
| `OLLAMA_EMBEDDING_BASE_URL` | Ollama URL for embeddings |
| `RAG_MAX_CHUNKS` | Max chunks to inject (default 5) |
| `RAG_CHUNK_SIZE` | Chunk size in chars (default 800) |
| `RAG_CHUNK_OVERLAP` | Overlap between chunks (default 100) |
