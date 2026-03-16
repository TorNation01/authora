# Runtime Model Configuration

Per-task routing, model allowlists, and admin-managed configuration for AUTHORA's AI layer.

## Overview

Model selection is resolved in this order:

1. **Project preferred** — `preferred_ollama_model` in book `ai_prefs`
2. **Project per-role** — `model_roles[role]` in project prefs
3. **User preferred** — `preferred_ollama_model` in user `ai_prefs` (when permitted)
4. **Admin DB overrides** — `Setting` key `ollama_model_roles` or role-specific
5. **Environment** — `OLLAMA_MODEL_QUICK_ASSIST`, etc.
6. **Hardware tier** — Tier-based recommended models
7. **Defaults** — `OLLAMA_DEFAULT_MODELS` in code

## Environment Variables

### Ollama Role-Based Models

| Variable | Role | Default |
|----------|------|---------|
| `OLLAMA_MODEL_QUICK_ASSIST` | quick_assist_model | qwen3:4b |
| `OLLAMA_MODEL_DEFAULT_WRITING` | default_writing_model | qwen3:8b |
| `OLLAMA_MODEL_PREMIUM_DRAFTING` | premium_drafting_model | qwen3:14b |
| `OLLAMA_MODEL_FICTION_IDEATION` | fiction_ideation_model | qwen3:8b |
| `OLLAMA_MODEL_NONFICTION_STRUCTURE` | nonfiction_structure_model | qwen3:8b |
| `OLLAMA_MODEL_EDITING_POLISH` | editing_polish_model | qwen3:8b |
| `OLLAMA_MODEL_SUMMARIZATION` | summarization_model | qwen3:4b |
| `OLLAMA_MODEL_EMBEDDINGS` | embeddings_model | qwen3-embedding:4b |
| `OLLAMA_MODEL_OPTIONAL_VISION` | optional_vision_model | qwen3-vl:8b |

### Cloud Model Allowlists

| Variable | Format | Example |
|----------|--------|---------|
| `AI_OPENAI_MODELS_ALLOWLIST` | Comma-separated | `gpt-4o,gpt-4o-mini` |
| `AI_ANTHROPIC_MODELS_ALLOWLIST` | Comma-separated | `claude-3-5-sonnet,claude-3-haiku` |

Empty or unset = allow all. When set, only listed models can be used.

## Admin-Managed Config

### Model Role Overrides

- **Endpoint:** `PUT /admin/ai/model-roles`
- **Storage:** `Setting` table, key `ollama_model_roles`
- **Format:** `{ "quick_assist_model": "qwen3:4b", ... }`

### Ollama Model Capabilities

- **Endpoint:** `PUT /admin/ai/providers/ollama/models/{model}/capabilities`
- **Storage:** `Setting` key `ollama_model_capabilities`
- **Fields:** `capabilities`, `recommended_roles`, `enabled`

### Ollama Timeout

- **Endpoint:** `GET/PUT /admin/ai/providers/ollama/timeout`
- **Storage:** `Setting` key `ollama_model_timeout`
- **Range:** 30–300 seconds

## Per-Task Routing

Task → role mapping is in `ai_registry.ACTION_TO_TASK` and `model_role_registry.TASK_TO_ROLE`.

| Task | Role |
|------|------|
| writing_assist | quick_assist_model |
| fiction_ideation | fiction_ideation_model |
| nonfiction_structure | nonfiction_structure_model |
| ghostwriting | premium_drafting_model |
| editing_polish | editing_polish_model |
| summarization | summarization_model |
| general | default_writing_model |

## Config File (Future)

A YAML/JSON config file for per-task routing is not yet implemented. Current options:

- **Env vars** — `OLLAMA_MODEL_*`
- **Admin API** — `PUT /admin/ai/model-roles`
- **DB Setting** — `ollama_model_roles`

A future `ai_routing.yaml` could support:

```yaml
# Example (not yet implemented)
tasks:
  writing_assist:
    role: quick_assist_model
    ollama: qwen3:4b
    openai: gpt-4o-mini
  ghostwriting:
    role: premium_drafting_model
    ollama: qwen3:14b
    openai: gpt-4o
```

## Fallback Policy

- **Config:** `AI_FALLBACK_ENABLED=true` (default)
- **Behaviour:** On provider failure, retry up to `AI_RETRY_COUNT`, then try next provider in chain
- **Modes:** `local`, `privacy_first`, `strict_privacy` → no cloud fallback

## Related

- [OLLAMA_MULTI_MODEL_ROUTING.md](./OLLAMA_MULTI_MODEL_ROUTING.md) — Ollama routing
- [AI_ROUTING_MATRIX.md](./AI_ROUTING_MATRIX.md) — Task → model matrix
- [TASK_MODEL_DEFAULTS.md](./TASK_MODEL_DEFAULTS.md) — Default mappings
- [ADMIN_AI_MODEL_SETTINGS.md](./ADMIN_AI_MODEL_SETTINGS.md) — Admin UI
