# AUTHORA Prioritized Completion Plan

**Date:** 2025-03-15

## Priority 1: Critical (Implement Now)

### 1.1 Add PATCH /me API
- **File:** `apps/api/authora/api/routes/auth.py`
- **Action:** Add `PATCH /me` for display_name; add `PATCH /me/password` for password change
- **Dependencies:** None

### 1.2 Upgrade Settings Page
- **File:** `apps/web/src/app/dashboard/settings/page.tsx`
- **Action:** Add edit mode for display_name; add password change form; remove "managed by administrator" when standalone
- **Dependencies:** 1.1

### 1.3 Fix SSO Page
- **File:** `apps/web/src/app/(auth)/sso/page.tsx`
- **Action:** Replace TODO with clear message; when sso_ready=false redirect to login; when true show "SSO not yet configured"
- **Dependencies:** None

### 1.4 Add Playwright
- **File:** `apps/web/package.json`
- **Action:** Add `@playwright/test` to devDependencies
- **Dependencies:** None

## Priority 2: High (Implement Soon)

### 2.1 Document Admin Workarounds
- **File:** `docs/ADMIN.md`
- **Action:** Add section on user management via API, seed, setup wizard
- **Dependencies:** None

## Priority 3: Deferred

### 3.1 Password Reset Flow
- **Action:** Requires email service, token storage. Defer to post-MVP.
- **Dependencies:** SMTP or SendGrid

### 3.2 Admin UI
- **Action:** Full admin panel. Defer; document workarounds.
- **Dependencies:** None

### 3.3 Background Workers
- **Action:** Export is sync; acceptable. Reminders need cron. Document manual cron setup.
- **Dependencies:** None
