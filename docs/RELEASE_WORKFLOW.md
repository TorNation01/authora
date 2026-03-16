# AUTHORA Release Workflow

Tagged release validation, artifact build, and release notes generation.

## Overview

| Trigger | Workflow | Purpose |
|---------|----------|---------|
| Push to `main` | ci.yml | Pre-merge validation |
| Tag `v*` | release.yml | Release build, artifacts, notes |
| Manual | Scripts | Pre-release checks, deploy |

## Release Types

| Type | Tag Pattern | Example | Artifacts |
|------|-------------|---------|-----------|
| Semantic | `v*` | v1.0.0, v1.1.0-beta.1 | Docker images, tarballs |
| Pre-release | `v*-alpha`, `v*-beta`, `v*-rc` | v1.0.0-rc.1 | Same; marked pre-release |

## Tagged Release Workflow

### 1. Pre-Release Validation

Before tagging, run full validation:

```bash
# From repo root
npm ci
npm run lint --workspaces --if-present
cd apps/api && pytest tests/ -v --tb=short
npm run build --workspace=apps/web
docker compose build api web
source .env && ./scripts/validate-env.sh production
cd apps/api && alembic upgrade head
./scripts/validate-all.sh http://localhost:8000
```

### 2. Create Tag

```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

### 3. Release Pipeline (Optional GitHub Action)

On tag push `v*`:

1. **Validate** – Re-run CI (lint, test, build)
2. **Build artifacts** – Docker images, source tarball
3. **Generate release notes** – From commits since last tag
4. **Create GitHub Release** – Attach artifacts, publish notes

### 4. Release Notes Generation Readiness

**Sources for release notes:**

| Source | Format | Tool |
|--------|--------|------|
| Git commits | Conventional Commits | `git log v0.9.0..v1.0.0 --oneline` |
| CHANGELOG.md | Manual | Edit before release |
| PR titles | GitHub API | `gh pr list --state merged` |
| Tag comparison | GitHub Releases | Auto-generated "Compare" link |

**Conventional Commits (recommended):**
- `feat:` – New feature
- `fix:` – Bug fix
- `docs:` – Documentation
- `chore:` – Maintenance
- `BREAKING CHANGE:` – Breaking change

**Example release notes template:**
```markdown
## v1.0.0 (YYYY-MM-DD)

### Features
- feat: Add collaboration invite accept endpoint (#123)
- feat: Launch gate system documentation (#124)

### Fixes
- fix: Invite expiry handling for expired tokens (#122)

### Documentation
- docs: CI pipeline and quality gates (#125)
```

**Generation options:**
1. **Manual** – Maintain `CHANGELOG.md` or `docs/RELEASE_NOTES.md`
2. **Semantic Release** – `semantic-release` (Conventional Commits)
3. **GitHub CLI** – `gh release create v1.0.0 --generate-notes`
4. **Custom script** – `git log $(git describe --tags --abbrev=0)..HEAD --pretty=format:"- %s"`

### 5. Release Artifact Validation

| Artifact | Validation |
|----------|------------|
| Docker api | `docker run --rm authora-api:latest python -c "from authora.main import app; print('OK')"` |
| Docker web | `docker run --rm -p 3000:3000 authora-web:latest` → curl localhost:3000 |
| Source tarball | Extract, run `npm ci && npm run build` |

### 6. Post-Release

- [ ] Update `LAUNCH_GATE_SYSTEM.md` if process changed
- [ ] Notify stakeholders
- [ ] Deploy to production (see [LAUNCH_GATE_SYSTEM](LAUNCH_GATE_SYSTEM.md))

## Main Branch Release Validation

For continuous deployment from `main`:

| Check | When | Command |
|-------|------|---------|
| CI pass | Every push/PR | GitHub Actions |
| Health | Post-deploy | `./scripts/healthcheck.sh $API_URL` |
| Smoke | Post-deploy | Manual or E2E job |

**Branch protection (recommended):**
- Require PR reviews
- Require status checks: `lint`, `api-test`, `web-build`, `docker-build`
- Require branches to be up to date
- No force push to `main`

## Optional: release.yml Workflow

```yaml
# .github/workflows/release.yml (example)
name: Release

on:
  push:
    tags: ['v*']

jobs:
  validate:
    uses: ./.github/workflows/ci.yml
    # Reuse CI jobs

  build-artifacts:
    needs: validate
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build api web
      - run: docker save authora-api authora-web | gzip > authora-images.tar.gz
      - uses: actions/upload-artifact@v4
        with:
          name: docker-images
          path: authora-images.tar.gz

  release:
    needs: build-artifacts
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          files: artifacts/*.tar.gz
```

## See Also

- [CI_PIPELINE](CI_PIPELINE.md) – CI stages
- [QUALITY_GATES](QUALITY_GATES.md) – Gate definitions
- [LAUNCH_GATE_SYSTEM](LAUNCH_GATE_SYSTEM.md) – Production launch checklist
