# Security Architecture

## Authentication

- **JWT access tokens**: Short-lived (60 min), stored in memory / Authorization header
- **Refresh tokens**: Long-lived (7 days), hashed in DB, httpOnly cookie or secure storage
- **Password hashing**: bcrypt, cost factor 12
- **OAuth**: Optional; store provider tokens encrypted

## Authorization

- **Resource ownership**: user_id / tenant_id on all scoped resources
- **Middleware**: Verify JWT → load user → attach to request
- **Dependency**: `get_current_user`, `require_project_access`, `require_admin`
- **Admin**: `is_admin` flag; admin routes protected

## Data Protection

- **TLS**: All external connections over HTTPS
- **DB**: Use SSL for connections in production
- **Storage**: S3/R2 server-side encryption (SSE-S3, SSE-KMS)
- **Secrets**: Never in code; env vars or secret manager

## Input Validation

- Pydantic on all API inputs
- File uploads: type allowlist, size limits (e.g. 10MB)
- SQL: SQLAlchemy ORM only; no raw SQL with user input

## Rate Limiting

- **Auth**: 5 login attempts / 15 min per IP
- **API**: 100 req/min per user (configurable)
- **AI**: 20 requests/min per user
- **Export**: 5 exports/hour per user

## Audit

- Log: user_id, action, resource, resource_id, ip, timestamp
- Redact: passwords, tokens, PII in logs
- Retention: 90 days default; configurable

## Headers

- `X-Request-ID`: Trace requests
- `Strict-Transport-Security`: HSTS
- `X-Content-Type-Options`: nosniff
- `Content-Security-Policy`: Restrict scripts, sources
