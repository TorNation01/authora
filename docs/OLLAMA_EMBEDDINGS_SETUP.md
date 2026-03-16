# Ollama Embeddings Setup

Ollama provides local embeddings for AUTHORA's semantic search and RAG.

## Prerequisites

- Ollama installed (same as for chat)
- Embedding model pulled: `ollama pull nomic-embed-text`

## Configuration

| Env | Default | Description |
|-----|---------|-------------|
| `EMBEDDINGS_ENABLED` | `false` | Set to `true` to enable |
| `EMBEDDINGS_PROVIDER` | `ollama` | Embedding provider |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Model for embeddings |
| `OLLAMA_EMBEDDING_BASE_URL` | (uses `OLLAMA_BASE_URL`) | Override for embeddings |

## Example

```env
EMBEDDINGS_ENABLED=true
EMBEDDINGS_PROVIDER=ollama
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

## Server Deployment

- Ollama runs on the AUTHORA server (or a reachable host)
- Remote users access AUTHORA in the browser
- **No Ollama on client devices** — embeddings run server-side

## Health Check

```
GET /api/v1/admin/ai/embeddings/ollama/health
```

## List Embedding Models

```
GET /api/v1/admin/ai/embeddings/ollama/models
```

Common models: `nomic-embed-text`, `bge-m3`, `mxbai-embed`.
