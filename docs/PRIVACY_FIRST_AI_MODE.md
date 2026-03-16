# Privacy-First AI Mode

AUTHORA supports strict privacy modes that ensure sensitive manuscript work never leaves the local environment.

## Modes

| Mode | Behavior |
|------|----------|
| `privacy_first` | Local-only; no cloud fallback |
| `strict_privacy` | Local-only; never use cloud (explicit strict variant) |
| `local` | Local-only; same as above |

All three modes prevent any fallback to OpenAI or Anthropic. If Ollama is unavailable, the request fails rather than sending data to the cloud.

## Use Cases

- **Source-sensitive private manuscript work** — Keep all AI processing local when handling confidential or unpublished material
- **Air-gapped deployments** — No cloud connectivity; Ollama is the only option
- **Compliance** — When policy requires that AI processing stays on-premises
- **User preference** — Writers who explicitly want local-only AI

## How It Works

1. **Provider selection** — `get_providers_for_mode("privacy_first")` returns only `["ollama"]`
2. **Fallback chain** — `get_fallback_chain()` returns an empty cloud fallback when mode is `local`, `privacy_first`, or `strict_privacy`
3. **Failure behavior** — If Ollama times out, is offline, or errors, the request fails. No automatic switch to cloud.

## Setting Privacy Mode

- **Per-book** — Set `routing_mode: "privacy_first"` or `ai_mode: "local"` in book `ai_prefs`
- **User preferences** — `preferences.ai_prefs.routing_mode: "privacy_first"` (when permitted by plan/admin)
- **Config** — `AI_PROVIDER_MODE=local` or `AI_PROVIDER_MODE=privacy_first` for server-wide default

## User Visibility

When privacy mode is active:

- The UI can show a clear indicator that "Local AI only" or "Privacy mode" is enabled
- Responses include `X-AI-Provider: local` when successful
- If Ollama is unavailable, the user sees an error rather than unexpected cloud usage

## Requirements

- **Ollama must be configured** — `OLLAMA_ENABLED=true` and a reachable `OLLAMA_BASE_URL`
- **At least one model** — Ollama must have at least one model pulled and available
- **Health check** — Use `GET /admin/ai/providers/ollama/health` to verify connectivity before enabling privacy mode for users

## Related

- [LOCAL_FIRST_MODE.md](./LOCAL_FIRST_MODE.md) — Local-first with cloud fallback
- [OLLAMA_MULTI_MODEL_ROUTING.md](./OLLAMA_MULTI_MODEL_ROUTING.md) — Model selection for local tasks
- [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) — Ollama installation and configuration
