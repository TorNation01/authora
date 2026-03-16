# AUTHORA AI Failure Mode Testing

Red-team and failure-mode testing for the AI layer.

## Provider Routing

- **Local-only mode**: `AI_LOCAL_ONLY=true` — only Ollama; cloud never called
- **Cloud fallback**: Only when `AI_FALLBACK_ENABLED=true` and local fails
- **Timeout handling**: Provider timeout returns clear error

## Red-Team AI Cases

| Case | Expected |
|------|----------|
| Oversized prompts | Rejected or truncated; no crash |
| Malformed context | Graceful error |
| Unavailable model | Clear message; no silent fail |
| Conflicting provider config | Degraded mode or config error |
| Privacy-mode bypass | Local-only stays local |
| Excessive-cost path | Timeout/limit applied |

## Ollama Unavailable

- Degrades gracefully
- User sees "Local AI unavailable"
- No cloud fallback when `AI_LOCAL_ONLY=true`

## Acceptance/Rejection Flow

- AI suggestions are accepted or rejected by user
- No silent replacement of user writing
