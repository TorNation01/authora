# Monitoring and Health

## Health Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Liveness – API process is running |
| `GET /health/ready` | Readiness – Database and Redis are reachable |

### Example

```bash
curl https://api.yourdomain.com/health
curl https://api.yourdomain.com/health/ready
```

## Health Check Script

```bash
./scripts/healthcheck.sh [base_url]
```

Default: `http://localhost:8000`

Example for production:

```bash
./scripts/healthcheck.sh https://api.yourdomain.com
```

Exit code 0 = healthy, 1 = unhealthy.

## Monitoring Recommendations

### Uptime Monitoring

Use an external service (e.g., UptimeRobot, Pingdom) to poll `/health` and `/health/ready` every 1–5 minutes.

### Logs

```bash
# API logs
docker compose logs -f api

# Web logs
docker compose logs -f web

# All services
docker compose logs -f
```

### Metrics

For production, consider:

- **Prometheus** – Scrape metrics from the API if exposed
- **Grafana** – Dashboards
- **Loki** – Log aggregation

### Alerts

Set up alerts for:

- Health check failures
- High error rates
- Disk space (PostgreSQL, storage)
- Memory/CPU usage
