# AI Provider System

Provider abstraction layer for AUTHORA's AI engine.

## Supported Providers

| Provider | Type | Status |
|----------|------|--------|
| **OpenAI** | Cloud | Implemented |
| **Anthropic** | Cloud | Implemented |
| **Ollama** | Local | Implemented |
| **Google/Gemini** | Cloud | Architecture-ready |

## Provider Interface

Each provider implements:

- `name` — Provider identifier (openai, anthropic, ollama)
- `complete_stream(prompt, system_prompt, max_tokens, **kwargs)` — Streaming completion
- `complete(prompt, system_prompt, max_tokens, **kwargs)` — Non-streaming, returns `AIResponse`

## AIResponse

```python
@dataclass
class AIResponse:
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str | None = None
```

## Provider Resolution

`get_provider(provider_name)` returns a configured provider:

- If `provider_name` given: return that provider if configured
- Otherwise: use `settings.ai_provider` (openai | anthropic | ollama)

## Credential Storage

- **OpenAI**: `OPENAI_API_KEY` in environment
- **Anthropic**: `ANTHROPIC_API_KEY` in environment
- **Ollama**: No key; `OLLAMA_BASE_URL` (default http://localhost:11434)

Credentials are never logged or exposed. Admin can update via `/admin/ai/config` (writes to .env).

## Health Checks

- **Ollama**: `GET /admin/ai/providers/ollama/health`
- **Ollama embeddings**: `GET /admin/ai/embeddings/ollama/health`

## Enable/Disable

Providers are enabled when credentials are present (OpenAI, Anthropic) or `OLLAMA_ENABLED=true` (Ollama). Admin can disable via config.

## Future Provider Slot

The architecture supports adding providers by:

1. Implementing `AIProvider` interface
2. Registering in `_get_provider_instances()` in `ai_registry.py`
3. Adding to `get_providers_for_mode()` ordering
4. Adding cloud fallback models in `model_role_registry.py` if applicable
