# AUTHORA Post-Deploy Smoke Tests

Run these after deployment to verify core functionality.

## Automated (Playwright)

```bash
cd apps/web
npm run test:e2e -- smoke.spec.ts
```

## Manual Checklist

| Test | Steps | Expected |
|------|-------|----------|
| Health | `curl https://api.your-domain/health` | `{"status":"ok"}` |
| Readiness | `curl https://api.your-domain/health/ready` | `{"status":"ready"}` |
| Login | Open web, login | Redirect to dashboard |
| Register | Open web, register new user | Account created |
| Create project | Dashboard → New project | Project created |
| Write chapter | Open book, add chapter, type | Content saved |
| Export | Export → DOCX | File downloads |
| Billing status | /billing (if enabled) | Plan displayed |

## Domain-Live Verification

```bash
./scripts/verify-go-live.sh https://api.your-domain.com https://your-domain.com
```

Checks: API health, readiness, CORS, SECRET_KEY not default.
