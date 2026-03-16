# Prompt Orchestration

Structured prompt system for AUTHORA's AI features.

## Components

| Component | Location | Purpose |
|-----------|----------|---------|
| **AIMode** | ai_orchestration.py | assist, co_write, ghostwriter, editing, spark, idea_generation |
| **AssistanceLevel** | ai_orchestration.py | strict, moderate, creative |
| **BookType** | ai_orchestration.py | fiction, nonfiction, general |
| **ActionDefinition** | ai_orchestration.py | Per-action prompt templates |
| **MODE_SYSTEM_PREFIXES** | ai_orchestration.py | Mode-specific system instructions |
| **ASSISTANCE_LEVEL_HINTS** | ai_orchestration.py | Level-specific hints |

## Prompt Structure

**System prompt** = MODE_SYSTEM_PREFIX + ASSISTANCE_LEVEL_HINT + book_type hint + workspace_context

**User prompt** = action template (fiction/nonfiction/general) with {selection}, {context}, {tone} placeholders

## Mode Behavior

| Mode | Behavior |
|------|----------|
| assist | Light suggestions, preserve voice |
| co_write | Collaborative, moderate changes |
| ghostwriter | Full generation, mark AI content |
| editing | Improve text, minimal creativity |
| spark | Creative brainstorming |
| idea_generation | Alias for spark |

## Composable Prompts

- Prompts are built from templates, not scattered across codebase
- Templates use format strings: `{selection}`, `{context}`, `{tone}`
- Admin can override via config (future: prompt template management UI)

## Project-Type Awareness

- **Fiction**: Narrative voice, character, pacing
- **Nonfiction**: Clarity, logic, evidence
- **General**: Neutral assistance

## Versioning and Testing

- Templates live in `ACTION_DEFINITIONS` in ai_orchestration.py
- Changes are code-based; future: versioned prompt store for A/B testing
