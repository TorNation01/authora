# Server Sizing and Model Selection

Guidance for sizing AUTHORA servers and choosing Ollama models based on hardware capacity.

## Hardware Tier Guidelines

| Tier | RAM (min) | VRAM (GPU) | Use case |
|------|-----------|------------|----------|
| 1 | 8 GB | — | Light, responsive, small models only |
| 2 | 16 GB | 8 GB | Balanced quality and speed |
| 3 | 32 GB | 16 GB | Strong drafting, ideation |
| 4 | 48 GB+ | 24 GB+ | Premium, large models |

## Model Size vs. Hardware

| Model family | Approx. size | RAM/VRAM needed |
|--------------|--------------|-----------------|
| qwen3:4b | ~2.5 GB | 4 GB |
| qwen3:8b | ~5 GB | 8 GB |
| qwen3:14b | ~8 GB | 12 GB |
| qwen3:30b | ~18 GB | 24 GB |
| qwen3:32b | ~20 GB | 24 GB |
| qwen3-embedding:0.6b | ~0.5 GB | 1 GB |
| qwen3-embedding:4b | ~2.5 GB | 4 GB |
| qwen3-embedding:8b | ~5 GB | 8 GB |
| qwen3-vl:8b | ~5 GB | 8 GB |

## Recommendations

- **Small VPS (4–8 GB RAM)**: Tier 1, qwen3:4b for most roles.
- **General server (16 GB RAM)**: Tier 2, mix of 4b and 8b models.
- **Dedicated server (32 GB RAM)**: Tier 3, 8b–14b for drafting.
- **GPU server (24 GB VRAM)**: Tier 3 or 4, 14b–30b for premium drafting.

## Warnings

- **Oversized models** — Admin UI may show warnings when selected models are likely too large for the detected tier.
- **Stability** — Tier 1 defaults are chosen to keep the system stable on lower-resource hardware.
- **Context length** — Larger models consume more memory for long context; RAG limits are tighter on lower tiers.

## See Also

- [OLLAMA_HARDWARE_TIERS.md](OLLAMA_HARDWARE_TIERS.md) — Tier definitions
- [OLLAMA_PERFORMANCE_TUNING.md](OLLAMA_PERFORMANCE_TUNING.md) — Performance tuning
- [OLLAMA_SETUP.md](OLLAMA_SETUP.md) — Installing Ollama
