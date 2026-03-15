# AUTHORA Gap Analysis

**Date:** 2025-03-15

## 1. Critical Gaps (Blocking Production)

| Gap | Area | Impact | Effort |
|-----|------|--------|--------|
| No user profile edit | Settings | Users cannot update display name | Low |
| No password change | Settings | Users cannot change password | Low |
| SSO page is stub | Auth | Confusing when sso_ready=true | Low |
| E2E tests fail | Tests | test:e2e broken (Playwright missing) | Low |

## 2. High-Priority Gaps (Should Fix)

| Gap | Area | Impact | Effort |
|-----|------|--------|--------|
| Settings copy misleading | Settings | "Managed by administrator" when standalone | Low |
| No PATCH /me API | Backend | Frontend cannot update user | Low |

## 3. Medium-Priority Gaps (Nice to Have)

| Gap | Area | Impact | Effort |
|-----|------|--------|--------|
| No admin UI | Admin | User management via API/DB only | High |
| No password reset | Auth | Users must contact admin if forgotten | Medium |
| CLI wizard limited | Setup | Web wizard is primary; CLI for env only | Low |
| No background workers | Jobs | Export synchronous; reminders need cron | Medium |

## 4. Low-Priority Gaps (Future)

| Gap | Area | Impact | Effort |
|-----|------|--------|--------|
| Per-user AI keys | AI | Currently global env; acceptable | High |
| Queue implementation | Jobs | EVENTS-QUEUES design not implemented | High |
| Minimal unit tests | Tests | One component test | Medium |

## 5. Root Cause Summary

| Root Cause | Affected Areas |
|------------|----------------|
| Auth API lacks PATCH /me | Settings |
| SSO not implemented | Auth |
| Playwright not in package.json | Tests |
| Admin UI never built | Admin |
| Workers/queues design only | Jobs |
