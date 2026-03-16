# AUTHORA Quality Gates

Gate definitions, pass criteria, and blocking rules for CI and release.

## Gate Summary

| Gate | Blocking | Command | Pass Criteria |
|------|----------|---------|---------------|
| Lint | ✓ | `npm run lint --workspaces --if-present` | Exit 0 |
| Type check | ✓ | `npx tsc --noEmit` (web) | Exit 0 |
| Unit tests (API) | ✓ | `pytest tests/ -v --tb=short` | All pass |
| Unit tests (Web) | ✓ | `npm run test --workspace=apps/web` | All pass |
| Integration tests | ✓ | Same as API (pytest) | All pass |
| Web build | ✓ | `npm run build --workspace=apps/web` | Exit 0 |
| API build | ✓ | `pip install -e apps/api` | Exit 0 |
| Docker build | ✓ | `docker compose build api web` | Exit 0 |
| E2E smoke | ✓ | `npm run test:e2e -- smoke.spec.ts` | All pass |
| Env validation | ✓ | `./scripts/validate-env.sh $MODE` | Exit 0 |
| Migration validation | ✓ | `alembic upgrade head` | Exit 0 |
| Release artifact | ✓ (release) | Build + smoke | Images run |

## Gate Definitions

### 1. Lint Gate

**Purpose:** Enforce code style and catch common errors.

**Command:**
```bash
npm run lint --workspaces --if-present
```

**Pass:** No lint errors. Warnings may be allowed (config-dependent).

**Fail:** Any error-level finding. Fix before merge.

**Fast-fail:** Yes. Lint runs first; fails quickly.

---

### 2. Type Check Gate

**Purpose:** Ensure TypeScript types are valid.

**Command:**
```bash
cd apps/web && npx tsc --noEmit
```

**Pass:** No type errors.

**Fail:** Any type error. Fix before merge.

**Note:** `next build` includes type-check; explicit `tsc --noEmit` gives faster feedback.

**Fast-fail:** Yes.

---

### 3. Unit Test Gate (API)

**Purpose:** Validate business logic, services, models.

**Command:**
```bash
cd apps/api && pytest tests/ -v --tb=short
```

**Pass:** All tests pass. Skips (DB/Redis unavailable) are acceptable in minimal CI.

**Fail:** Any test failure. Fix or fix environment.

**Fast-fail:** Yes.

---

### 4. Unit Test Gate (Web)

**Purpose:** Validate components, hooks, utils.

**Command:**
```bash
npm run test --workspace=apps/web
```

**Pass:** All tests pass.

**Fail:** Any test failure.

**Fast-fail:** Yes.

---

### 5. Integration Test Gate

**Purpose:** Validate API routes, DB, auth, external integrations.

**Scope:** Covered by API pytest suite (test_*.py with DB/Redis).

**Pass:** All integration tests pass.

**Fail:** Any failure. Often indicates DB schema, env, or API contract issue.

**Fast-fail:** Yes.

---

### 6. Build Validation Gate

**Purpose:** Ensure app builds successfully.

**Commands:**
```bash
npm run build --workspace=apps/web
pip install -e apps/api  # or: cd apps/api && pip install -e .
```

**Pass:** Build completes without error.

**Fail:** Compile error, missing dependency, config error.

**Fast-fail:** Yes.

---

### 7. Docker Build Gate

**Purpose:** Validate Docker images build.

**Command:**
```bash
docker compose build api web
```

**Pass:** Both images build successfully.

**Fail:** Dockerfile error, COPY path wrong, dependency install fails.

**Fast-fail:** Yes.

---

### 8. E2E Smoke Gate

**Purpose:** Validate critical user paths without full auth.

**Command:**
```bash
cd apps/web && npm run test:e2e -- smoke.spec.ts
```

**Pass:** All smoke tests pass (landing, login, register, pricing, 404, dashboard redirect).

**Fail:** Page load failure, selector broken, timeout.

**Fast-fail:** Yes. E2E can be slow; run after faster gates.

**Prerequisite:** Web + API running (e.g. `docker compose up -d` or Playwright webServer).

---

### 9. Env/Config Validation Gate

**Purpose:** Ensure required env vars are set for target environment.

**Command:**
```bash
source .env && ./scripts/validate-env.sh development   # CI
source .env && ./scripts/validate-env.sh production    # Pre-deploy
```

**Pass:** No missing required vars; SECRET_KEY not default (prod/staging).

**Fail:** Missing DATABASE_URL, REDIS_URL, SECRET_KEY; or SECRET_KEY default in prod.

**Fast-fail:** Yes for release. Optional for PR (may not have .env).

---

### 10. Migration Validation Gate

**Purpose:** Ensure migrations apply cleanly.

**Command:**
```bash
cd apps/api && alembic upgrade head
```

**Pass:** Migrations apply without error.

**Fail:** Migration failure, schema conflict, downgrade needed.

**Fast-fail:** Yes for release.

**Note:** Run against clean or test DB. CI uses `alembic upgrade head` before pytest.

---

### 11. Release Artifact Gate

**Purpose:** Validate built artifacts run correctly.

**Checks:**
- Docker API: Start container, hit `/health`
- Docker Web: Start container, hit `/`
- Source: Extract tarball, build, run tests

**Pass:** Artifacts run and respond.

**Fail:** Image won't start, health fails, runtime error.

**When:** Tagged release workflow only.

---

## Blocking Rules

| Context | Blocking Gates |
|---------|----------------|
| **PR merge** | Lint, API tests, Web build, Docker build |
| **Push to main** | Same as PR |
| **Tagged release** | All gates + env validation + migration + artifact |
| **Deploy** | See [LAUNCH_GATE_SYSTEM](LAUNCH_GATE_SYSTEM.md) |

## Non-Blocking Checks

| Check | Purpose | Action on Fail |
|-------|---------|----------------|
| Dependency audit | Security | Warn in PR; do not block |
| Coverage report | Visibility | Publish; optional threshold |
| E2E full suite | Extended validation | Run nightly or manual |
| Performance test | Latency | Informational |

## Clear Output for Maintainers

- **Pytest:** `--tb=short` for concise traces; `-v` for test names
- **Playwright:** `--reporter=list` for CI; HTML report as artifact
- **ESLint:** Default output; `--max-warnings 0` to fail on warnings
- **Grouping:** Use GitHub Actions `::group::` for collapsible sections

## See Also

- [CI_PIPELINE](CI_PIPELINE.md) – Pipeline stages
- [TEST_MATRIX](TEST_MATRIX.md) – Test coverage
- [RELEASE_WORKFLOW](RELEASE_WORKFLOW.md) – Release process
- [LAUNCH_GATE_SYSTEM](LAUNCH_GATE_SYSTEM.md) – Production launch
