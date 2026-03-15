# AUTHORA Production Risk Checklist

Risks and mitigations for production operation.

---

## High Priority

| Risk | Mitigation | Status |
|------|------------|--------|
| Default SECRET_KEY in production | Config validator warns; must set `SECRET_KEY` | Implemented |
| Cron endpoint open when CRON_SECRET unset | Set `CRON_SECRET` when using cron; endpoint rejects if secret configured but missing | Documented |
| Stack traces in 500 responses | Global handler returns generic message; logs internally | Implemented |
| PII in error responses | All handlers use generic `detail`; no paths/DB errors to client | Implemented |

---

## Medium Priority

| Risk | Mitigation | Status |
|------|------------|--------|
| Tokens in localStorage (XSS) | Consider httpOnly cookies for refresh; document XSS hygiene | Documented |
| In-memory rate limit (single worker) | Use Redis-backed rate limit for multi-worker deployments | Documented |
| No automatic token refresh on 401 | Frontend redirects to login; consider refresh flow | Documented |
| No session revocation on password change | Future: invalidate refresh tokens on password change | Backlog |

---

## Lower Priority

| Risk | Mitigation | Status |
|------|------------|--------|
| No magic-byte file validation | MIME + extension + path traversal; add magic bytes for stricter | Optional |
| CORS origins too permissive | Restrict to production domain(s) | Config |
| No CSP header | Add Content-Security-Policy at reverse proxy | Optional |
| API docs exposed | Disable or restrict in production | Config |

---

## Operational

| Risk | Mitigation |
|------|------------|
| Single point of failure | Run multiple API workers; use managed DB/Redis |
| No distributed rate limit | Redis-backed rate limit for horizontal scaling |
| Log volume | Configure log aggregation (Loki, CloudWatch, etc.) |
| Backup integrity | Regular restore tests |

---

## Compliance Notes

- **Audit logs:** `AuditLog` model; ensure retention meets requirements
- **PII:** No PII in error responses; audit logs may contain IP/path
- **Data residency:** DB and storage location for regulated data
