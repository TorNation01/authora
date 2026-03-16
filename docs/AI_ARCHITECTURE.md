# AUTHORA AI Architecture

How AI works in AUTHORA: modular service layer, provider abstraction, and end-to-end flows.

---

## Overview

AUTHORA uses a **modular AI service layer**—not ad hoc UI calls. All AI flows go through:

1. **Frontend** → AI action UI (AIActionPanel, AIWritingPanel, AIDrawer, GhostwriterQuestionnaire)
2. **Backend** → AI action endpoints (`/api/v1/ai/actions`, `/api/v1/ai/complete`, ghostwriter, fiction, nonfiction)
3. **AI service layer** → `ai_service.py` (orchestration, provider, logging)
4. **Prompt builder** → `ai_orchestration.py` (modes, actions, templates)
5. **Provider adapter** → `ai_provider.py` + `infrastructure/ai_provider/` (OpenAI, Anthropic)
6. **Usage/accounting** → `AIActionLog`, billing `record_usage`
7. **Revision history** → `AIRevision`, accept/reject flow

---

## AI Modes

| Mode | ID | Description |
|------|-----|-------------|
| Assist | `assist` | Light suggestions, preserve user voice |
| Co-Write | `co_write` | Collaborative, moderate changes |
| Ghostwriter | `ghostwriter` | Full generation from brief |
| Edit | `editing` | Improve existing text, minimal creativity |
| Spark | `spark` | Creative brainstorming |

---

## Assistance Levels

| Level | ID | Description |
|-------|-----|-------------|
| Strict | `strict` | Minimal changes |
| Moderate | `moderate` | Balanced |
| Creative | `creative` | More freedom |

---

## AI Capabilities (Actions)

All actions support fiction, nonfiction, and general book types with tuned prompts.

| Action | Uses selection | Uses context |
|--------|----------------|--------------|
| rewrite_sentence | ✓ | |
| rewrite_paragraph | ✓ | |
| improve_wording | ✓ | |
| improve_flow | ✓ | |
| expand | ✓ | |
| condense | ✓ | |
| change_tone | ✓ | |
| continue_draft | ✓ | |
| generate_outline | | ✓ |
| generate_scene_ideas | | ✓ |
| generate_chapter_ideas | | ✓ |
| generate_examples | ✓ | |
| summarize_chapter | ✓ | |
| suggest_chapter_names | ✓ | |
| fix_transitions | ✓ | |
| create_hook | | ✓ |
| create_conclusion | ✓ | |
| help_when_stuck | ✓ | |
| notes_to_prose | ✓ | |
| generate_section | | ✓ |

---

## Provider Layer

**Location:** `apps/api/authora/infrastructure/ai_provider/` and `services/ai_provider.py`

- **Base:** `AIProvider` interface (`complete`, `complete_stream`)
- **OpenAI:** Primary provider (`gpt-4o-mini` default)
- **Anthropic:** Alternative (`claude-3-haiku` default)
- **Null:** No-op when no API key
- **Factory:** `get_ai_provider()` / `get_provider()` from config (`AI_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)

Future providers (Gemini, local) can be added by implementing the interface and registering in the factory.

---

## AI Service Layer

**Location:** `apps/api/authora/services/ai_service.py`

- `complete_stream(prompt, system_prompt, max_tokens)` → yields chunks
- `complete_sync(prompt, system_prompt, max_tokens)` → `AICompletionResult` (text, provider, model, tokens)
- `log_ai_action(...)` → writes to `ai_action_log`
- `create_revision(...)` → writes to `ai_suggestions` (AIRevision)
- `is_ai_configured()` → checks for API keys

All AI entry points (ai.py, ai_actions, ghostwriter, fiction, nonfiction) use this layer or the provider directly.

---

## Prompt Builder

**Location:** `apps/api/authora/services/ai_orchestration.py`

- `ACTION_DEFINITIONS` — action IDs with fiction/nonfiction/general prompts
- `build_user_prompt(action_id, book_type, selection, context, extra)`
- `build_system_prompt(mode, level, book_type, workspace_context)`
- `build_workspace_context(db, book_id, book_type, chapter_id)` — fiction/nonfiction context
- `MODE_SYSTEM_PREFIXES` — mode-specific system instructions
- `ASSISTANCE_LEVEL_HINTS` — strict/moderate/creative hints

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/ai/actions` | GET | List available actions |
| `/api/v1/ai/actions/run` | POST | Run action (streaming) |
| `/api/v1/ai/actions/revisions` | POST | Record accept/reject |
| `/api/v1/ai/actions/revisions` | GET | List revision history |
| `/api/v1/ai/complete` | POST | Free-form completion (streaming) |
| `/api/v1/projects/{id}/books/{id}/fiction/ai` | POST | Fiction prompts |
| `/api/v1/projects/{id}/books/{id}/nonfiction/ai` | POST | Nonfiction prompts |
| `/api/v1/projects/{id}/books/{id}/ghostwriter/*` | POST | Ghostwriter flow |

---

## Data Models

### AIActionLog

Tracks every AI invocation for usage and audit.

- `user_id`, `project_id`, `book_id`, `chapter_id`
- `action_id`, `mode`
- `provider`, `model`, `input_tokens`, `output_tokens`
- `status`, `created_at`

### AIRevision (ai_suggestions)

Stores AI suggestions for accept/reject and history.

- `chapter_id`, `user_id`, `project_id`, `book_id`
- `action_id`, `original_text`, `suggested_text`
- `status` (pending | accepted | rejected)
- `provider`, `model`, `input_tokens`, `output_tokens`
- `created_at`

---

## User Flow

1. **Select text** (or provide context) in the editor
2. **Choose action** (e.g. "Improve wording") and mode/level
3. **Run** → POST `/api/v1/ai/actions/run` → streaming response
4. **Review** → Suggestion shown in panel
5. **Accept** → Insert into editor; optionally POST `/api/v1/ai/actions/revisions` with status=accepted
6. **Reject** → Dismiss; optionally POST with status=rejected
7. **Compare** → CompareVersionsDialog (original vs suggested)

---

## Ghostwriter Flow

1. Intake questionnaire
2. Generate outline (AI)
3. Approve outline
4. Generate chapter briefs (AI)
5. Approve briefs
6. Generate draft (AI)
7. Apply draft to chapter
8. Regenerate section / rewrite with feedback (AI)

---

## Safety and Limits

- **Rate limit:** `ai_safety.check_rate_limit(user_id)` — per-user, per-minute
- **Prompt filter:** `ai_safety.filter_prompt(prompt)` — content safety
- **Billing:** When `feature_billing` is on, `check_ai_action_limit` and `record_usage` apply

---

## Configuration

| Env var | Purpose |
|---------|---------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `AI_PROVIDER` | `openai` or `anthropic` |
| `AI_MODEL` | Model name (e.g. `gpt-4o-mini`) |

---

## File Reference

| Path | Purpose |
|------|---------|
| `services/ai_service.py` | Unified AI service |
| `services/ai_orchestration.py` | Modes, actions, prompts |
| `services/ai_provider.py` | Provider wrapper, complete_with_retry |
| `services/ai.py` | Legacy fallback (used when no provider) |
| `services/ai_safety.py` | Rate limit, prompt filter |
| `services/fiction_ai.py` | Fiction context, prompts |
| `services/nonfiction_ai.py` | Nonfiction context |
| `services/ghostwriter_ai.py` | Ghostwriter prompts |
| `infrastructure/ai_provider/` | Provider implementations |
| `api/routes/ai_actions.py` | AI actions API |
| `api/routes/ai.py` | Free-form completion API |
| `models/ai_revision.py` | Revision model |
| `models/ai_action_log.py` | Action log model |
