# Ollama Hardware Tiers

AUTHORA classifies server hardware into four tiers to automatically choose safe, sensible default Ollama models. Each tier has recommended model-role mappings and RAG context limits.

## Tier Summary

| Tier | Label | Typical intent |
|------|-------|----------------|
| 1 | Light local inference | Modest server, prioritize responsiveness and stability, smaller models only |
| 2 | Balanced local inference | Strong general-purpose server, good day-to-day writing, balanced quality and speed |
| 3 | Strong local inference | High-memory/VRAM server, higher-quality drafting, heavier workloads acceptable |
| 4 | Premium local inference | Very strong server, large model usage acceptable, premium drafting prioritized |

## Detection

- **Configured**: Set `OLLAMA_HARDWARE_TIER=1|2|3|4` to override auto-detection.
- **Auto-detected**: Uses RAM (and VRAM via `nvidia-smi` when available) to classify.
  - Tier 1: &lt; 12 GB effective (RAM or VRAM)
  - Tier 2: 12–24 GB
  - Tier 3: 24–48 GB
  - Tier 4: ≥ 48 GB

## Recommended Default Mappings by Tier

### Tier 1: Light

| Role | Model |
|------|-------|
| quick_assist_model | qwen3:4b |
| default_writing_model | qwen3:4b |
| premium_drafting_model | qwen3:8b |
| fiction_ideation_model | qwen3:8b |
| nonfiction_structure_model | qwen3:8b |
| editing_polish_model | qwen3:4b |
| embeddings_model | qwen3-embedding:0.6b or qwen3-embedding:4b |
| optional_vision_model | disabled (uses default text model) |

### Tier 2: Balanced

| Role | Model |
|------|-------|
| quick_assist_model | qwen3:4b |
| default_writing_model | qwen3:8b |
| premium_drafting_model | qwen3:14b |
| fiction_ideation_model | qwen3:8b or qwen3:14b |
| nonfiction_structure_model | qwen3:8b or qwen3:14b |
| editing_polish_model | qwen3:8b |
| embeddings_model | qwen3-embedding:4b or mxbai-embed-large |
| optional_vision_model | disabled |

### Tier 3: Strong

| Role | Model |
|------|-------|
| quick_assist_model | qwen3:4b |
| default_writing_model | qwen3:8b |
| premium_drafting_model | qwen3:14b or qwen3:30b |
| fiction_ideation_model | qwen3:14b or qwen3:30b |
| nonfiction_structure_model | qwen3:14b or qwen3:30b |
| editing_polish_model | qwen3:8b or qwen3:14b |
| embeddings_model | qwen3-embedding:4b, qwen3-embedding:8b, or mxbai-embed-large |
| optional_vision_model | qwen3-vl:8b |

### Tier 4: Premium

| Role | Model |
|------|-------|
| quick_assist_model | qwen3:4b |
| default_writing_model | qwen3:8b or qwen3:14b |
| premium_drafting_model | qwen3:30b or qwen3:32b |
| fiction_ideation_model | qwen3:14b, qwen3:30b, or qwen3:32b |
| nonfiction_structure_model | qwen3:14b, qwen3:30b, or qwen3:32b |
| editing_polish_model | qwen3:14b |
| embeddings_model | qwen3-embedding:8b or mxbai-embed-large |
| optional_vision_model | qwen3-vl:8b (if installed) |

## RAG Limits by Tier

| Tier | rag_max_chunks | rag_chunk_size | rag_chunk_overlap |
|------|----------------|---------------|------------------|
| 1 | 3 | 600 | 80 |
| 2 | 5 | 800 | 100 |
| 3 | 7 | 1000 | 120 |
| 4 | 10 | 1200 | 150 |

## Manual Override

Admin overrides (DB or env) always take precedence over tier-based defaults. Use `OLLAMA_MODEL_QUICK_ASSIST`, etc., or the Admin → AI → Model role mapping UI.

## See Also

- [AI_HARDWARE_AUTOMAP.md](AI_HARDWARE_AUTOMAP.md) — Auto-selection and fallback behavior
- [OLLAMA_MODEL_ROLE_MAP.md](OLLAMA_MODEL_ROLE_MAP.md) — Role definitions
- [SERVER_SIZING_AND_MODEL_SELECTION.md](SERVER_SIZING_AND_MODEL_SELECTION.md) — Server sizing
