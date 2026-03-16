# AUTHORA Worker

Background job processor for async tasks. **Currently optional** — AUTHORA export runs synchronously via the API.

## Current State

- **Export**: Handled synchronously by `GET /api/v1/export/books/{id}/{format}`. No worker required.
- **Reminders**: Handled by cron calling `POST /api/v1/accountability/cron/reminders`. No worker required.
- **Worker**: Listens to `authora:queue:export` but `run_export_job` is a stub. Not deployed in Docker Compose.

## When to Use the Worker

Add worker to deployment when:
- Implementing async export for large books (avoid timeouts)
- Adding other background jobs (e.g. AI processing, batch operations)

## Running Locally

```bash
cd apps/worker
REDIS_URL=redis://localhost:6379/0 python -m authora_worker.main
```

## Production

Worker is not in `docker-compose.yml`. To add: create `Dockerfile.worker`, add worker service, ensure Redis is available.
