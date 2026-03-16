# AI Admin Guide

Admin controls for AI providers in AUTHORA.

## Admin → AI Providers

Path: `/dashboard/admin/ai`

### Provider Mode

Shows current `AI_PROVIDER_MODE` (auto | cloud | local). Change via env:

```env
AI_PROVIDER_MODE=auto
```

### Configured Providers

Lists all available providers (OpenAI, Anthropic, Ollama) with:

- Name and type (local vs cloud)
- Default model
- Enabled status

### Ollama Section

When `OLLAMA_ENABLED=true`:

- **Health** — connectivity check to Ollama
- **Refresh models** — sync list of installed models from Ollama
- **Available models** — names and sizes

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/admin/ai/providers` | List providers and config |
| `GET /api/v1/admin/ai/providers/ollama/health` | Ollama health check |
| `GET /api/v1/admin/ai/providers/ollama/models` | List Ollama models |

## Enable/Disable Providers

Providers are enabled/disabled via env:

- **OpenAI**: set `OPENAI_API_KEY`
- **Anthropic**: set `ANTHROPIC_API_KEY`
- **Ollama**: set `OLLAMA_ENABLED=true`

No per-provider toggle in the UI; use env or setup wizard.

## Per-Book AI Preferences

Users (or admins) can set per-book preferences:

- `PATCH /api/v1/projects/{id}/books/{id}/ai-preferences`
- Body: `{ "ai_mode": "local", "preferred_provider": "ollama", "preferred_model": "llama3.2" }`

## Usage Logging

AI actions are logged to `ai_action_log` with:

- `provider`, `model`
- `input_tokens`, `output_tokens`
- `action_id`, `status`

View via Admin → AI usage (`/dashboard/admin/ai-usage`).

## Health Checks

- **System health** (`/api/v1/admin/health/detailed`): includes `ai_configured` (true if any provider is configured)
- **Ollama health** (`/api/v1/admin/ai/providers/ollama/health`): Ollama-specific connectivity

## Troubleshooting

| Issue | Check |
|-------|-------|
| Ollama not reachable | `OLLAMA_BASE_URL`, firewall, Ollama running |
| No models listed | Run `ollama pull <model>` on the Ollama host |
| Cloud provider fails | API key, rate limits, model name |
| Wrong model used | Task routing, `OLLAMA_MODEL_*` env vars |
