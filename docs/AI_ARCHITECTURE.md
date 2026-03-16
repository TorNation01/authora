# AI Architecture

AUTHORA's modular, provider-agnostic AI engine for writer-facing assistance.

## Overview

The AI layer is designed to:

- **Separate provider logic from application logic** — providers implement a standard interface
- **Support multiple providers** — OpenAI, Anthropic, Ollama, future (Google/Gemini)
- **Support local and cloud** — hybrid deployment, local-first when configured
- **Route by task** — each writing task maps to an appropriate model
- **Respect user and project preferences** — per-book AI settings, plan-based access
- **Remain extensible** — new providers, tasks, and tools can be added without rebuilding

## Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **Provider abstraction** | `services/ai_provider.py`, `infrastructure/ai_provider/` | Standard interface for text generation |
| **Provider registry** | `services/ai_registry.py` | Multi-provider support, task routing, fallback chain |
| **Model role registry** | `services/model_role_registry.py` | Task → role → model mapping |
| **Hardware model mapping** | `services/hardware_model_mapping.py` | Tier-based Ollama model recommendations |
| **Task catalog** | `services/ai_task_catalog.py` | Formal task definitions with metadata |
| **Orchestration** | `services/ai_orchestration.py` | Prompt building, modes, actions |
| **Context assembly** | `services/ai_context_assembly.py` | Intelligent context for prompts |
| **AI service** | `services/ai_service.py` | Execution, logging, revisions |

## Architecture Diagram

```
User Request (action_id, selection, context)
       │
       ▼
┌──────────────────┐
│  AI Actions API  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│  AI Orchestration│────▶│  Task Catalog   │
│  (prompts, modes)│     │  (metadata)     │
└────────┬─────────┘     └─────────────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│ Context Assembly │────▶│  RAG (optional) │
└────────┬─────────┘     └─────────────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────┐
│  AI Registry     │────▶│  Model Roles    │
│  (routing)       │     │  (Ollama/cloud) │
└────────┬─────────┘     └─────────────────┘
         │
         ▼
┌──────────────────┐
│  Provider        │  OpenAI | Anthropic | Ollama
│  (complete_stream)│
└──────────────────┘
```

## Key Interfaces

### AIProvider

```python
class AIProvider(ABC):
    @property
    def name(self) -> str: ...

    async def complete_stream(self, prompt, system_prompt, max_tokens, **kwargs) -> AsyncGenerator[str, None]: ...
    async def complete(self, prompt, system_prompt, max_tokens, **kwargs) -> AIResponse: ...
```

### Routing Flow

1. `action_id` → `task` (via `action_to_task`)
2. `task` → `role` (via `task_to_role`)
3. `get_provider_for_task(task, project_prefs, ...)` → `(provider, model, provider_name)`
4. Fallback chain via `get_fallback_chain` on failure

## Deployment Modes

- **Server-hosted**: Shared AI backend, OpenAI/Anthropic or self-hosted Ollama
- **Standalone**: Local Ollama only, no cloud
- **Hybrid**: Local-first with cloud fallback

## Related

- [AI_PROVIDER_SYSTEM.md](./AI_PROVIDER_SYSTEM.md)
- [OLLAMA_INTEGRATION.md](./OLLAMA_INTEGRATION.md)
- [MODEL_ROUTING.md](./MODEL_ROUTING.md)
