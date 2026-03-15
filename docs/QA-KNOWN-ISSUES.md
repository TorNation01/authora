# AUTHORA Known Issues

**As of:** March 2025

---

## Blocking / High

_None._ Web unit test dependencies (`@testing-library/jest-dom`, `@testing-library/react`) have been added to package.json. Run `npm install` then `npm run test`. 

---

## Medium

| ID | Issue | Impact | Mitigation |
|----|-------|--------|------------|
| K2 | API tests require PostgreSQL/Redis for full run | 48 tests skip when DB unavailable | Run with DB in CI; document local setup |
| K3 | E2E tests require dev server | Manual start or webServer config | Use Playwright webServer in CI |
| K4 | Tokens in localStorage (XSS exposure) | Security risk if XSS | Document; consider httpOnly cookies |

---

## Low

| ID | Issue | Impact | Mitigation |
|----|-------|--------|------------|
| K5 | No automatic token refresh on 401 | User must re-login when token expires | Manual refresh or re-auth |
| K6 | In-memory rate limit (single worker) | Multi-worker deployments share no state | Use Redis-backed rate limit for scale |
| K7 | Cron endpoint open when CRON_SECRET unset | Reminder cron could be invoked by anyone | Set CRON_SECRET in production |

---

## Resolved / Documented

| ID | Issue | Resolution |
|----|-------|------------|
| — | Default SECRET_KEY in production | Config validator warns; documented |
| — | Stack traces in 500 responses | Global handler returns generic message |
| — | Path traversal in file uploads | Validation added |
