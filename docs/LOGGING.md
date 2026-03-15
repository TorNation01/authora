# AUTHORA Logging Guide

## Log Output

- **API**: JSON logs to stdout (structlog)
- **Web**: Next.js default logs to stdout
- **Docker**: Captures stdout/stderr

## View Logs

```bash
# All services
docker compose logs -f

# API only
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api
```

## Log Levels

- **DEBUG**: Set `DEBUG=true` in .env (dev only)
- **INFO**: Default
- **WARNING**: Non-fatal issues
- **ERROR**: Failures

## Structured Logging (API)

The API uses structlog. Log format:

```json
{"event": "request", "method": "GET", "path": "/health", "level": "info", "timestamp": "..."}
```

## Production Logging

1. **Docker**: Logs go to journald or Docker logging driver
2. **File**: Add a volume and configure logging to file
3. **Centralized**: Use Fluentd, Filebeat, or Vector to ship to Loki, ELK, Datadog

## Sensitive Data

- Never log secrets, tokens, or passwords
- Redact `Authorization` headers in access logs
- Caddy/Nginx: Use `log_format` that excludes sensitive headers

## Log Retention

- Default: Docker retains logs (check `docker info` for driver)
- Configure: `logging.driver` in docker-compose
- Recommended: 7–30 days for app logs
