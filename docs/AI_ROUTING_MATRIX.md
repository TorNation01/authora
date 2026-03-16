# AI Routing Matrix

Launch-ready routing matrix mapping writing tasks to model classes and provider preferences.

## Model Classes

| Class | Role | Local Default | Cloud Fallback | Use When |
|-------|------|--------------|----------------|----------|
| **Fast local creative** | `quick_assist_model` | qwen3:4b | gpt-4o-mini, claude-3-haiku | Brainstorming, quick ideas, help when stuck |
| **Strong local drafting** | `editing_polish_model` | qwen3:8b | gpt-4o-mini | Rewrite, improve flow, fix transitions |
| **Premium cloud reasoning** | `premium_drafting_model` | qwen3:14b | gpt-4o, claude-3-5-sonnet | Ghostwriting, large structural assist |
| **Lightweight summarization** | `summarization_model` | qwen3:4b | gpt-4o-mini | Chapter/section summary, research notes, vault retrieval |
| **Privacy-safe local** | Any local role | Per-role | — | When `privacy_first` or `strict_privacy` mode |
| **Copywriting specialist** | `premium_drafting_model` | qwen3:14b | gpt-4o | Blurb, marketing copy |
| **Structural/planning specialist** | `fiction_ideation_model` / `nonfiction_structure_model` | qwen3:8b | gpt-4o-mini | Outline, chapter ideas, scene ideas |

## Task → Model Class Mapping

| Task | Model Class | Local Enough? | Premium Recommended? |
|------|-------------|---------------|----------------------|
| Idea generation | Fast local creative | ✓ | No |
| Outline generation | Structural specialist | ✓ | No |
| Rewrite paragraph | Strong local drafting | ✓ | No |
| Improve flow | Strong local drafting | ✓ | No |
| Chapter summary | Lightweight summarization | ✓ | No |
| Consistency check | Strong local drafting | ✓ | No |
| Blurb writing | Copywriting specialist | Maybe | Yes |
| Title generation | Fast local creative | ✓ | No |
| Ghostwriting draft assist | Premium cloud reasoning | Maybe | Yes |
| Beta-reader feedback summary | Lightweight summarization | ✓ | No |
| Editor feedback summary | Lightweight summarization | ✓ | No |
| Research note summarization | Lightweight summarization | ✓ | No |
| Knowledge-vault retrieval summary | Lightweight summarization | ✓ | No |

## Default Routing Logic

1. **Resolve routing mode** — From project `ai_prefs.routing_mode` or `ai_mode`, else config `AI_PROVIDER_MODE` (default: `auto`).
2. **Map action → task** — Via `ACTION_TO_TASK` (e.g. `rewrite_paragraph` → `editing_polish`).
3. **Map task → role** — Via `TASK_TO_ROLE` (e.g. `editing_polish` → `editing_polish_model`).
4. **Resolve model** — Project preferred → project per-role → user preferred → db overrides → env → tier → defaults.
5. **Select provider** — Per mode: `local_first` → ollama first; `quality_first` → cloud first; `privacy_first` → local only.

## Fallback Logic

| Scenario | Behavior |
|----------|----------|
| Preferred model unavailable | Use tier fallback or next smaller model (e.g. qwen3:14b → qwen3:8b → qwen3:4b) |
| Ollama timeout/error | Retry same provider up to 3×; then next provider in chain (if mode allows cloud) |
| Mode `local_first` / `auto` | Chain: ollama → openai → anthropic |
| Mode `quality_first` | Chain: openai/anthropic → ollama |
| Mode `privacy_first` / `strict_privacy` | No cloud fallback; request fails if local unavailable |

## Privacy Notes

| Mode | Data Leaves Local? | Use Case |
|------|--------------------|----------|
| `privacy_first` | No | Source-sensitive manuscript, compliance |
| `strict_privacy` | No | Same as above, explicit |
| `local` | No | Local-only preference |
| `local_first` | Only if local fails | Hybrid; fallback may send to cloud |
| `quality_first` | Yes (first attempt) | Premium quality; local as backup |
| `cloud` / `cloud_only` | Yes | Cloud-only deployment |

**When local is enough:** Brainstorming, summarization, rewrites, consistency checks, title ideas, research/vault summaries. Most day-to-day writing assist.

**When premium is recommended:** Ghostwriting, blurb copy, long-form generation, complex structural planning. Premium improves coherence and polish.

## Cost Notes

| Provider | Typical Cost | Best For |
|----------|--------------|----------|
| Ollama (local) | $0 (compute only) | All tasks when available |
| gpt-4o-mini | Low | Quick assist, summarization, editing |
| gpt-4o | Medium–high | Ghostwriting, blurb, premium drafting |
| claude-3-haiku | Low | Quick assist, summarization |
| claude-3-5-sonnet | Medium–high | Ghostwriting, premium drafting |

**Recommendation:** Use local-first for most tasks; reserve premium cloud for ghostwriting and copywriting when quality matters.

## Action → Task Reference

| Action ID | Task | Model Class |
|-----------|------|-------------|
| `generate_scene_ideas` | fiction_ideation | Structural specialist |
| `generate_chapter_ideas` | fiction_ideation | Structural specialist |
| `generate_outline` | fiction_ideation / nonfiction_structure | Structural specialist |
| `rewrite_sentence` | editing_polish | Strong local drafting |
| `rewrite_paragraph` | editing_polish | Strong local drafting |
| `improve_wording` | editing_polish | Strong local drafting |
| `improve_flow` | editing_polish | Strong local drafting |
| `condense` | editing_polish | Strong local drafting |
| `fix_transitions` | editing_polish | Strong local drafting |
| `identify_repetition` | editing_polish | Strong local drafting |
| `suggest_transitions` | editing_polish | Strong local drafting |
| `style_guidance` | editing_polish | Strong local drafting |
| `summarize_chapter` | summarization | Lightweight summarization |
| `summarize_section` | summarization | Lightweight summarization |
| `research_note_summary` | editing_polish* | Lightweight summarization (recommended) |
| `vault_retrieval_summary` | editing_polish* | Lightweight summarization (recommended) |
| `expand` | writing_assist | Fast local creative |
| `change_tone` | writing_assist | Fast local creative |
| `continue_draft` | writing_assist | Strong local drafting |
| `generate_examples` | writing_assist | Fast local creative |
| `help_when_stuck` | writing_assist | Fast local creative |
| `notes_to_prose` | writing_assist | Strong local drafting |
| `create_hook` | writing_assist | Fast local creative |
| `create_conclusion` | writing_assist | Fast local creative |
| `suggest_chapter_names` | writing_assist | Fast local creative |
| `title_brainstorm` | fiction_ideation | Fast local creative |
| `blurb_copy` | ghostwriting | Copywriting specialist |
| `generate_section` | ghostwriting | Premium cloud reasoning |
| `freeform_creative` | general | Default writing |

\* `research_note_summary` and `vault_retrieval_summary` currently map to `editing_polish`; consider remapping to `summarization` for lighter model routing.

## Related

- [TASK_MODEL_DEFAULTS.md](./TASK_MODEL_DEFAULTS.md) — Detailed task-to-model defaults
- [OLLAMA_MULTI_MODEL_ROUTING.md](./OLLAMA_MULTI_MODEL_ROUTING.md) — Ollama model routing
- [LOCAL_FIRST_MODE.md](./LOCAL_FIRST_MODE.md) — Routing modes
- [PRIVACY_FIRST_AI_MODE.md](./PRIVACY_FIRST_AI_MODE.md) — Privacy modes
