# Admin AI Model Settings

Admin controls for the AI model role mapping system. Exposed in **Dashboard → Admin → AI** and via the admin API.

## Model Role Mapping Section

When Ollama is enabled, the admin AI page shows a **Model role mapping** card with:

- **Refresh models** — Fetches available Ollama models from the configured base URL
- **Validate** — Checks that each role’s selected model exists in Ollama
- **Save** — Persists role→model overrides to the database

### Role Dropdowns

Each role has a dropdown populated from the Ollama model list:

| Role | Label |
|------|-------|
| quick_assist_model | Quick assist |
| default_writing_model | Default writing |
| premium_drafting_model | Premium drafting |
| fiction_ideation_model | Fiction ideation |
| nonfiction_structure_model | Nonfiction structure |
| editing_polish_model | Editing & polish |
| embeddings_model | Embeddings |
| optional_vision_model | Vision (optional) |

Custom models (e.g. from env) that are not in the Ollama list appear as `{model} (custom)`.

## Admin API

### GET /api/v1/admin/ai/model-roles

Returns role mappings and available Ollama models.

**Response:**

```json
{
  "roles": ["quick_assist_model", "default_writing_model", ...],
  "mappings": {
    "quick_assist_model": {
      "ollama": "qwen3:4b",
      "openai": "gpt-4o-mini",
      "anthropic": "claude-3-haiku-20240307"
    },
    ...
  },
  "defaults": {
    "quick_assist_model": "qwen3:4b",
    ...
  },
  "cloud_fallbacks": { ... },
  "ollama_models": [{"name": "qwen3:4b", "size": 1234567890}, ...],
  "ollama_base_url": "http://localhost:11434",
  "db_overrides": {}
}
```

### PUT /api/v1/admin/ai/model-roles

Update role→model overrides. Stored in `Setting` key `ai_model_roles`.

**Request body:**

```json
{
  "mappings": {
    "quick_assist_model": "qwen3:4b",
    "premium_drafting_model": "qwen3:14b"
  }
}
```

**Response:**

```json
{
  "ok": true,
  "mappings": {
    "quick_assist_model": "qwen3:4b",
    "premium_drafting_model": "qwen3:14b"
  }
}
```

Only valid role IDs are stored. Invalid keys are ignored.

### GET /api/v1/admin/ai/model-roles/validate

Validates that selected models exist in Ollama.

**Response:**

```json
{
  "valid": true,
  "results": {
    "quick_assist_model": {"model": "qwen3:4b", "valid": true},
    "premium_drafting_model": {"model": "qwen3:14b", "valid": true}
  },
  "available_count": 5
}
```

If Ollama is disabled or unreachable:

```json
{
  "valid": false,
  "message": "Ollama is not enabled",
  "results": {}
}
```

## Override Priority

1. **Admin DB override** — `Setting.ai_model_roles` (set via admin UI or API)
2. **Environment** — `OLLAMA_MODEL_QUICK_ASSIST`, etc.
3. **Recommended defaults** — See [OLLAMA_MODEL_ROLE_MAP.md](OLLAMA_MODEL_ROLE_MAP.md)

Admin overrides take precedence over env. Per-project overrides (future) will take precedence over admin.

## AI History

Provider and model used for each AI action are logged in:

- `AIActionLog` — `provider`, `model`
- `AIRevision` — `provider`, `model`

These reflect the actual provider and model from the registry resolution.

## See Also

- [OLLAMA_MODEL_ROLE_MAP.md](OLLAMA_MODEL_ROLE_MAP.md) — Role definitions and defaults
- [AI_MODEL_REGISTRY.md](AI_MODEL_REGISTRY.md) — Registry design
- [AI_ADMIN_GUIDE.md](AI_ADMIN_GUIDE.md) — General admin AI controls
