# AUTHORA Test Matrix

Test coverage, execution matrix, and failure handling for all test suites.

## Test Categories

| Category | Scope | Framework | Location | CI Job |
|----------|-------|-----------|----------|--------|
| Lint | Code style, patterns | ESLint | apps/web | lint |
| Type check | TypeScript types | tsc | apps/web | (via build) |
| Unit (Web) | Components, utils | Vitest | apps/web | (test) |
| Unit (API) | Services, models | pytest | apps/api/tests | api-test |
| Integration (API) | Routes, DB, auth | pytest | apps/api/tests | api-test |
| E2E smoke | Pages, auth redirect | Playwright | apps/web/e2e | (optional) |
| E2E full | Auth, dashboard | Playwright | apps/web/e2e | (optional) |

## API Test Matrix

| Test File | Focus | Dependencies | Skip Condition |
|-----------|-------|--------------|----------------|
| test_auth.py | Login, signup, tokens | DB, Redis | DB unavailable |
| test_permissions.py | RBAC, project access | DB | DB unavailable |
| test_projects.py | CRUD, listing | DB | DB unavailable |
| test_books.py | Books, chapters | DB | DB unavailable |
| test_export.py | Export service | DB | DB unavailable |
| test_health.py | /health, /health/ready | None | — |
| test_security.py | Rate limit, CORS | None | — |
| test_setup.py | Setup wizard | DB, Redis | DB/Redis unavailable |
| test_billing.py | Billing routes | DB, admin | DB unavailable |
| test_invite_accept.py | Invite accept flow | DB | DB unavailable |
| test_notes.py | Notes CRUD | DB | DB unavailable |
| test_ai_actions.py | AI routes | DB | DB unavailable |
| test_ghostwriter.py | Ghostwriter service | DB | DB unavailable |
| test_fiction_nonfiction.py | Workspace types | DB | DB unavailable |
| test_accountability.py | Accountability | DB | DB unavailable |
| test_gamification.py | Gamification | DB | DB unavailable |
| test_journey.py | Journey/roadmap | DB | DB unavailable |
| test_env_validation.py | Config validation | None | — |
| test_file_validation.py | File upload | DB | DB unavailable |

**Run all API tests:**
```bash
cd apps/api
DATABASE_URL=postgresql://authora:authora@localhost:5432/authora_test \
REDIS_URL=redis://localhost:6379/1 \
SECRET_KEY=test-secret \
pytest tests/ -v --tb=short
```

**Run specific subset:**
```bash
pytest tests/test_health.py tests/test_security.py -v  # No DB
pytest tests/test_auth.py -v -k "login"               # Filter by name
```

## Web Test Matrix

| Test Type | Location | Command | Notes |
|-----------|----------|---------|-------|
| Unit | `*.test.tsx`, `*.test.ts` | `npm run test --workspace=apps/web` | Vitest, jsdom |
| E2E smoke | e2e/smoke.spec.ts | `npm run test:e2e -- smoke.spec.ts` | Playwright |
| E2E auth | e2e/auth.spec.ts | `npm run test:e2e -- auth.spec.ts` | Playwright |
| E2E dashboard | e2e/dashboard.spec.ts | `npm run test:e2e -- dashboard.spec.ts` | Playwright |

**E2E smoke tests (no auth):**
- Landing page loads
- Login page loads
- Register page loads
- Pricing, features, contact pages
- Dashboard redirects to login when unauthenticated
- 404 page renders

## Environment Matrix

| Env | PostgreSQL | Redis | Use Case |
|-----|------------|-------|----------|
| CI (minimal) | ✓ (service) | — | api-test; some tests skip if Redis missing |
| CI (full) | ✓ | ✓ | All API tests |
| Local dev | ✓ | ✓ | Full suite |
| Docker | postgres + redis | ✓ | E2E with compose |

**CI recommendation:** Add Redis service to api-test job for full coverage. Tests that require Redis may skip when unavailable (check conftest).

## Parallelization

| Suite | Parallel | Workers | Notes |
|-------|----------|---------|-------|
| API pytest | Yes | auto | Session-scoped DB; per-test rollback |
| Web Vitest | Yes | auto | Isolated |
| Playwright | Yes (CI: 1) | 1 in CI | Avoid port conflicts |
| Lint | N/A | 1 | Fast |
| Build | N/A | 1 | Sequential |

## Fast-Fail Strategy

| Stage | Fast-Fail | Continue on Fail |
|-------|-----------|------------------|
| Lint | ✓ | — |
| Type check | ✓ | — |
| API tests | ✓ | — |
| Web build | ✓ | — |
| Docker build | ✓ | — |
| E2E smoke | ✓ | — |
| E2E full | — | Optional (slower) |

**Critical path:** Lint → Type → API tests → Build → Docker. E2E can run after or in parallel with build.

## Test Failure Visibility

| Output | Format | Consumer |
|--------|--------|----------|
| Pytest | stdout, JUnit XML | CI, IDE |
| Vitest | stdout | CI |
| Playwright | HTML report, trace | CI artifacts |
| ESLint | stdout, SARIF (optional) | CI, PR annotations |

**JUnit XML (pytest):**
```bash
pytest tests/ -v --tb=short --junitxml=report.xml
```

**Playwright report:**
```bash
npm run test:e2e -- --reporter=html
# Report in playwright-report/
```

## Coverage (Future)

| Target | Tool | Command |
|--------|------|---------|
| API | pytest-cov | `pytest --cov=authora --cov-report=xml` |
| Web | Vitest coverage | `vitest run --coverage` |

Add coverage gates when adopted (e.g. fail if coverage drops below threshold).

## See Also

- [CI_PIPELINE](CI_PIPELINE.md) – Pipeline stages and jobs
- [RELEASE_WORKFLOW](RELEASE_WORKFLOW.md) – Release validation
- [QUALITY_GATES](QUALITY_GATES.md) – Gate definitions
