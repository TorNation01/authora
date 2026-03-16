# AI Hardware Auto-Mapping

How AUTHORA automatically selects Ollama models based on hardware tier, and how fallback behavior works when preferred models are unavailable.

## Auto-Selection Flow

1. **Hardware tier** — Resolved from `OLLAMA_HARDWARE_TIER` or auto-detection (RAM/VRAM).
2. **Tier defaults** — Each tier has recommended model-role mappings (see [OLLAMA_HARDWARE_TIERS.md](OLLAMA_HARDWARE_TIERS.md)).
3. **Resolution order** — Project prefs (future) → DB admin overrides → env → tier defaults → legacy defaults.
4. **Fallback** — When assigned model is not in Ollama, pick first available from tier preferred list or fallback chain.

## Manual Override

- **Admin UI**: Dashboard → Admin → AI → Model role mapping. Edit each role and Save.
- **One-click apply**: "Apply recommended" applies the tier-based mapping for the current hardware tier, with fallback when models are missing.
- **Environment**: `OLLAMA_MODEL_QUICK_ASSIST`, `OLLAMA_MODEL_DEFAULT_WRITING`, etc.
- **Database**: `Setting` key `ai_model_roles` stores role→model overrides.

Manual overrides always take precedence over tier-based defaults.

## Fallback Behavior

When a role’s assigned model is not available in Ollama:

1. **Within-tier** — Try other models from the tier’s preferred list for that role.
2. **Cross-tier** — Use the fallback chain (e.g. qwen3:8b → qwen3:4b → llama3.2 for text roles).
3. **Cloud** — If no local model works and `AI_PROVIDER_MODE=auto`, fall back to OpenAI or Anthropic.

Fallback is applied at request time when Ollama is enabled: the system fetches available models, applies fallback, and uses the effective mapping for the request.

## Validation

- **Admin → Validate** — Checks that each role’s selected model exists in Ollama.
- **Health** — Model availability is inferred from the Ollama `/api/tags` response.

## Remote Users

**Remote users do not need Ollama installed on their own devices.** When AUTHORA is server-hosted:

- Ollama runs on the server.
- Users connect via browser to the AUTHORA web app.
- All AI inference runs on the server.
- Model selection and hardware tier apply to the server only.

## See Also

- [OLLAMA_HARDWARE_TIERS.md](OLLAMA_HARDWARE_TIERS.md) — Tier definitions and mappings
- [OLLAMA_PERFORMANCE_TUNING.md](OLLAMA_PERFORMANCE_TUNING.md) — Tuning recommendations
- [SERVER_SIZING_AND_MODEL_SELECTION.md](SERVER_SIZING_AND_MODEL_SELECTION.md) — Server sizing
