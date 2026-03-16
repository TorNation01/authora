# Hardware-Tier-Aware AI Model Selection — Summary

## 1. Hardware Tier Summary

| Tier | Label | RAM/VRAM | Intent |
|------|-------|----------|--------|
| 1 | Light local inference | &lt; 12 GB | Modest server, responsiveness, smaller models |
| 2 | Balanced local inference | 12–24 GB | General-purpose, balanced quality/speed |
| 3 | Strong local inference | 24–48 GB | High-memory, heavier drafting |
| 4 | Premium local inference | ≥ 48 GB | Very strong, large models |

## 2. Recommended Default Mappings by Tier

See [OLLAMA_HARDWARE_TIERS.md](OLLAMA_HARDWARE_TIERS.md) for full tables. Summary:

- **Tier 1**: qwen3:4b (most roles), qwen3:8b (premium/drafting), embedding 0.6b/4b, vision disabled
- **Tier 2**: qwen3:4b (quick), qwen3:8b (default/editing), qwen3:14b (premium), embedding 4b
- **Tier 3**: qwen3:4b (quick), qwen3:8b (default), qwen3:14b/30b (premium/ideation), vision enabled
- **Tier 4**: qwen3:4b (quick), qwen3:8b/14b (default), qwen3:30b/32b (premium), embedding 8b

## 3. How Auto-Selection Works

1. **Tier** — From `OLLAMA_HARDWARE_TIER` or auto-detection (RAM, VRAM via nvidia-smi).
2. **Defaults** — Tier defines recommended model per role.
3. **Resolution** — Project prefs → DB overrides → env → tier defaults → legacy defaults.
4. **Fallback** — If assigned model missing in Ollama, pick first available from tier list or fallback chain.

## 4. How Manual Override Works

- **Admin UI**: Dashboard → Admin → AI → Model role mapping. Edit roles, Save.
- **Apply recommended**: One-click applies tier-based mapping with fallback.
- **Environment**: `OLLAMA_MODEL_QUICK_ASSIST`, etc.
- **Database**: `Setting` key `ai_model_roles`.

Manual overrides always override tier defaults.

## 5. Fallback Behavior

- **Within-Ollama**: If preferred model missing, use next in tier list or fallback chain (e.g. qwen3:8b → qwen3:4b).
- **To cloud**: If no local model works and `AI_PROVIDER_MODE=auto`, use OpenAI/Anthropic.
- **At runtime**: Effective mapping is computed per request when Ollama is enabled.

## 6. Remote Users

**Remote users do not need Ollama on their devices.** When AUTHORA is server-hosted:

- Ollama runs on the server.
- Users access AUTHORA via browser.
- All AI inference runs on the server.
- Hardware tier and model selection apply to the server only.
