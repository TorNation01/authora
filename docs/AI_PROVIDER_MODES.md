# AI Provider Modes

AUTHORA supports multiple AI providers and lets you choose how they are used via **provider mode**.

## Modes

| Mode | Env | Behavior |
|------|-----|----------|
| **Auto** | `AI_PROVIDER_MODE=auto` | Prefer local (Ollama) first, fallback to cloud (OpenAI, Anthropic) |
| **Cloud** | `AI_PROVIDER_MODE=cloud` | Use only cloud providers (OpenAI, Anthropic) |
| **Local** | `AI_PROVIDER_MODE=local` | Use only local provider (Ollama) |

Default: `auto`.

## Per-Project Override

Projects and books can override the global mode via **per-book AI preferences**:

- `ai_mode`: `auto` | `cloud` | `local`
- `preferred_provider`: `openai` | `anthropic` | `ollama`
- `preferred_model`: model name (e.g. `llama3.2`, `gpt-4o-mini`)

Stored in `book_settings.settings["ai_prefs"]`. Updated via:

- `GET /api/v1/projects/{id}/books/{id}/ai-preferences`
- `PATCH /api/v1/projects/{id}/books/{id}/ai-preferences`

## Resolution Order

1. Book/project `ai_prefs.ai_mode` or `preferred_provider`
2. Global `AI_PROVIDER_MODE`
3. Provider order for mode:
   - **auto**: local (Ollama) → cloud (OpenAI, Anthropic)
   - **cloud**: OpenAI → Anthropic
   - **local**: Ollama only

## Fallback Chain

When the primary provider fails (rate limit, timeout, error), AUTHORA tries the next provider in the chain for that mode. For example, in `auto` mode:

1. Try Ollama (if enabled)
2. If Ollama fails → try OpenAI
3. If OpenAI fails → try Anthropic
