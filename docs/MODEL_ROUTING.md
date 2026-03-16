# Model Routing

AUTHORA routes AI requests to providers and models based on **task type** and configuration.

## Task Types

| Task | Description | Example actions |
|------|--------------|-----------------|
| `writing_assist` | General writing help | expand, continue_draft, change_tone |
| `fiction_ideation` | Fiction brainstorming | generate_outline, generate_scene_ideas |
| `nonfiction_structure` | Nonfiction structure | nonfiction outlines |
| `ghostwriting` | Full draft generation | generate_section, chapter drafts |
| `editing_polish` | Editing and polish | rewrite_sentence, improve_wording |
| `general` | Fallback | free-form completion |

## Action → Task Mapping

| Action ID | Task |
|-----------|------|
| rewrite_sentence, rewrite_paragraph, improve_wording, improve_flow | editing_polish |
| expand, change_tone, continue_draft | writing_assist |
| condense, summarize_chapter, fix_transitions | editing_polish |
| generate_outline, generate_scene_ideas, generate_chapter_ideas | fiction_ideation |
| generate_section | ghostwriting |
| ... | (see `ai_registry.ACTION_TO_TASK`) |

## Provider Model Resolution

### OpenAI

- Model: `AI_MODEL` env or `gpt-4o-mini`
- Same model for all tasks (no task-specific routing for OpenAI in current config)

### Anthropic

- Model: `AI_MODEL` env or `claude-3-haiku-20240307`
- Same model for all tasks

### Ollama

- Model: task-specific env or `OLLAMA_MODEL_DEFAULT`
- `get_ollama_model_for_task(task)` returns the configured model for that task

## Resolution Flow

1. **Project/book prefs** — `ai_prefs.preferred_provider`, `ai_prefs.preferred_model`
2. **Provider mode** — `AI_PROVIDER_MODE` (auto/cloud/local)
3. **Provider order** — local first in auto, then cloud
4. **Model for task** — `get_ollama_model_for_task(task)` for Ollama; `AI_MODEL` for cloud

## Fallback

If the primary provider fails, the next provider in the chain is tried. No per-task fallback model within Ollama (e.g. llama3.2 → mistral) is configured by default; that would require additional config.
