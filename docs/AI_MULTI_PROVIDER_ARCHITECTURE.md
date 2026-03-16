# AI Multi-Provider Architecture Report

Short architecture report on AUTHORA's multi-provider AI support.

---

## 1. How Multiple AI Providers Are Supported

AUTHORA uses a **provider-agnostic architecture**:

- **Provider interface** (`ai_provider.py`): `AIProvider` with `complete()`, `complete_stream()`, returning `AIResponse` (text, provider, model, tokens).
- **Provider implementations**: `OpenAIProvider`, `AnthropicProvider`, `OllamaProvider`.
- **Registry** (`ai_registry.py`): `get_provider_for_task()`, `get_fallback_chain()`, `list_available_providers()`.
- **Service layer** (`ai_service.py`): `complete_sync()`, `complete_stream()` — both use the registry and support fallback.

Adding a new provider (e.g. Gemini, Anthropic v2):

1. Implement `AIProvider` (complete, complete_stream).
2. Register in `get_provider()` and `_get_provider_instances()`.
3. Add config/env and optional task routing.

No major rewrite required.

---

## 2. How Ollama Is Integrated

- **OllamaProvider** (`infrastructure/ai_provider/ollama_provider.py`): HTTP client to Ollama `/api/chat` (streaming and non-streaming) and `/api/tags` (list models).
- **Config**: `OLLAMA_ENABLED`, `OLLAMA_BASE_URL`, `OLLAMA_MODEL_DEFAULT`, task-specific `OLLAMA_MODEL_*`.
- **Registry**: Ollama is a first-class provider; `get_provider_for_task()` returns it when enabled and mode allows.
- **Setup wizard**: Ollama option, base URL, connection test.
- **Admin**: Health check, model list, refresh.

---

## 3. How Multiple Ollama Models Are Selected

- **Task routing**: Each task (writing_assist, fiction_ideation, ghostwriting, etc.) can map to a different Ollama model via env:
  - `OLLAMA_MODEL_WRITING_ASSIST`, `OLLAMA_MODEL_FICTION_IDEATION`, etc.
- **Fallback**: If a task-specific model is not set, `OLLAMA_MODEL_DEFAULT` is used.
- **Resolution**: `get_ollama_model_for_task(task)` in config returns the model for that task.

---

## 4. How Remote Users Use Server-Hosted AI Without Local Installs

- **Server deployment**: AUTHORA API runs on a server. Ollama runs on the same server (or a reachable host).
- **Client flow**: Browsers (web app) call the API only. No Ollama or AI SDK on the client.
- **API flow**: `POST /api/v1/ai/actions/run` → `ai_service.complete_stream()` → registry → OllamaProvider → HTTP to `OLLAMA_BASE_URL`.
- **Config**: `OLLAMA_BASE_URL=http://localhost:11434` when Ollama is on the API server; or `http://ollama-host:11434` when on another host.
- **Result**: Remote users get AI via the browser; all AI runs server-side. No local Ollama required.

---

## Summary

| Aspect | Implementation |
|--------|----------------|
| Multi-provider | Registry, provider interface, fallback chain |
| Ollama | OllamaProvider, config, setup wizard, admin UI |
| Model selection | Task → env mapping, `get_ollama_model_for_task()` |
| Remote use | API-only; Ollama on server; clients use browser |
