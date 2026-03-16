# Ollama Performance Tuning

Tuning recommendations for Ollama-based local AI in AUTHORA.

## Hardware Tier Selection

- Set `OLLAMA_HARDWARE_TIER=1|2|3|4` to match your server if auto-detection is wrong.
- Use Tier 1 (light) for modest servers.
- Use Tier 4 (premium) only when you have sufficient RAM/VRAM.

## RAG Context Limits

RAG limits are tier-aware:

| Tier | Max chunks | Chunk size | Overlap |
|------|------------|------------|---------|
| 1 | 3 | 600 | 80 |
| 2 | 5 | 800 | 100 |
| 3 | 7 | 1000 | 120 |
| 4 | 10 | 1200 | 150 |

Lower tiers use smaller context to reduce memory and latency.

## Model Selection

- **Quick assist** — Keep qwen3:4b for low latency.
- **Drafting** — Use larger models (14b, 30b) only when hardware supports them.
- **Embeddings** — qwen3-embedding:0.6b or 4b for lighter loads; 8b for higher quality when resources allow.
- **Vision** — Enable only when needed and when qwen3-vl:8b (or equivalent) is installed.

## Ollama Context Length

- Ollama models have context limits (e.g. 8K, 32K tokens).
- Larger context increases memory use.
- For long documents, consider smaller models or chunking.

## Fallback

- When preferred models are missing, AUTHORA falls back to smaller models.
- Ensure at least qwen3:4b (or llama3.2) is installed for reliable fallback.

## See Also

- [OLLAMA_HARDWARE_TIERS.md](OLLAMA_HARDWARE_TIERS.md) — Tier definitions
- [AI_HARDWARE_AUTOMAP.md](AI_HARDWARE_AUTOMAP.md) — Auto-selection and fallback
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md) — Installing Ollama
