# AUTHORA Production Hardening

Security hardening checklist and implementation guidance for production deployment.

## Auth & Session Security

| Item | Status | Notes |
|------|--------|-------|
| Secure cookies | ✓ | HttpOnly, SameSite where applicable |
| JWT expiry | ✓ | Configurable `access_token_expire_minutes` |
| Password hashing | ✓ | bcrypt |
| Session invalidation | ✓ | Refresh token rotation |
| Brute-force mitigation | ✓ | Rate limiting on auth endpoints |
| Admin route protection | ✓ | `is_admin` check |

## CSRF & CORS

| Item | Status | Notes |
|------|--------|-------|
| CORS policy | ✓ | `CORS_ORIGINS` from env |
| CSRF tokens | N/A | Stateless JWT; no CSRF for API |
| Secure headers | ✓ | Caddy: X-Content-Type-Options, X-Frame-Options, etc. |

## Secrets & Storage

| Item | Status | Notes |
|------|--------|-------|
| SECRET_KEY | ✓ | Must change from default |
| Env file | ✓ | Never commit .env |
| Stripe keys | ✓ | Test vs live separation |

## Rate Limiting

| Item | Status | Notes |
|------|--------|-------|
| Auth endpoints | ✓ | Rate limit applied |
| Health skip | ✓ | /health excluded from limit |
| API general | ✓ | Per-IP limits |

## Webhook & File Safety

| Item | Status | Notes |
|------|--------|-------|
| Stripe webhook signature | ✓ | Verified before processing |
| File upload validation | ✓ | Type, size limits |
| Export access | ✓ | Owner/collaborator only |

## Privilege Escalation Tests

- Non-admin cannot access `/api/v1/admin/*`
- Non-owner cannot access project/book without invite
- Expired invite cannot access
- Revoked user loses access on next request

## Security Review Checklist

- [ ] SECRET_KEY changed
- [ ] CORS_ORIGINS restricted to known origins
- [ ] Admin routes require is_admin
- [ ] Stripe webhook secret set
- [ ] Rate limiting enabled
- [ ] Secure headers (Caddy)
- [ ] No debug mode in production
