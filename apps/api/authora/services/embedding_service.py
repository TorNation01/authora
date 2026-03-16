"""Embedding service - provider abstraction, health checks."""

from authora.config import get_settings


def get_embedding_provider():
    """Get configured embedding provider. Returns None if disabled."""
    s = get_settings()
    if not s.embeddings_enabled:
        return None
    ollama_ok = s.ollama_enabled or bool(s.ollama_embedding_base_url)
    if s.embeddings_provider == "ollama" and ollama_ok:
        from authora.infrastructure.embedding_provider.ollama_embedding_provider import (
            OllamaEmbeddingProvider,
        )
        base_url = s.ollama_embedding_base_url or s.ollama_base_url
        return OllamaEmbeddingProvider(
            base_url=base_url,
            model=s.ollama_embedding_model,
        )
    return None


def is_embeddings_configured() -> bool:
    """Check if embeddings are configured and enabled."""
    return get_embedding_provider() is not None


async def embed_text(text: str) -> list[float] | None:
    """Embed a single text. Returns None if not configured."""
    provider = get_embedding_provider()
    if not provider:
        return None
    return await provider.embed(text)


async def embed_batch(texts: list[str]) -> list[list[float]] | None:
    """Embed multiple texts. Returns None if not configured."""
    provider = get_embedding_provider()
    if not provider:
        return None
    return await provider.embed_batch(texts)
