# AUTHORA Checklists

## CSRF Strategy

AUTHORA uses **token-based auth** (JWT in `Authorization: Bearer`) for API calls. CSRF is mitigated by:

- **SameSite cookies** (if any): Set `SameSite=Strict` or `Lax` for session cookies.
- **No cookie-based auth for API**: Primary auth is Bearer token in header; browsers do not automatically send custom headers on cross-site requests.
- **CORS**: API restricts `allow_origins` to known frontend origins; credentials allowed only for same-origin or whitelisted origins.
- **State-changing requests**: All POST/PUT/DELETE require `Authorization` header; GET is idempotent.

For forms that post to the API, ensure the frontend sends the token in the `Authorization` header (not in a cookie). No additional CSRF token is required for this architecture.

---

## Idempotency & Retry Safety

- **GET**: All read endpoints are idempotent and safe to retry.
- **POST create**: Project, book, chapter, note create endpoints generate new IDs; retries may create duplicates. Use idempotency keys for critical flows if needed.
- **PUT/PATCH**: Update endpoints are idempotent; last write wins.
- **DELETE**: Idempotent (204 or 404 on re-delete).
- **Autosave**: Editor autosave uses debouncing; duplicate requests within the debounce window are acceptable.
- **Export**: Export endpoints generate fresh output each call; retries are safe but may incur extra cost.

---

## Complete QA Checklist

### Functional

- [ ] **Auth**: Register, login, logout, refresh token, password validation
- [ ] **Projects**: Create, list, update, delete
- [ ] **Books**: Create, list, update, delete, reorder chapters
- [ ] **Chapters**: Create, edit, delete, content persistence
- [ ] **Editor**: TipTap editor loads, formatting, headings, lists
- [ ] **Ghostwriter**: Generate draft, approve, reject
- [ ] **AI actions**: Rewrite, expand, suggest (with/without API key)
- [ ] **Export**: DOCX, PDF, EPUB, TXT, outline, chapters ZIP
- [ ] **Notes**: Create, search, tag, attach to book
- [ ] **Accountability**: Settings, goals, reminders
- [ ] **Gamification**: Stats, achievements, quests
- [ ] **Onboarding**: Flow completes, redirects correctly
- [ ] **Setup wizard**: All steps, validation, finalize

### Non-Functional

- [ ] **Performance**: Page load < 3s, API response < 500ms (p95)
- [ ] **Accessibility**: Keyboard nav, focus, screen reader basics
- [ ] **Responsive**: Mobile, tablet, desktop
- [ ] **Browser**: Chrome, Firefox, Safari, Edge

### Security

- [ ] **Auth**: Protected routes return 401 without token
- [ ] **Ownership**: Users cannot access other users' projects/books
- [ ] **Input**: XSS, SQL injection attempts rejected
- [ ] **File upload**: Blocked types rejected, size limits enforced

---

## Pre-Release Checklist

### Code

- [ ] All tests pass (`npm run test`, `pytest`)
- [ ] Lint passes (`npm run lint`)
- [ ] No console errors in production build
- [ ] TypeScript strict mode passes
- [ ] No hardcoded secrets or debug code

### Build & Deploy

- [ ] Docker images build successfully
- [ ] Environment variables documented
- [ ] Migrations run cleanly
- [ ] Health endpoints return 200

### Data

- [ ] Backup taken before release
- [ ] Rollback procedure documented
- [ ] Seed data (if any) verified

### Documentation

- [ ] CHANGELOG updated
- [ ] API changes documented
- [ ] Deployment steps current

---

## Go-Live Checklist

### Pre-Launch (T-24h)

- [ ] Final backup
- [ ] SSL certificates valid
- [ ] DNS propagated
- [ ] Monitoring configured
- [ ] Alert contacts set

### Launch (T-0)

- [ ] Deploy to production
- [ ] Run migrations
- [ ] Smoke test: landing, login, create project
- [ ] Verify health endpoints
- [ ] Check logs for errors

### Post-Launch (T+1h)

- [ ] Monitor error rates
- [ ] Verify backups running
- [ ] User feedback channel ready

---

## Production Readiness Checklist

### Security

- [ ] SECRET_KEY is strong (32+ chars, random)
- [ ] Database password is strong
- [ ] No default credentials
- [ ] CORS restricted to known origins
- [ ] Rate limiting enabled
- [ ] Secure headers (X-Content-Type-Options, etc.)
- [ ] HTTPS enforced

### Reliability

- [ ] Restart policy: unless-stopped
- [ ] Health checks on all services
- [ ] Persistent volumes for DB, Redis, storage
- [ ] Backup cron configured
- [ ] Restore tested

### Observability

- [ ] Logging to stdout (or centralized)
- [ ] Request ID on responses
- [ ] Audit log for sensitive actions
- [ ] Uptime monitoring
- [ ] Error alerting

### Operations

- [ ] Runbook for common incidents
- [ ] Rollback procedure documented
- [ ] Update procedure documented
- [ ] Contact for outages
