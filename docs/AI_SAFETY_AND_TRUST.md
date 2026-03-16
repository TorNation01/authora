# AI Safety and Trust

Safety rules and trust controls for AUTHORA's AI assistance.

## Core Principles

1. **AI must not silently overwrite user writing** — Suggestions are explicit
2. **Original text preservable** — User can accept or reject
3. **Source-grounded tasks avoid fabricated citations** — Research/summary tasks use verified content
4. **Ghostwriting/copywriting clearly labeled** — AI-generated content marked
5. **Privacy mode respected** — Local-only when user selects
6. **Logs avoid exposing sensitive content** — Minimize manuscript content in logs

## Safeguards

### Hallucinated Source Support

- Research/summary tasks use RAG-retrieved or user-provided content
- Vault retrieval clearly marked as `[source_type]`
- No fabrication of citations or sources

### Overconfident Factual Claims

- Nonfiction mode emphasizes clarity and evidence
- Summarization tasks require factual grounding
- Style guidance avoids asserting false facts

### Style Drift

- `strict` and `moderate` assistance levels preserve voice
- System prompts instruct "preserve author's voice"
- User can reject suggestions

### Intrusive AI Takeover

- Suggestions are opt-in (user accepts/rejects)
- Continuation suggestions can be disabled per-book
- Rewrite shortcuts can be disabled

## Implementation

| Component | Location | Purpose |
|-----------|----------|---------|
| **Rate limit** | ai_safety.py | Per-user, per-minute (configurable) |
| **Prompt filter** | ai_safety.py | BLOCKED_PATTERNS (jailbreak, "ignore instructions") |
| **AI revision tracking** | AIRevision model | Accept/reject logged |
| **AIActionLog** | ai_action_log model | Provider, model, tokens; minimal content |

## Admin Controls

- Provider enable/disable
- Model allowlist/blocklist (Ollama)
- Task-to-model routing
- Plan-based AI access
- Local-only mode for users/projects
- Rate limiting configuration

## User Controls

Per-book `ai_prefs`:

- `ai_assistance_on` — Master switch
- `allow_continuation_suggestions` — On/off
- `allow_rewrite_shortcuts` — On/off
- `allow_brainstorming_helpers` — On/off
- `routing_mode` — privacy_first for local-only
