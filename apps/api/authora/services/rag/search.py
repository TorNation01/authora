"""Semantic search for RAG."""

import uuid
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from authora.services.embedding_service import embed_text, get_embedding_provider


@dataclass
class SearchResult:
    """A semantic search result."""

    source_type: str
    source_id: str
    book_id: str | None
    chapter_id: str | None
    content_text: str
    chunk_index: int
    score: float
    metadata: dict


async def semantic_search(
    db: AsyncSession,
    project_id: uuid.UUID,
    query: str,
    *,
    user_id: uuid.UUID | None = None,
    book_id: uuid.UUID | None = None,
    source_types: list[str] | None = None,
    limit: int = 5,
) -> list[SearchResult]:
    """Semantic search within a project. Returns ranked results."""
    provider = get_embedding_provider()
    if not provider:
        return []
    query_vec = await provider.embed(query)
    if not query_vec:
        return []
    vec_str = "[" + ",".join(str(x) for x in query_vec) + "]"
    source_filter = ""
    if source_types:
        placeholders = ", ".join(f"'{t}'" for t in source_types)
        source_filter = f" AND source_type IN ({placeholders})"
    book_filter = " AND book_id = :book_id" if book_id else ""
    sql = f"""
        SELECT id, source_type, source_id, book_id, chapter_id, content_text, chunk_index, metadata AS chunk_metadata,
               1 - (embedding <=> :vec::vector) AS score
        FROM content_embeddings
        WHERE project_id = :project_id AND embedding IS NOT NULL
        {source_filter}
        {book_filter}
        ORDER BY embedding <=> :vec::vector
        LIMIT :limit
    """
    params = {
        "vec": vec_str,
        "project_id": str(project_id),
        "limit": limit,
    }
    if book_id:
        params["book_id"] = str(book_id)
    result = await db.execute(text(sql), params)
    rows = result.fetchall()
    return [
        SearchResult(
            source_type=r[1],
            source_id=str(r[2]),
            book_id=str(r[3]) if r[3] else None,
            chapter_id=str(r[4]) if r[4] else None,
            content_text=r[5] or "",
            chunk_index=r[6] or 0,
            score=float(r[7]) if r[7] is not None else 0.0,
            metadata=r[8] if isinstance(r[8], dict) else {},
        )
        for r in rows
    ]
