"""AI provider abstraction."""

from authora.infrastructure.ai_provider.base import AIProvider
from authora.infrastructure.ai_provider.factory import get_ai_provider

__all__ = ["AIProvider", "get_ai_provider"]
