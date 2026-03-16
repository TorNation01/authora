# AUTHORA AI Provider Outage Runbook

Response procedures when AI providers (OpenAI, Anthropic, Ollama) are unavailable.

## Degraded Mode

AUTHORA supports degraded mode: when no AI provider is available, AI features are disabled but the app remains usable.

## OpenAI/Anthropic Outage

**Symptom**: AI actions fail with timeout or API error.

1. **Check health**
   ```bash
   curl https://api.your-domain/health/ai
   ```

2. **Options**
   - Wait for provider recovery
   - Enable Ollama (local) if available: `OLLAMA_ENABLED=true`
   - Set `AI_FALLBACK_ENABLED=true` to try next provider

3. **User communication**: Show clear error; suggest retry later

## Ollama Unavailable

**Symptom**: Local AI fails when `OLLAMA_ENABLED=true`.

1. **Check Ollama**
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. **Options**
   - Restart Ollama service
   - Disable: `OLLAMA_ENABLED=false` (fallback to cloud if configured)
   - User sees "Local AI unavailable" message

## Local-Only Mode Bypass Attempts

**Symptom**: Concern that cloud might be called when local-only.

- **Verify**: `AI_LOCAL_ONLY=true` and `AI_CLOUD_DISABLED=true` in env
- **Test**: Disable cloud keys; confirm only Ollama works
