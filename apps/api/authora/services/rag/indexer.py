"""RAG indexing service - embed and store chunks."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from authora.models import ContentEmbedding, IndexingJob
from authora.services.embedding_service import embed_batch, get_embedding_provider
from authora.services.rag.chunker import Chunk


async def delete_embeddings_for_source(
    db: AsyncSession,
    source_type: str,
    source_id: uuid.UUID,
) -> int:
    """Delete all embeddings for a source. Returns count deleted."""
    result = await db.execute(
        delete(ContentEmbedding).where(
            ContentEmbedding.source_type == source_type,
            ContentEmbedding.source_id == source_id,
        )
    )
    return result.rowcount or 0


async def index_chunks(
    db: AsyncSession,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    chunks: list[Chunk],
    book_id: uuid.UUID | None = None,
) -> int:
    """Embed and store chunks. Returns count indexed."""
    provider = get_embedding_provider()
    if not provider:
        return 0
    if not chunks:
        return 0
    texts = [c.text for c in chunks]
    vectors = await provider.embed_batch(texts)
    if not vectors or len(vectors) != len(chunks):
        return 0
    model_name = getattr(provider, "model", "embedding")
    def _to_uuid(v):
        if v is None:
            return None
        if isinstance(v, uuid.UUID):
            return v
        try:
            return uuid.UUID(str(v))
        except (ValueError, TypeError):
            return None

    for i, (chunk, vec) in enumerate(zip(chunks, vectors)):
        ce = ContentEmbedding(
            project_id=project_id,
            user_id=user_id,
            source_type=chunk.source_type,
            source_id=_to_uuid(chunk.source_id) or uuid.uuid4(),
            book_id=_to_uuid(chunk.metadata.get("book_id")) or book_id,
            chapter_id=_to_uuid(chunk.metadata.get("chapter_id")),
            chunk_index=chunk.chunk_index,
            content_text=chunk.text,
            chunk_metadata=chunk.metadata,
            embedding_model=model_name,
            embedding=vec,
        )
        db.add(ce)
    await db.flush()
    return len(chunks)


async def reindex_source(
    db: AsyncSession,
    source_type: str,
    source_id: uuid.UUID,
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    chunks: list[Chunk],
    book_id: uuid.UUID | None = None,
) -> int:
    """Delete existing and reindex. Returns count indexed."""
    await delete_embeddings_for_source(db, source_type, source_id)
    return await index_chunks(db, user_id, project_id, chunks, book_id)
