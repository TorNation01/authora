# AI Task Catalog

Formal catalog of AI tasks in AUTHORA.

## Task Metadata

Each task defines:

- **ideal_model_characteristics** — e.g. "creative", "preserves voice"
- **context_needs** — e.g. "premise", "genre", "selection"
- **safety_rules** — e.g. "preserve author voice", "suggestions only"
- **requires_factual_grounding** — For research/summary tasks
- **local_acceptable** — Whether Ollama is acceptable
- **premium_preferred** — Whether to prefer premium models when available
- **max_tokens** — Output limit

## Task Categories

| Category | Examples |
|----------|----------|
| writing_assist | expand, condense, continue_draft |
| fiction_ideation | generate_scene_ideas, generate_chapter_ideas |
| nonfiction_structure | generate_outline |
| ghostwriting | generate_section, notes_to_prose, blurb_copy |
| editing_polish | rewrite_sentence, improve_flow, fix_transitions |
| summarization | summarize_chapter, summarize_section |
| brainstorming | suggest_chapter_names, help_when_stuck |
| extraction | vault_retrieval_summary |
| general | freeform_creative |

## Task List

| Task ID | Label | Category |
|---------|-------|----------|
| rewrite_sentence | Rewrite sentence | editing_polish |
| rewrite_paragraph | Rewrite paragraph | editing_polish |
| improve_wording | Improve wording | editing_polish |
| improve_flow | Improve flow | editing_polish |
| expand | Expand | writing_assist |
| condense | Condense | editing_polish |
| change_tone | Change tone | writing_assist |
| continue_draft | Continue draft | writing_assist |
| generate_outline | Generate outline | nonfiction_structure |
| generate_scene_ideas | Generate scene ideas | fiction_ideation |
| generate_chapter_ideas | Generate chapter ideas | fiction_ideation |
| generate_examples | Generate examples | writing_assist |
| summarize_chapter | Summarize chapter | summarization |
| suggest_chapter_names | Suggest chapter names | brainstorming |
| fix_transitions | Fix transitions | editing_polish |
| create_hook | Create hook/opening | writing_assist |
| create_conclusion | Create conclusion | writing_assist |
| help_when_stuck | Help when stuck | brainstorming |
| notes_to_prose | Convert notes to prose | ghostwriting |
| generate_section | Generate section | ghostwriting |
| title_brainstorm | Title brainstorm | brainstorming |
| blurb_copy | Blurb copy | ghostwriting |
| research_note_summary | Research note summary | summarization |
| vault_retrieval_summary | Vault retrieval summary | extraction |
| identify_repetition | Identify repetition | editing_polish |
| suggest_transitions | Suggest transitions | editing_polish |
| style_guidance | Style guidance | editing_polish |
| freeform_creative | Freeform creative | general |

## Integration

- `ai_orchestration.ACTION_DEFINITIONS` — Prompt templates (fiction/nonfiction/general)
- `ai_registry.ACTION_TO_TASK` — Maps action_id → task type
- `ai_task_catalog.AI_TASK_CATALOG` — Full metadata for routing and safety
