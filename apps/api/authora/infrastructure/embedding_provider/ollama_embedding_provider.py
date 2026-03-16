"""Ollama embedding provider - local embeddings via /api/embed."""

import httpx


class OllamaEmbeddingProvider:
    """Ollama embeddings via /api/embed."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._dimension = 768  # nomic-embed-text default

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def dimension(self) -> int:
        return self._dimension

    async def embed(self, text: str) -> list[float]:
        """Embed a single text."""
        vectors = await self.embed_batch([text])
        return vectors[0] if vectors else []

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts via Ollama /api/embed."""
        if not texts:
            return []
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": texts if len(texts) > 1 else texts[0]},
            )
            resp.raise_for_status()
            data = resp.json()
            embeddings = data.get("embeddings", [])
            if not embeddings:
                return []
            if isinstance(embeddings[0], (int, float)):
                return [embeddings]
            return embeddings

    async def health_check(self) -> tuple[bool, str]:
        """Check Ollama connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    return True, "Ollama is reachable"
                return False, f"Ollama returned {resp.status_code}"
        except httpx.ConnectError as e:
            return False, f"Cannot connect to Ollama: {e}"
        except Exception as e:
            return False, str(e)

    async def list_embedding_models(self) -> list[dict]:
        """List Ollama models that support embeddings (heuristic: check /api/tags)."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            models = data.get("models", [])
            # Common embedding model names
            embed_names = ("nomic-embed", "embed", "bge-m3", "mxbai-embed")
            return [
                m for m in models
                if any(n in (m.get("name") or "").lower() for n in embed_names)
            ]
