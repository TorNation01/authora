# AUTHORA AI Co-Author System

Production-ready AI co-writing system. Users co-write books with AI while maintaining control.

---

## 1. AI Co-Author Summary

### Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Assist** | Light suggestions, preserve voice | Inline rewrites, word improvements |
| **Co-write** | Collaborative, moderate changes | Expand, continue draft, style suggestions |
| **Ghostwriter** | Full generation from brief | Chapter drafts, outlines, briefs |
| **Editing** | Improve text, minimal creativity | Clarity, flow, grammar |
| **Spark** | Creative brainstorming | Ideas, scene/chapter suggestions |

### Features

| Feature | Implementation | API |
|---------|----------------|-----|
| **Generate chapters** | Ghostwriter draft from brief | `POST /ghostwriter/briefs/{id}/generate`, `POST /ghostwriter/draft/generate` |
| **Expand outlines** | Outline → briefs → drafts | `POST /ghostwriter/outline/generate`, `POST /ghostwriter/outline/approve` |
| **Rewrite content** | rewrite_sentence, rewrite_paragraph | `POST /ai/actions/run` (action_id) |
| **Improve clarity** | improve_wording, improve_flow, fix_transitions | `POST /ai/actions/run` |
| **Style matching** | Voice/tone from intake, personalization | Ghostwriter intake, AI personalization |

### User Control

| Control | Implementation |
|---------|----------------|
| **Accept/reject AI output** | `POST /ai/revisions` with status `accepted` or `rejected` |
| **Edit AI content** | User edits before applying; apply draft optional in ghostwriter |
| **Adjust tone** | `change_tone` action with `extra.tone`; ghostwriter `voice_tone` |

### API Endpoints

- `GET /ai/actions` — List available actions
- `POST /ai/actions/run` — Run action (streaming); supports mode, level, preferred_provider
- `POST /ai/revisions` — Record accept/reject
- `GET /ai/revisions` — List revision history
- `POST /ai/complete` — Streaming completion (legacy)
- Ghostwriter: `/projects/{id}/books/{id}/ghostwriter/*` — intake, outline, briefs, draft

---

## 2. Model Routing Summary

### Providers

| Provider | Config | Fallback |
|----------|--------|----------|
| **OpenAI** | `OPENAI_API_KEY` | gpt-4o-mini, gpt-4o |
| **Anthropic** | `ANTHROPIC_API_KEY` | claude-3-haiku, claude-3-5-sonnet |
| **Ollama** | `OLLAMA_ENABLED`, `OLLAMA_BASE_URL` | qwen3:4b–14b by role |

### Task → Model Mapping

| Task | Ollama Role | Cloud (OpenAI) | Cloud (Anthropic) |
|------|-------------|----------------|-------------------|
| writing_assist | quick_assist | gpt-4o-mini | claude-3-haiku |
| ghostwriting | premium_drafting | gpt-4o | claude-3-5-sonnet |
| editing_polish | editing_polish | gpt-4o-mini | claude-3-haiku |
| fiction_ideation | fiction_ideation | gpt-4o-mini | claude-3-haiku |
| summarization | summarization | gpt-4o-mini | claude-3-haiku |

### Routing Modes

| Mode | Order |
|------|-------|
| `auto` / `local_first` | Ollama → OpenAI → Anthropic |
| `cloud` | OpenAI, Anthropic only |
| `local` / `privacy_first` | Ollama only (no cloud fallback) |
| `quality_first` | Cloud first, then Ollama |

### Per-Task Selection

- **Project prefs**: `ai_prefs.routing_mode`, `preferred_provider`, `preferred_model`
- **User prefs**: Same keys in user preferences
- **Request override**: `AIActionRequest.preferred_provider`, `preferred_model`
- **Admin overrides**: DB `ai_model_role_overrides` (admin panel)

### Fallback Logic

1. Resolve provider from mode + prefs
2. Try primary provider (with retries)
3. On failure, try next in fallback chain
4. `local` / `privacy_first`: no cloud fallback

---

## 3. Production-Ready Confirmation

### Checklist

- [x] Assist mode
- [x] Co-write mode
- [x] Ghostwriter mode
- [x] Generate chapters
- [x] Expand outlines
- [x] Rewrite content
- [x] Improve clarity
- [x] Style matching (voice/tone)
- [x] Accept/reject AI output
- [x] Edit AI content before applying
- [x] Adjust tone (change_tone action)
- [x] OpenAI support
- [x] Ollama (local) support
- [x] Anthropic support
- [x] Model selection per task
- [x] Fallback logic
- [x] Per-book AI preferences
- [x] Rate limiting
- [x] Usage logging (AIActionLog)
- [x] Revision history (AIRevision)

### Configuration

```bash
# At least one required
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434

# Optional
AI_PROVIDER_MODE=auto  # auto | local | cloud | local_first | quality_first
AI_MODEL=gpt-4o-mini   # Default cloud model
```

---

## See Also

- [ai_orchestration.py](../apps/api/authora/services/ai_orchestration.py) — Modes, actions, prompts
- [ai_registry.py](../apps/api/authora/services/ai_registry.py) — Provider routing, fallback
- [model_role_registry.py](../apps/api/authora/services/model_role_registry.py) — Task → model mapping
- [ghostwriter_ai.py](../apps/api/authora/services/ghostwriter_ai.py) — Outline, brief, draft generation
