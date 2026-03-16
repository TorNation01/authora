# AI Model Registry

AUTHORA uses a **configurable AI model registry** with task-role assignments. The registry resolves which model to use for each AI task, supports admin overrides, and enables fallback from local (Ollama) to cloud (OpenAI, Anthropic).

## Overview

- **Roles** — Named slots (e.g. `quick_assist_model`, `premium_drafting_model`) that map to specific models
- **Tasks** — AI action types (e.g. `writing_assist`, `ghostwriting`) that map to roles
- **Resolution** — Project prefs → DB overrides → env → recommended defaults

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `model_role_registry` | `authora/services/model_role_registry.py` | Role constants, defaults, resolution |
| `ai_registry` | `authora/services/ai_registry.py` | Task routing, provider selection |
| `ai_model_settings` | `authora/services/ai_model_settings.py` | Load/save DB overrides |
| `Setting` | `ai_model_roles` key | Admin overrides (JSON: `{role: model}`) |

## Resolution Flow

```
Task (e.g. ghostwriting)
  → task_to_role(task)  →  premium_drafting_model
  → get_ollama_model_for_role(role)
      1. project_prefs.model_roles[role]  (future)
      2. db_overrides[role]  (Setting ai_model_roles)
      3. getattr(settings, ROLE_CONFIG_KEYS[role])  (env)
      4. OLLAMA_DEFAULT_MODELS[role]
      5. settings.ollama_model_default
```

## Usage in Code

```python
from authora.services.model_role_registry import (
    task_to_role,
    get_ollama_model_for_role,
    get_cloud_model_for_role,
    get_all_role_mappings,
)

# Resolve model for a task
role = task_to_role("ghostwriting")  # premium_drafting_model
model = get_ollama_model_for_role(role, db_overrides=overrides)

# Cloud fallback
cloud_model = get_cloud_model_for_role(role, "openai", settings.ai_model)

# Admin: all mappings
mappings = get_all_role_mappings(db_overrides=overrides)
```

## Integration Points

| Caller | Uses |
|--------|------|
| `ai_registry.get_provider_for_task` | `task_to_role`, `get_ollama_model_for_role` |
| `ai_registry._get_model_for_task` | Role-based resolution for Ollama and cloud |
| `ai_actions.run_action_stream` | Loads `db_overrides`, passes to `complete_with_retry` |
| Admin API `GET /admin/ai/model-roles` | `get_all_role_mappings`, `get_ai_model_role_overrides` |
| Admin API `PUT /admin/ai/model-roles` | `save_ai_model_role_overrides` |

## Per-Project Override (Future)

The registry supports `project_prefs.model_roles` as the highest-priority override. When implemented:

- Book/project settings can store `ai_prefs.model_roles = { role: model }`
- Resolution will use project override before DB admin override
- Global defaults remain unchanged for projects without overrides

## Validation

- Admin UI: **Validate** button calls `GET /admin/ai/model-roles/validate`
- Validates that each role’s selected model exists in Ollama (`/api/tags`)
- Returns `{ valid: bool, results: { role: { model, valid } } }`

## See Also

- [OLLAMA_MODEL_ROLE_MAP.md](OLLAMA_MODEL_ROLE_MAP.md) — Role definitions and default mappings
- [ADMIN_AI_MODEL_SETTINGS.md](ADMIN_AI_MODEL_SETTINGS.md) — Admin UI and API
- [AI_PROVIDER_MODES.md](AI_PROVIDER_MODES.md) — Auto, cloud, local modes
