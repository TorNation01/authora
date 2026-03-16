# Ollama Model Role Map

AUTHORA uses a **role-based model registry** to assign Ollama models to AI tasks. Each role has a recommended default model and can be overridden via env, admin UI, or (future) per-project settings.

## Roles

| Role ID | Description | Use case |
|---------|-------------|----------|
| `quick_assist_model` | Quick assist | Light suggestions, expand, continue_draft |
| `default_writing_model` | Default writing | General completion, fallback |
| `premium_drafting_model` | Premium drafting | Ghostwriting, full section generation |
| `fiction_ideation_model` | Fiction ideation | Outlines, scene ideas, chapter ideas |
| `nonfiction_structure_model` | Nonfiction structure | Nonfiction outlines, structure |
| `editing_polish_model` | Editing & polish | Rewrite, improve wording, condense |
| `embeddings_model` | Embeddings | RAG, semantic search (Ollama /api/embed) |
| `optional_vision_model` | Vision (optional) | Image-aware tasks (future) |

## Recommended Default Mappings

| Role | Recommended Ollama model | Alternatives |
|------|--------------------------|--------------|
| quick_assist_model | `qwen3:4b` | Fast, low latency |
| default_writing_model | `qwen3:8b` | Balanced quality/speed |
| premium_drafting_model | `qwen3:14b` | Best quality for long drafts |
| fiction_ideation_model | `qwen3:8b` or `qwen3:14b` | Creative brainstorming |
| nonfiction_structure_model | `qwen3:8b` or `qwen3:14b` | Structure and logic |
| editing_polish_model | `qwen3:8b` | Editing and refinement |
| embeddings_model | `qwen3-embedding:4b` or `mxbai-embed-large` | RAG embeddings |
| optional_vision_model | `qwen3-vl:8b` or `gemma3` | Vision tasks (optional) |

## Environment Variables

| Variable | Role | Default |
|----------|------|---------|
| `OLLAMA_MODEL_QUICK_ASSIST` | quick_assist_model | qwen3:4b |
| `OLLAMA_MODEL_DEFAULT_WRITING` | default_writing_model | qwen3:8b |
| `OLLAMA_MODEL_PREMIUM_DRAFTING` | premium_drafting_model | qwen3:14b |
| `OLLAMA_MODEL_FICTION_IDEATION` | fiction_ideation_model | qwen3:8b |
| `OLLAMA_MODEL_NONFICTION_STRUCTURE` | nonfiction_structure_model | qwen3:8b |
| `OLLAMA_MODEL_EDITING_POLISH` | editing_polish_model | qwen3:8b |
| `OLLAMA_MODEL_EMBEDDINGS` | embeddings_model | qwen3-embedding:4b |
| `OLLAMA_MODEL_OPTIONAL_VISION` | optional_vision_model | qwen3-vl:8b |

## Task → Role Mapping

| Task | Role |
|------|------|
| writing_assist | quick_assist_model |
| fiction_ideation | fiction_ideation_model |
| nonfiction_structure | nonfiction_structure_model |
| ghostwriting | premium_drafting_model |
| editing_polish | editing_polish_model |
| general | default_writing_model |

## Resolution Order

1. **Per-project override** (future) — `project_prefs.model_roles[role]`
2. **Admin DB override** — `Setting` key `ai_model_roles`
3. **Environment** — `OLLAMA_MODEL_*` vars
4. **Recommended default** — `OLLAMA_DEFAULT_MODELS[role]`
5. **Fallback** — `OLLAMA_MODEL_DEFAULT`

## Cloud Fallback

When local (Ollama) is unavailable and `AI_PROVIDER_MODE=auto`, AUTHORA falls back to cloud providers with role-specific models:

| Role | OpenAI fallback | Anthropic fallback |
|------|-----------------|---------------------|
| quick_assist_model | gpt-4o-mini | claude-3-haiku-20240307 |
| premium_drafting_model | gpt-4o | claude-3-5-sonnet-20241022 |
| embeddings_model | text-embedding-3-small | — |
| (others) | gpt-4o-mini | claude-3-haiku-20240307 |

## See Also

- [AI_MODEL_REGISTRY.md](AI_MODEL_REGISTRY.md) — Registry design and usage
- [ADMIN_AI_MODEL_SETTINGS.md](ADMIN_AI_MODEL_SETTINGS.md) — Admin UI and API
- [MODEL_ROUTING.md](MODEL_ROUTING.md) — Task routing and action mapping
