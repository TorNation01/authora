# AUTHORA CI Pipeline

Continuous integration pipeline for lint, type checks, tests, builds, and deployment quality gates.

## Overview

| Trigger | Workflow | Purpose |
|---------|----------|---------|
| Pull request | `ci.yml` | Fast-fail on critical errors; block merge if gates fail |
| Push to `main` | `ci.yml` | Full validation before merge |
| Tag `v*` | `release.yml` (optional) | Release validation, artifact build, release notes |

## Pipeline Stages

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Lint      │ → │  Type Check │ → │  Unit/Int   │ → │   Build     │ → │   E2E       │
│  (fast)     │   │  (fast)     │   │  (API+Web)  │   │  (Web+API)  │   │  (smoke)    │
└─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
       │                  │                  │                  │                  │
   Fast-fail          Fast-fail          Fast-fail          Fast-fail          Gate
```

**Fast-fail:** Critical errors stop the pipeline immediately. Non-critical jobs may run in parallel.

## Jobs

### 1. Lint Checks

| Target | Command | Notes |
|-------|---------|------|
| Web (ESLint) | `npm run lint --workspace=apps/web` | Next.js ESLint config |
| API | `cd apps/api && ruff check .` or `pip install ruff && ruff check .` | Optional; add when adopted |
| All workspaces | `npm run lint --workspaces --if-present` | Runs workspace linters |

**Current:** `npm run lint --workspaces --if-present` (root package.json)

### 2. Type Checks

| Target | Command | Notes |
|-------|---------|------|
| Web | `cd apps/web && npx tsc --noEmit` | TypeScript strict |
| API | `cd apps/api && mypy authora` | Optional; add when adopted |

**Current:** Web type-check via `next build` (implicit). Add explicit `tsc --noEmit` for faster feedback.

### 3. Unit & Integration Tests

| Target | Command | Dependencies |
|--------|---------|--------------|
| API | `cd apps/api && pytest tests/ -v --tb=short` | PostgreSQL, Redis |
| Web | `cd apps/web && npm run test` | None (Vitest, jsdom) |

**API test env:**
```bash
DATABASE_URL=postgresql://authora:authora@localhost:5432/authora_test
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=test-secret
DEPLOYMENT_MODE=standalone
```

### 4. Build Validation

| Target | Command |
|--------|---------|
| Web | `npm run build --workspace=apps/web` |
| API | `pip install -e apps/api` (or build wheel) |

### 5. Docker Build Validation

```bash
docker compose build api web
```

Validates Dockerfiles and build context. Does not run containers.

### 6. E2E Smoke Tests

| Target | Command | Notes |
|-------|---------|-------|
| Smoke | `cd apps/web && npm run test:e2e -- smoke.spec.ts` | Requires web + API running |

**E2E requirements:**
- Web server on `PLAYWRIGHT_BASE_URL` (default `http://localhost:3000`)
- API reachable from web (via `NEXT_PUBLIC_API_URL`)
- In CI: Start services via `docker compose up -d` or use Playwright's `webServer` (dev server)

### 7. Env/Config Validation

```bash
source .env && ./scripts/validate-env.sh development
```

For production validation (pre-deploy):
```bash
source .env && ./scripts/validate-env.sh production
```

### 8. Migration Validation

```bash
cd apps/api && alembic upgrade head
cd apps/api && alembic check  # Optional: detect autogenerate drift
```

Validates migrations apply cleanly. Run against test DB in CI.

## GitHub Actions Configuration

**Current workflow:** `.github/workflows/ci.yml`

| Job | Runs On | Services |
|-----|---------|----------|
| lint | ubuntu-latest | — |
| api-test | ubuntu-latest | postgres:16 |
| web-build | ubuntu-latest | — |
| docker-build | ubuntu-latest | — |

**Gaps to address:**
- [ ] Add Redis service for API tests (or mock/skip Redis-dependent tests)
- [ ] Add explicit type-check job (tsc --noEmit)
- [ ] Add E2E smoke job (with docker compose or Playwright webServer)
- [ ] Add env validation job
- [ ] Add migration validation job
- [ ] Add `validate-all` or release gate job for tagged releases

## Deployment Pipeline Hooks

Optional integration points for deployment systems:

| Hook | When | Action |
|------|------|--------|
| Pre-deploy | Before `deploy.sh` | Run `./scripts/validate-all.sh $API_URL` |
| Post-deploy | After deploy | Run `./scripts/healthcheck.sh $API_URL` |
| Rollback | On failure | Run `./scripts/rollback.sh $BACKUP prod` |

**Example (GitHub Actions deploy job):**
```yaml
deploy:
  needs: [lint, api-test, web-build, docker-build]
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - run: ./scripts/deploy.sh prod
    - run: ./scripts/healthcheck.sh ${{ env.API_URL }}
```

## Test Failure Visibility

- **PR checks:** All jobs must pass. Failures block merge.
- **Branch protection:** Require `lint`, `api-test`, `web-build`, `docker-build` before merge.
- **Annotations:** Use `$GITHUB_*` env for error reporting (e.g. `::error file=...`).
- **Artifacts:** Upload Playwright report, pytest JUnit XML for dashboards.

## Clear Output for Maintainers

- Use `--tb=short` for pytest to keep traces concise.
- Use `-v` for verbose test names.
- Group related jobs; use descriptive job names.
- Add `continue-on-error` only for non-blocking checks (e.g. optional audit).

## See Also

- [TEST_MATRIX](TEST_MATRIX.md) – Test coverage and matrix
- [RELEASE_WORKFLOW](RELEASE_WORKFLOW.md) – Tagged releases and artifacts
- [QUALITY_GATES](QUALITY_GATES.md) – Gate definitions and pass criteria
