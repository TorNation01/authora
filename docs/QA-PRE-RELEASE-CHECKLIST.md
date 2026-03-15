# AUTHORA Pre-Release Checklist

Complete before tagging a release or deploying to staging.

---

## Code & Tests

- [ ] All API tests pass: `npm run test:api`
- [ ] All web unit tests pass: `npm run test` (apps/web)
- [ ] E2E smoke tests pass: `npm run test:e2e`
- [ ] Lint passes: `npm run lint`
- [ ] Build succeeds: `npm run build`
- [ ] No console errors in dev

## Dependencies

- [ ] `npm run audit` – no high/critical
- [ ] `pip-audit` (API) – no known vulnerabilities
- [ ] Dependencies up to date or documented

## Configuration

- [ ] `.env.example` current
- [ ] SECRET_KEY not default in production
- [ ] CORS_ORIGINS set for production domain
- [ ] Database migrations applied

## Documentation

- [ ] README accurate
- [ ] API docs (OpenAPI) current
- [ ] Changelog updated
- [ ] Security checklist reviewed

## Deployment

- [ ] Local deploy works: `npm run bootstrap:dev`
- [ ] Production deploy script tested
- [ ] Health endpoints respond
- [ ] Backup/restore verified

## Sign-Off

- [ ] Regression checklist completed
- [ ] Manual QA checklist completed
- [ ] Known issues documented
- [ ] Stakeholder approval
