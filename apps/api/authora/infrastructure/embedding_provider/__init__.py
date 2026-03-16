"""Embedding providers."""

from authora.infrastructure.embedding_provider.base import EmbeddingProvider
from authora.infrastructure.embedding_provider.ollama_embedding_provider import (
    OllamaEmbeddingProvider,
)

__all__ = ["EmbeddingProvider", "OllamaEmbeddingProvider"]
