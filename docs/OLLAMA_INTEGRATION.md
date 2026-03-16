# Ollama Integration

First-class local LLM support via Ollama.

## Overview

Ollama provides local inference for AUTHORA. Users can run models on their machine or a shared server without sending content to the cloud.

## Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `OLLAMA_ENABLED` | false | Enable Ollama provider |
| `OLLAMA_BASE_URL` | http://localhost:11434 | Ollama API URL |
| `OLLAMA_MODEL_DEFAULT` | (tier-based) | Default model when not task-specific |
| `OLLAMA_HARDWARE_TIER` | (auto) | 1-4 for model size recommendations |

## Model Discovery

- `GET /api/tags` on Ollama returns installed models
- Admin: `GET /admin/ai/providers/ollama/models` lists models
- Admin can enable/disable models via allowlist (future)

## Task Routing to Ollama

Each task maps to a role; each role maps to an Ollama model:

| Role | Typical model |
|------|---------------|
| quick_assist_model | qwen3:4b |
| default_writing_model | qwen3:8b |
| premium_drafting_model | qwen3:14b |
| fiction_ideation_model | qwen3:8b |
| editing_polish_model | qwen3:8b |

Admin can override via `PUT /admin/ai/model-roles` or env vars.

## Connectivity

- **Test**: `POST /admin/ai/providers/ollama/test` with custom base URL
- **Health**: `GET /admin/ai/providers/ollama/health`
- **Timeout**: 120s for generation; 10s for model list

## Deployment Modes

- **Local**: User runs Ollama on same machine as AUTHORA
- **Server-side**: AUTHORA server connects to Ollama on internal network
- **Remote**: `OLLAMA_BASE_URL` can point to another host (e.g. http://ollama-server:11434)

## Streaming

Ollama supports streaming via `/api/chat` with `stream: true`. AUTHORA uses it for real-time token delivery.

## Graceful Failure

- Connection errors → fallback to next provider in chain (if cloud configured)
- Timeout → retry up to 3 times, then fallback
- Model not found → use default model for role

## Model Capability Tagging

Hardware tier (1-4) determines recommended model sizes. Tier 1 = low RAM; Tier 4 = high VRAM. See `hardware_model_mapping.py`.
