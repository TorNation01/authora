# Ollama Multi-Model Routing

AUTHORA supports multiple local Ollama models with intelligent task-based routing, capability tagging, and per-project/user preferences.

## Overview

- **Model discovery** — Detects installed Ollama models via the Ollama API
- **Capability tagging** — Tag models for roles (e.g. fast creative, strong writing, efficient summarizer)
- **Task routing** — Each writing task maps to a role, then to a model via preferences and capability tags
- **Fallback** — When a preferred model is unavailable, falls back to tier defaults or smaller models

## Task → Role Mapping

| Task | Role | Typical Use |
|------|------|-------------|
| Brainstorming, quick assist | `quick_assist_model` | Fast creative local model |
| Rewrite, improve wording | `editing_polish_model` | Strong local writing model |
| Summarize chapter/section | `summarization_model` | Efficient summarizer local model |
| Ghostwriting, generate section | `premium_drafting_model` | Best available premium model (if allowed) |
| Fiction ideation | `fiction_ideation_model` | Creative local model |
| Nonfiction structure | `nonfiction_structure_model` | Structure-focused local model |
| General | `default_writing_model` | Default writing model |

## Model Resolution Order

1. **Project preferred** — `preferred_ollama_model` in book/project `ai_prefs` (overrides all roles)
2. **Project per-role** — `model_roles[role]` in project prefs
3. **User preferred** — `preferred_ollama_model` in user `ai_prefs` (when permitted)
4. **DB overrides** — Admin-set role → model mappings (Setting)
5. **Env vars** — `OLLAMA_MODEL_QUICK_ASSIST`, etc.
6. **Hardware tier** — Tier-based recommended models
7. **Defaults** — `OLLAMA_DEFAULT_MODELS`

## Capability Tags

Models can be tagged with capabilities and recommended roles in Admin:

- **Capabilities** — e.g. `fast`, `creative`, `summarization`, `editing`, `premium`
- **Recommended roles** — Which roles this model is suited for
- **Enabled** — Whether the model is available for routing

Stored in `Setting` under `ollama_model_capabilities`.

## Admin Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/ai/providers/ollama/models` | GET | List models with capability tags |
| `/admin/ai/providers/ollama/models/{model}/capabilities` | PUT | Update capability tags |
| `/admin/ai/providers/ollama/models/{model}/test` | POST | Run test prompt against model |
| `/admin/ai/providers/ollama/timeout` | GET/PUT | Read/update request timeout (30–300s) |
| `/admin/ai/providers/ollama/health` | GET | Ollama host health check |

## Timeout Settings

- Default: 120 seconds
- Range: 30–300 seconds
- Stored in `Setting` under `ollama_model_timeout`
- Applied to all Ollama generation requests

## Offline / Unavailable Handling

- **Health check** — `GET /admin/ai/providers/ollama/health` verifies Ollama connectivity
- **Per-model test** — `POST /admin/ai/providers/ollama/models/{model}/test` validates a specific model
- **Fallback chain** — On timeout or error, the system retries with the next provider in the routing mode order (see [LOCAL_FIRST_MODE.md](./LOCAL_FIRST_MODE.md))
- **User-visible label** — AI responses include `X-AI-Provider: local` or `X-AI-Provider: cloud` so the UI can show whether local or cloud AI was used

## Related

- [LOCAL_FIRST_MODE.md](./LOCAL_FIRST_MODE.md) — Local-first vs cloud-first routing modes
- [PRIVACY_FIRST_AI_MODE.md](./PRIVACY_FIRST_AI_MODE.md) — Strict privacy local-only mode
- [OLLAMA_INTEGRATION.md](./OLLAMA_INTEGRATION.md) — Ollama setup and configuration
- [OLLAMA_HARDWARE_TIERS.md](./OLLAMA_HARDWARE_TIERS.md) — Tier-based model recommendations
