# Local-First AI Mode

AUTHORA supports several routing modes that control whether local (Ollama) or cloud (OpenAI, Anthropic) AI is used, and how fallback works.

## Routing Modes

| Mode | Behavior |
|------|----------|
| `local_first` | Prefer Ollama; fall back to cloud if local fails or is unavailable |
| `auto` | Same as `local_first` |
| `local` | Ollama only; no cloud fallback |
| `privacy_first` | Same as `local` — local-only when available |
| `strict_privacy` | Local-only; never use cloud (see [PRIVACY_FIRST_AI_MODE.md](./PRIVACY_FIRST_AI_MODE.md)) |
| `quality_first` | Cloud first (premium models); fall back to local if cloud fails |
| `cloud` / `cloud_only` | OpenAI/Anthropic only; no local |
| `speed_first` | Local first (fast inference); fall back to cloud |

## Local-First with Cloud Fallback

When `routing_mode` is `local_first` or `auto`:

1. **First attempt** — Use Ollama with the model resolved for the task (see [OLLAMA_MULTI_MODEL_ROUTING.md](./OLLAMA_MULTI_MODEL_ROUTING.md))
2. **On failure** — Retry same provider up to 3 times
3. **If still failing** — Fall back to next provider in chain: `ollama → openai → anthropic`
4. **User visibility** — Response includes `X-AI-Provider: local` or `X-AI-Provider: cloud` so the UI can indicate which provider was used

## Cloud-First with Local Fallback

When `routing_mode` is `quality_first`:

1. **First attempt** — Use cloud (OpenAI or Anthropic) with premium models
2. **On failure** — Fall back to Ollama
3. **Use case** — When quality is paramount but local is acceptable as backup

## Local-Only (No Cloud Fallback)

When `routing_mode` is `local`, `privacy_first`, or `strict_privacy`:

- **No cloud fallback** — If Ollama is unavailable, the request fails
- **Use case** — Privacy-sensitive work, air-gapped environments, or when cloud API keys are not configured

## Where Routing Mode Is Set

- **Per-book** — `ai_prefs.routing_mode` or `ai_prefs.ai_mode` in book settings
- **User preferences** — `preferences.ai_prefs.routing_mode` (when permitted)
- **Config** — `AI_PROVIDER_MODE` env var (default: `auto`)

## User-Visible Provider Label

The AI Actions API returns `X-AI-Provider: local` or `X-AI-Provider: cloud` in the response headers (or equivalent in the response body for streaming). The frontend can use this to:

- Show a badge like "Local AI" or "Cloud AI"
- Indicate privacy level to the user
- Help users understand when their data stayed local vs. was sent to a cloud provider

## Related

- [OLLAMA_MULTI_MODEL_ROUTING.md](./OLLAMA_MULTI_MODEL_ROUTING.md) — Task routing and model selection
- [PRIVACY_FIRST_AI_MODE.md](./PRIVACY_FIRST_AI_MODE.md) — Strict privacy local-only mode
- [MODEL_ROUTING.md](./MODEL_ROUTING.md) — General model routing overview
