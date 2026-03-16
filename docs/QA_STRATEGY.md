# AUTHORA QA Strategy

Production validation strategy covering unit, integration, end-to-end, smoke, regression, permission, AI, billing, deployment, and backup/restore testing.

## Test Pyramid

```
                    ┌─────────────┐
                    │   E2E / UI  │  Playwright, critical flows
                    ├─────────────┤
                    │ Integration │  API + DB, cross-service
                    ├─────────────┤
                    │    Unit     │  Services, utils, models
                    └─────────────┘
```

## Test Types

| Type | Location | Scope | Tools |
|------|----------|-------|-------|
| Unit | `apps/api/tests/test_*.py` | Services, models, utils | pytest |
| Integration | `apps/api/tests/test_*.py` | API + DB, auth, billing | pytest, httpx |
| E2E | `apps/web/e2e/*.spec.ts` | User flows, UI | Playwright |
| Smoke | `apps/web/e2e/smoke.spec.ts` | Health, login, basic nav | Playwright |
| Regression | `apps/api/tests/`, `apps/web/e2e/` | Full suite | pytest + playwright |
| Permission | `apps/api/tests/test_permissions.py` | RBAC, project access | pytest |
| AI | `apps/api/tests/test_ai_*.py` | Routing, fallback, timeouts | pytest |
| Billing | `apps/api/tests/test_billing.py` | Entitlements, limits, Stripe | pytest |
| Deployment | `scripts/validate-deploy.sh` | Bootstrap, health, env | bash |
| Backup/Restore | `scripts/validate-backup.sh` | Backup, restore drill | bash |

## Coverage Areas

### Frontend
- Auth flows (login, register, logout)
- Onboarding, setup wizard
- Project creation, template selection
- Manuscript editor, autosave
- AI assist, guidance mode
- Export, collaboration UI
- Billing status, upgrade prompts

### Backend
- Auth/session handling
- Project CRUD, permissions
- Book/chapter CRUD
- Notes, comments, highlights
- AI actions, provider routing
- Export generation (DOCX, PDF, EPUB)
- Billing entitlements, limits
- Admin routes, grants, promo codes
- Stripe webhook verification

### Workers/Jobs
- Background export jobs
- Reminder cron
- Usage aggregation (if any)

### Database
- Migrations apply cleanly
- Constraints, indexes
- Transaction boundaries

### AI Orchestration
- Provider routing (OpenAI, Anthropic, Ollama)
- Local-only mode
- Fallback behavior
- Timeout handling

### Stripe/Webhook
- Signature verification
- Event handling (checkout, subscription)
- Idempotent processing

### Collaboration/Permissions
- Invite flow, expiry
- Role scopes (owner, editor, beta, client)
- Private notes visibility

### Admin
- Admin-only routes protected
- Grants, promo codes, audit log

### Deployment/Runtime
- Health endpoints
- Env validation
- Bootstrap idempotency

## Running Tests

```bash
# API unit + integration
cd apps/api && pytest

# API with coverage
cd apps/api && pytest --cov=authora

# Web unit (Vitest)
cd apps/web && npm run test

# E2E (Playwright)
cd apps/web && npm run test:e2e

# Smoke only
cd apps/web && npx playwright test smoke.spec.ts

# Full validation
./scripts/validate-all.sh
```

## Test Data

- Use `conftest.py` fixtures: `test_user`, `admin_user`, `auth_client`, `admin_client`
- Isolate tests: rollback after each test
- No shared mutable state

## E2E Flow Scenarios

See [E2E_FLOW_SCENARIOS.md](E2E_FLOW_SCENARIOS.md) for launch-critical flows.

## Related

- [PRODUCTION_HARDENING](PRODUCTION_HARDENING.md)
- [RELEASE_GATES](RELEASE_GATES.md)
- [LAUNCH_DAY_CHECKLIST](LAUNCH_DAY_CHECKLIST.md)
