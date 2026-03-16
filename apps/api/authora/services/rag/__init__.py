"""RAG services - chunking, indexing, search."""

from authora.services.rag.chunker import Chunk, chunk_chapter, chunk_chapter_brief, chunk_note, chunk_outline
from authora.services.rag.indexer import delete_embeddings_for_source, index_chunks, reindex_source
from authora.services.rag.search import SearchResult, semantic_search

__all__ = [
    "Chunk",
    "chunk_chapter",
    "chunk_chapter_brief",
    "chunk_note",
    "chunk_outline",
    "delete_embeddings_for_source",
    "index_chunks",
    "reindex_source",
    "SearchResult",
    "semantic_search",
]
