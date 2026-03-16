# AI Context Retrieval (RAG)

How AI uses retrieved context for better assistance.

## Flow

1. User runs an AI action (e.g. "Improve wording") with selection or context
2. Selection/context is used as a RAG query (truncated to 500 chars)
3. Semantic search retrieves top-k relevant chunks from the project
4. Chunks are appended to workspace context as "RELEVANT CONTEXT FROM YOUR PROJECT"
5. AI generates with full context (fiction/nonfiction + retrieved chunks)

## Use Cases

- **Rewrite with chapter context**: Retrieve related passages from other chapters
- **Continue writing**: Use outline and recent chapters
- **Terminology consistency**: Find where terms were used before
- **Tone/voice**: Retrieve passages that match desired style

## Limits

- **rag_max_chunks**: Default 5 chunks (configurable)
- **Truncation**: Each chunk excerpt limited to 800 chars in context
- **Project-scoped**: Only chunks from the current project

## Privacy

- Retrieved context stays within the project
- No cross-project or cross-user leakage
- Ownership enforced via `project_id` and `user_id`
