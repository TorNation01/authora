# Ollama Setup

Ollama provides local/self-hosted LLMs for AUTHORA. No API keys required.

## Prerequisites

- [Ollama](https://ollama.com) installed on the machine that runs the AUTHORA API (or a reachable host)

## Installation

### macOS / Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Windows

Download from [ollama.com](https://ollama.com/download).

## Pull Models

```bash
ollama pull llama3.2
ollama pull mistral
ollama pull codellama
```

List installed models:

```bash
ollama list
```

## Configuration

| Env | Default | Description |
|-----|---------|-------------|
| `OLLAMA_ENABLED` | `false` | Set to `true` to enable Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL_DEFAULT` | `llama3.2` | Default model when no task-specific model is set |

### Task-Specific Models

Map different Ollama models to AUTHORA tasks:

| Env | Task |
|-----|------|
| `OLLAMA_MODEL_WRITING_ASSIST` | Writing assist, expand, continue |
| `OLLAMA_MODEL_FICTION_IDEATION` | Fiction outlines, scene ideas |
| `OLLAMA_MODEL_NONFICTION_STRUCTURE` | Nonfiction structure, outlines |
| `OLLAMA_MODEL_GHOSTWRITING` | Ghostwriter drafts |
| `OLLAMA_MODEL_EDITING_POLISH` | Editing, polish, grammar |

Example:

```env
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_DEFAULT=llama3.2
OLLAMA_MODEL_GHOSTWRITING=mistral
OLLAMA_MODEL_EDITING_POLISH=codellama
```

## Server Deployment

When AUTHORA runs on a server and Ollama runs on the same host:

1. Set `OLLAMA_BASE_URL=http://localhost:11434` (default).
2. Remote clients connect to the AUTHORA API; the API calls Ollama locally.
3. **No Ollama on client devices** — all AI runs server-side.

When Ollama runs on a different host:

```env
OLLAMA_BASE_URL=http://ollama-host:11434
```

Ensure the AUTHORA server can reach `ollama-host:11434` (firewall, network).

## Setup Wizard

The setup wizard (standalone mode) includes an Ollama step:

1. Select **Ollama (local)** as AI provider.
2. Enter base URL (default `http://localhost:11434`).
3. Click **Test Ollama connection** to validate.

## Health Check

Admin endpoint:

```
GET /api/v1/admin/ai/providers/ollama/health
```

Returns `{ "ok": true, "message": "Ollama is reachable" }` or an error.

## Model Refresh

To sync the list of available Ollama models in the admin UI:

```
GET /api/v1/admin/ai/providers/ollama/models
```

Or use the **Refresh models** button on the Admin → AI providers page.
