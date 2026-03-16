# Provider Healthchecks

Healthcheck endpoints for AUTHORA's AI providers.

## Public Endpoints (No Auth)

### GET /health

**Purpose:** Liveness probe.

**Response:**
```json
{"status": "ok", "app": "AUTHORA", "version": "1.0.0"}
```

### GET /health/ready

**Purpose:** Readiness probe. Checks database and Redis.

**Response (200):**
```json
{
  "status": "ready",
  "checks": {"database": true, "redis": true},
  "app": "AUTHORA",
  "version": "1.0.0"
}
```

**Response (503):** When DB or Redis fails.

### GET /health/ai

**Purpose:** AI availability for load balancers and probes. Does not require auth.

**Response:**
```json
{
  "ai_available": true,
  "providers_configured": ["openai", "ollama"],
  "status": "ok"
}
```

- `ai_available`: `true` if at least one provider is configured
- `providers_configured`: List of provider names that are enabled
- `status`: `"ok"` if available, `"degraded"` if none configured

**Note:** This does not verify connectivity; it only reports configuration. Use admin endpoints for connectivity checks.

## Admin Endpoints (Require Admin Auth)

### GET /admin/ai/providers/health

**Purpose:** Aggregated health for all configured AI providers. Performs connectivity checks.

**Response:**
```json
{
  "providers": {
    "openai": {"ok": true, "message": "reachable"},
    "anthropic": {"ok": false, "message": "not configured"},
    "ollama": {"ok": true, "message": "Ollama is reachable"}
  },
  "any_available": true,
  "degraded": false
}
```

- `any_available`: At least one provider is reachable
- `degraded`: Some providers configured but none reachable

### GET /admin/ai/providers/ollama/health

**Purpose:** Ollama connectivity only.

**Response:**
```json
{"ok": true, "message": "Ollama is reachable"}
```

### GET /admin/ai/providers/openai/health

**Purpose:** OpenAI connectivity (lightweight models list).

**Response:**
```json
{"ok": true, "message": "OpenAI is reachable"}
```

### GET /admin/ai/providers/anthropic/health

**Purpose:** Anthropic connectivity (lightweight models list).

**Response:**
```json
{"ok": true, "message": "Anthropic is reachable"}
```

## Kubernetes Probes

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5

# Optional: custom probe for AI-dependent workloads
aiProbe:
  httpGet:
    path: /health/ai
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 30
```

## Docker Compose

```yaml
api:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
```

## What Each Check Does

| Endpoint | Checks |
|----------|--------|
| `/health` | App is running |
| `/health/ready` | DB and Redis connectivity |
| `/health/ai` | At least one AI provider configured |
| `/admin/ai/providers/health` | Actual API calls to OpenAI, Anthropic, Ollama |
| `/admin/ai/providers/ollama/health` | GET to Ollama `/api/tags` |
| `/admin/ai/providers/openai/health` | OpenAI `models.list()` |
| `/admin/ai/providers/anthropic/health` | Anthropic `GET /v1/models` |

## Related

- [AI_DEPLOYMENT_CONFIG.md](./AI_DEPLOYMENT_CONFIG.md) — Deployment setup
- [AI_ENV_CONFIGURATION.md](./AI_ENV_CONFIGURATION.md) — Env configuration
