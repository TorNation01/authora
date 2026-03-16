# AI Deployment Configuration

Production-ready deployment and runtime configuration for AUTHORA's server-hosted AI backend.

## Overview

- **Secrets** — Store in environment or secret manager; never in code or logs
- **Healthchecks** — Use `/health`, `/health/ready`, `/health/ai` for probes
- **Startup validation** — API validates AI config at startup; logs degraded mode if needed
- **Graceful degradation** — If some providers fail, others are used; app stays up

## Environment Setup

### Development

```bash
# .env
DATABASE_URL=postgresql://...
SECRET_KEY=...
OPENAI_API_KEY=sk-...          # Optional
ANTHROPIC_API_KEY=sk-ant-...   # Optional
OLLAMA_ENABLED=true            # Optional; local
OLLAMA_BASE_URL=http://localhost:11434
AI_PROVIDER_MODE=auto
```

### Staging

```bash
AUTHORA_ENV=staging
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_ENABLED=false           # Or true if staging has Ollama
AI_PROVIDER_MODE=local_first   # Prefer local when available
AI_RETRY_COUNT=3
AI_FALLBACK_ENABLED=true
```

### Production

```bash
AUTHORA_ENV=production
OPENAI_API_KEY=sk-...          # From secret manager
ANTHROPIC_API_KEY=sk-ant-...   # From secret manager
OLLAMA_ENABLED=true            # If self-hosted
OLLAMA_BASE_URL=http://ollama:11434
AI_PROVIDER_MODE=auto
AI_CLOUD_DISABLED=false
AI_LOCAL_ONLY=false
AI_OPENAI_TIMEOUT=60
AI_ANTHROPIC_TIMEOUT=60
AI_OLLAMA_TIMEOUT=120
AI_RETRY_COUNT=3
```

## Secret Management

### Docker

```bash
docker run -e OPENAI_API_KEY="$(cat /run/secrets/openai_key)" ...
```

### Kubernetes

```yaml
env:
  - name: OPENAI_API_KEY
    valueFrom:
      secretKeyRef:
        name: authora-ai-secrets
        key: openai-api-key
```

### Cloud Run / AWS / Vercel

Use the platform's secret or environment variable UI. Never commit secrets.

## Health Endpoints

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /health` | No | Liveness |
| `GET /health/ready` | No | Readiness (DB, Redis) |
| `GET /health/ai` | No | AI availability (for probes) |
| `GET /admin/ai/providers/health` | Admin | Per-provider health |
| `GET /admin/ai/providers/ollama/health` | Admin | Ollama only |
| `GET /admin/ai/providers/openai/health` | Admin | OpenAI only |
| `GET /admin/ai/providers/anthropic/health` | Admin | Anthropic only |

## Startup Validation

On startup, the API:

1. Resolves `AUTHORA_ENV` (development/staging/production)
2. Logs which AI providers are configured
3. Validates key format (no raw keys in logs)
4. Warns if no provider is available
5. Warns if config exists but validation fails

## Graceful Degraded Mode

- **No providers** — AI actions return 503; app otherwise works
- **Some providers down** — Fallback to next provider in chain
- **Local-only mode** — If Ollama is down, requests fail (no cloud fallback)
- **Cloud disabled** — Only Ollama used; 503 if Ollama down

## Server-Hosted AI Backend

For self-hosted Ollama alongside the API:

1. Run Ollama on same host or dedicated machine
2. Set `OLLAMA_BASE_URL` to reach it (e.g. `http://ollama:11434` in Docker)
3. Set `OLLAMA_ENABLED=true`
4. Pull models: `ollama pull qwen3:4b`, etc.
5. Optionally set `OLLAMA_HARDWARE_TIER` to match hardware

## Per-Task Routing

- **Env** — `OLLAMA_MODEL_QUICK_ASSIST`, `OLLAMA_MODEL_DEFAULT_WRITING`, etc.
- **Admin** — `PUT /admin/ai/model-roles` for DB overrides
- **Project/User** — Per-book `ai_prefs`, user `preferences.ai_prefs`

See [RUNTIME_MODEL_CONFIG.md](./RUNTIME_MODEL_CONFIG.md) and [OLLAMA_MULTI_MODEL_ROUTING.md](./OLLAMA_MULTI_MODEL_ROUTING.md).

## Checklist

- [ ] `SECRET_KEY` changed from default
- [ ] `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` or `OLLAMA_ENABLED=true`
- [ ] `OLLAMA_BASE_URL` correct if using Ollama
- [ ] `AUTHORA_ENV=production` in production
- [ ] Secrets from secret manager, not plain env files in prod
- [ ] Health probes configured (`/health`, `/health/ready`, `/health/ai`)

## Related

- [AI_ENV_CONFIGURATION.md](./AI_ENV_CONFIGURATION.md) — Env var reference
- [PROVIDER_HEALTHCHECKS.md](./PROVIDER_HEALTHCHECKS.md) — Health endpoints
- [RUNTIME_MODEL_CONFIG.md](./RUNTIME_MODEL_CONFIG.md) — Model routing
- [OLLAMA_SETUP.md](./OLLAMA_SETUP.md) — Ollama installation
