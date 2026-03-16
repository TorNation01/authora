# AI Environment Configuration

Secure environment variable handling and provider-specific configuration for AUTHORA's AI layer.

## Secret Handling

- **Never log API keys** — Keys are validated for format only; raw values are never written to logs
- **Use env files** — Store secrets in `.env` (gitignored). Never commit `.env` to version control
- **Redaction** — Log messages are scanned for secret-like patterns (`sk-`, `sk-ant-`, `AIza`) and redacted
- **Validation** — Keys are validated at startup; invalid format logs a warning without exposing the value

## Provider API Keys

| Variable | Provider | Format | Required When |
|----------|----------|--------|---------------|
| `OPENAI_API_KEY` | OpenAI | `sk-` prefix, 20+ chars | Using OpenAI |
| `ANTHROPIC_API_KEY` | Anthropic | `sk-ant-` prefix, 20+ chars | Using Anthropic |
| `GEMINI_API_KEY` | Gemini (slot) | `AIza` prefix, 30+ chars | Using Gemini |

## Ollama Host Config

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_ENABLED` | `false` | Set to `true` to enable Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL (http or https) |
| `OLLAMA_MODEL_DEFAULT` | `llama3.2` | Default model when no role-specific |
| `OLLAMA_REQUEST_TIMEOUT` | `120` | Request timeout in seconds (30–300) |
| `OLLAMA_HARDWARE_TIER` | auto | `1` \| `2` \| `3` \| `4` for model recommendations |

## Provider Toggles

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_CLOUD_DISABLED` | `false` | Disable all cloud providers (OpenAI, Anthropic, Gemini) |
| `AI_LOCAL_ONLY` | `false` | Local-only mode; no cloud fallback |
| `AI_OPENAI_ENABLED` | (auto) | Override: `true`/`false` to force enable/disable |
| `AI_ANTHROPIC_ENABLED` | (auto) | Override: `true`/`false` |
| `AI_OLLAMA_ENABLED` | (auto) | Override: uses `OLLAMA_ENABLED` when unset |

## Timeouts and Retries

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_OPENAI_TIMEOUT` | `60` | OpenAI request timeout (seconds) |
| `AI_ANTHROPIC_TIMEOUT` | `60` | Anthropic request timeout (seconds) |
| `AI_OLLAMA_TIMEOUT` | `120` | Ollama request timeout (seconds) |
| `AI_RETRY_COUNT` | `3` | Retries per provider before fallback |
| `AI_FALLBACK_ENABLED` | `true` | Allow fallback to next provider on failure |

## Model Allowlists

Restrict which models can be used. Empty = allow all.

| Variable | Format | Example |
|----------|--------|---------|
| `AI_OPENAI_MODELS_ALLOWLIST` | Comma-separated | `gpt-4o,gpt-4o-mini` |
| `AI_ANTHROPIC_MODELS_ALLOWLIST` | Comma-separated | `claude-3-5-sonnet,claude-3-haiku` |

## Routing Mode

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER_MODE` | `auto` | `auto` \| `local_first` \| `quality_first` \| `privacy_first` \| `cloud` \| `local` |

## Per-Environment Overrides

Use `AUTHORA_ENV` or `ENVIRONMENT` to set:

- `development` — Default; relaxed validation
- `staging` — Staging; can disable cloud for cost control
- `production` — Production; stricter validation

Example:

```bash
AUTHORA_ENV=production
AI_CLOUD_DISABLED=false
AI_LOCAL_ONLY=false
```

## Validation

At startup, the API:

1. Logs which providers are configured (no secrets)
2. Validates key format for configured providers
3. Warns if no AI provider is available
4. Warns if config is present but validation fails

## Related

- [AI_DEPLOYMENT_CONFIG.md](./AI_DEPLOYMENT_CONFIG.md) — Deployment and secrets
- [ENV-MAP.md](./ENV-MAP.md) — Full environment variable reference
- [PROVIDER_HEALTHCHECKS.md](./PROVIDER_HEALTHCHECKS.md) — Health endpoints
