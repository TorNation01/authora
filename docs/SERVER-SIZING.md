# AUTHORA Server Sizing Guide

## Development

| Resource | Minimum |
|----------|---------|
| CPU | 2 cores |
| RAM | 4 GB |
| Disk | 20 GB SSD |
| Network | 10 Mbps |

## Production – Small (1–50 users)

| Resource | Minimum |
|----------|---------|
| CPU | 2 cores |
| RAM | 4 GB |
| Disk | 40 GB SSD |
| Network | 50 Mbps |

- Single server with Docker Compose
- PostgreSQL, Redis, API, Web on same host
- Suitable for personal/small team use

## Production – Medium (50–500 users)

| Resource | Minimum |
|----------|---------|
| CPU | 4 cores |
| RAM | 8 GB |
| Disk | 100 GB SSD |
| Network | 100 Mbps |

- Consider separate DB host
- Redis can stay on app server
- Enable connection pooling (default: pool_size=5)

## Production – Large (500+ users)

| Resource | Minimum |
|----------|---------|
| App servers | 2+ (load balanced) |
| DB server | 4 cores, 16 GB RAM |
| Redis | Dedicated or managed (e.g. Redis Cloud) |
| Disk | 200+ GB SSD for DB |

- Use managed PostgreSQL (RDS, Cloud SQL, etc.)
- Use managed Redis
- Horizontal scaling for API and Web
- CDN for static assets

## Docker Resource Limits

Example for medium deployment:

```yaml
api:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
      reservations:
        memory: 512M

web:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
```

## Database Sizing

- ~1 KB per user (metadata)
- ~10–50 KB per chapter (content)
- Plan for 2–3x growth
- Regular `VACUUM ANALYZE` recommended
