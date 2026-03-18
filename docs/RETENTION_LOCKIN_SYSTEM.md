# Retention & Lock-in System

Product lock-in systems to increase retention and reduce churn.

---

## 1. Retention System Summary

### Project persistence
- Project data stored in `projects` table
- `template_id` exposed in `ProjectResponse` for template linkage
- `last_accessed_at` updated on project GET for recency and sorting

### Progress tracking
- **GET `/projects/{id}/progress`** — returns:
  - `total_words`, `total_chapters`, `chapters_done`
  - `progress_pct` (chapter completion percentage)
  - Per-book stats: `word_count`, `chapter_count`, `chapters_done`
- `last_accessed_at` updated on project access for “recent activity” sorting

### Resume session (continue where you left off)
- **POST `/projects/resume-session`** — records current project, book, chapter
- **GET `/projects/resume`** — returns valid resume session if &lt; 14 days old
- Stored in `user_preferences.preferences["resume_session"]`
- Validates access: project, book, chapter must exist and user must have access

### AI personalization storage
- Stored in `user_preferences.preferences["ai_personalization"]`
- Used by AI actions for style, tone, and voice consistency
- Endpoints: `/auth/ai-personalization` (get/update/learn/reset)

### Template dependency
- Projects created from templates have `template_id`
- `get_template_info_for_project()` returns template metadata for lock-in context
- Template purchases unlock access to creator-paid templates

---

## 2. Lock-in Strategy Summary

| Mechanism | Purpose |
|-----------|---------|
| **Resume session** | One-click “Continue writing” on dashboard; deep link to exact chapter |
| **Project persistence** | All work saved; `last_accessed_at` for recency |
| **Progress tracking** | Visible momentum; progress_pct and word counts |
| **AI personalization** | Learned style increases switching cost |
| **Template dependency** | Projects tied to purchased templates; re-use value |

### Seamless return experience
- Dashboard fetches `/projects/resume` and shows “Continue writing” when valid
- Link format: `/dashboard/projects/{id}/books/{bookId}?chapter={chapterId}`
- Book studio reads `?chapter=` and selects that chapter on load

### Fast loading
- Resume session: single DB read from `user_preferences`
- Progress: aggregated from chapters; no heavy joins
- Project list: supports `last_accessed_at` sort for quick access to recent work

---

## 3. Production-Ready Confirmation

### User data securely stored
- [x] Resume session in `user_preferences` (user-scoped)
- [x] AI personalization in `user_preferences` (user-scoped)
- [x] Project/chapter access validated before storing resume session
- [x] No sensitive data in URL; chapter ID is UUID

### Seamless return experience
- [x] Dashboard “Continue writing” when resume session &lt; 14 days
- [x] Deep link `?chapter=` selects correct chapter on book load
- [x] Resume session updated on chapter change in book studio

### Fast loading
- [x] Resume: single query
- [x] Progress: aggregated from existing chapter data
- [x] No blocking calls on critical paths

### API surface
- [x] `POST /projects/resume-session` — record current chapter
- [x] `GET /projects/resume` — get resume session
- [x] `GET /projects/{id}/progress` — project progress
- [x] `ProjectResponse.template_id` — template linkage

### Frontend
- [x] Dashboard fetches resume and passes to `DashboardQuickStart`
- [x] Book studio records resume on `activeChapter` change
- [x] Book studio reads `?chapter=` and selects chapter on load

---

## Key Files

| Area | Path |
|------|------|
| Service | `apps/api/authora/services/retention_lockin_service.py` |
| API | `apps/api/authora/api/routes/projects.py` |
| Schema | `apps/api/authora/schemas/project.py` |
| Dashboard | `apps/web/src/app/dashboard/page.tsx` |
| Quick start | `apps/web/src/components/onboarding/DashboardQuickStart.tsx` |
| Book studio | `apps/web/src/app/dashboard/projects/[id]/books/[bookId]/page.tsx` |
