# AUTHORA Monitoring Guide

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Liveness – app is running |
| `GET /health/ready` | Readiness – DB and Redis connected |

Use `/health` for liveness probes, `/health/ready` for readiness/load balancer.

## Docker Health Checks

Containers include health checks. View status:

```bash
docker compose ps
```

## Metrics to Monitor

1. **API**
   - Response time (p95, p99)
   - Error rate (5xx)
   - Request rate

2. **Database**
   - Connection count
   - Query latency
   - Replication lag (if applicable)

3. **Redis**
   - Memory usage
   - Connected clients
   - Hit rate

4. **System**
   - CPU, memory, disk
   - Network I/O

## Logging

- API: structlog JSON to stdout (Docker captures)
- View: `docker compose logs -f api`
- Production: ship to centralized logging (Loki, ELK, Datadog)

## Alerting Recommendations

- API `/health/ready` returns 503
- Disk > 80% full
- PostgreSQL down
- Redis down
- High error rate (> 1%)

## Uptime Checks

Use UptimeRobot, Pingdom, or similar:

- `https://api.authora.studio/health` every 5 min
- Alert on 2+ consecutive failures
