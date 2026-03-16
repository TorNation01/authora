# Task Model Defaults

Default AI model assignments for each writing task in AUTHORA.

## Quick Reference

| Task Category | Role | Ollama Default | Cloud (OpenAI) | Cloud (Anthropic) |
|---------------|------|----------------|----------------|-------------------|
| Quick assist | quick_assist_model | qwen3:4b | gpt-4o-mini | claude-3-haiku |
| Default writing | default_writing_model | qwen3:8b | gpt-4o-mini | claude-3-haiku |
| Premium drafting | premium_drafting_model | qwen3:14b | gpt-4o | claude-3-5-sonnet |
| Fiction ideation | fiction_ideation_model | qwen3:8b | gpt-4o-mini | claude-3-haiku |
| Nonfiction structure | nonfiction_structure_model | qwen3:8b | gpt-4o-mini | claude-3-haiku |
| Editing polish | editing_polish_model | qwen3:8b | gpt-4o-mini | claude-3-haiku |
| Summarization | summarization_model | qwen3:4b | gpt-4o-mini | claude-3-haiku |

## Task-by-Task Defaults

### Idea Generation & Brainstorming

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| generate_scene_ideas | fiction_ideation | fiction_ideation_model | qwen3:8b | Creative, varied output |
| generate_chapter_ideas | fiction_ideation | fiction_ideation_model | qwen3:8b | Structural thinking |
| title_brainstorm | fiction_ideation | fiction_ideation_model | qwen3:8b | Short outputs |
| help_when_stuck | writing_assist | quick_assist_model | qwen3:4b | Fast suggestions |
| generate_examples | writing_assist | quick_assist_model | qwen3:4b | Illustrative |

### Outline & Structure

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| generate_outline | fiction_ideation / nonfiction_structure | fiction_ideation_model / nonfiction_structure_model | qwen3:8b | Structural specialist |

### Rewriting & Editing

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| rewrite_sentence | editing_polish | editing_polish_model | qwen3:8b | Preserve voice |
| rewrite_paragraph | editing_polish | editing_polish_model | qwen3:8b | Strong drafting |
| improve_wording | editing_polish | editing_polish_model | qwen3:8b | Word choice |
| improve_flow | editing_polish | editing_polish_model | qwen3:8b | Transitions |
| condense | editing_polish | editing_polish_model | qwen3:8b | Conciseness |
| fix_transitions | editing_polish | editing_polish_model | qwen3:8b | Flow |
| suggest_transitions | editing_polish | editing_polish_model | qwen3:8b | Suggestions |
| identify_repetition | editing_polish | editing_polish_model | qwen3:8b | Consistency check |
| style_guidance | editing_polish | editing_polish_model | qwen3:8b | Consistency |

### Summarization

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| summarize_chapter | summarization | summarization_model | qwen3:4b | Lightweight |
| summarize_section | summarization | summarization_model | qwen3:4b | Lightweight |
| research_note_summary | editing_polish* | summarization_model (recommended) | qwen3:4b | Factual grounding |
| vault_retrieval_summary | editing_polish* | summarization_model (recommended) | qwen3:4b | Extraction |

\* Currently maps to editing_polish; summarization is recommended for lighter routing.

### Copywriting & Marketing

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| blurb_copy | ghostwriting | premium_drafting_model | qwen3:14b | Premium preferred |
| suggest_chapter_names | writing_assist | quick_assist_model | qwen3:4b | Short outputs |

### Ghostwriting & Draft Assist

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| generate_section | ghostwriting | premium_drafting_model | qwen3:14b | Premium preferred |
| notes_to_prose | writing_assist | quick_assist_model | qwen3:4b | Factual grounding |
| continue_draft | writing_assist | quick_assist_model | qwen3:4b | Premium preferred in catalog |

### Hooks & Conclusions

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| create_hook | writing_assist | quick_assist_model | qwen3:4b | Creative |
| create_conclusion | writing_assist | quick_assist_model | qwen3:4b | Closure |

### General

| Action | Task | Role | Local Default | Notes |
|--------|------|------|---------------|-------|
| expand | writing_assist | quick_assist_model | qwen3:4b | Add detail |
| change_tone | writing_assist | quick_assist_model | qwen3:4b | Tone shift |
| freeform_creative | general | default_writing_model | qwen3:8b | User-defined |

## Future Task Slots (Recommended)

| Task | Suggested Role | Rationale |
|------|----------------|-----------|
| beta_reader_feedback_summary | summarization_model | Lightweight extraction |
| editor_feedback_summary | summarization_model | Lightweight extraction |
| consistency_check | editing_polish_model | Style/voice consistency |

## Hardware Tier Overrides

When `OLLAMA_HARDWARE_TIER` is set, tier-based mappings override defaults:

| Tier | Quick Assist | Default Writing | Premium Drafting | Summarization |
|------|--------------|-----------------|------------------|---------------|
| 1 (low) | qwen3:4b | qwen3:4b | qwen3:8b | qwen3:4b |
| 2 | qwen3:4b | qwen3:8b | qwen3:14b | qwen3:4b |
| 3 | qwen3:4b | qwen3:8b | qwen3:14b | qwen3:4b |
| 4 (high) | qwen3:4b | qwen3:8b | qwen3:30b | qwen3:4b |

## Override Order

Model resolution (highest to lowest priority):

1. Project `preferred_ollama_model` (overrides all roles)
2. Project `model_roles[role]`
3. User `preferred_ollama_model` (when permitted)
4. Admin DB overrides (Setting)
5. Env vars (`OLLAMA_MODEL_QUICK_ASSIST`, etc.)
6. Hardware tier mapping
7. `OLLAMA_DEFAULT_MODELS`

## Related

- [AI_ROUTING_MATRIX.md](./AI_ROUTING_MATRIX.md) — Full routing matrix
- [OLLAMA_HARDWARE_TIERS.md](./OLLAMA_HARDWARE_TIERS.md) — Tier definitions
- [MODEL_ROUTING.md](./MODEL_ROUTING.md) — Routing overview
