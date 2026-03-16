# Model Routing

AI routing engine that selects the best model/provider for each task.

## Routing Modes

| Mode | Behavior |
|------|----------|
| `auto` | Local-first, fallback to cloud |
| `local_first` | Same as auto |
| `local` | Ollama only, no cloud |
| `cloud` | OpenAI/Anthropic only |
| `privacy_first` | Local only (alias for local) |
| `quality_first` | Cloud first (premium models) |
| `speed_first` | Local first (fast inference) |

## Routing Factors

- **Task type** — writing_assist, fiction_ideation, ghostwriting, etc.
- **User/project preferences** — `ai_mode`, `routing_mode`, `preferred_provider`
- **Provider availability** — only configured providers are considered
- **Plan** — `premium_model_routing` feature for premium users

## Task → Role Mapping

| Task | Role |
|------|------|
| writing_assist | quick_assist_model |
| fiction_ideation | fiction_ideation_model |
| nonfiction_structure | nonfiction_structure_model |
| ghostwriting | premium_drafting_model |
| editing_polish | editing_polish_model |
| general | default_writing_model |

## Role → Model Resolution

**Ollama**: `get_ollama_model_for_role(role)` — order: project_prefs → db_overrides → env → tier defaults → OLLAMA_DEFAULT_MODELS

**Cloud**: `get_cloud_model_for_role(role, provider)` — CLOUD_FALLBACK_MODELS or settings.ai_model

## Fallback Chain

On failure, the system tries:

1. Same provider, retry (up to 3 times)
2. Next provider in mode order (e.g. ollama → openai → anthropic)
3. Legacy `ai.complete` as last resort

## Admin Overrides

- `PUT /admin/ai/model-roles` — Set role → model mappings (stored in Setting)
- `POST /admin/ai/model-roles/apply-recommended` — Apply hardware-tier defaults

## User Overrides

Per-book `ai_prefs`:

- `ai_mode`: auto | cloud | local
- `routing_mode`: auto | quality_first | speed_first | privacy_first | local_first
- `preferred_provider`: openai | anthropic | ollama
- `preferred_model`: Override for cloud
- `preferred_ollama_model`: Override for local
