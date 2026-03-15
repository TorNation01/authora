# AUTHORA Multi-Project Support Report

**Date:** March 2025  
**Status:** Complete

---

## 1. How Multi-Project Support Works

### 1.1 Data Model

- **User** → owns many **Projects**
- **Project** → contains many **Books**
- **Book** → contains **Chapters**, **Notes**, **GhostwriterWorkspace**, **FictionWorkspace**, **NonfictionWorkspace**, **BookSettings**, etc.

Each project is fully isolated. All content (chapters, notes, outlines, AI history, goals, reminders, exports, progress, version history, settings) is scoped to the book, which belongs to a project.

### 1.2 Project Lifecycle

| State   | Meaning                          | `deleted_at`   |
|---------|----------------------------------|----------------|
| Active  | Visible in default list          | `NULL`         |
| Archived| Hidden from default, restorable  | timestamp set  |

---

## 2. Implemented Features

### 2.1 Create Multiple Projects

- **API:** `POST /api/v1/projects` with `{ name: string }`
- **Frontend:** "New project" button → `/dashboard/projects/new`
- **Limit:** Enforced by plan (projects count excludes archived)

### 2.2 Switch Between Projects

- **API:** `GET /api/v1/projects` returns user's projects
- **Frontend:** Dashboard grid of project cards; click to open `/dashboard/projects/{id}`
- **Navigation:** Project → Books → Editor/Ghostwriter/Plan

### 2.3 Dashboard Showing All Projects

- **API:** `GET /api/v1/projects?status=active|archived|all`
- **Frontend:** Dashboard lists projects with search, filters, and sort

### 2.4 Project Status Filters

- **API:** `?status=active` (default) | `archived` | `all`
- **Frontend:** Status dropdown (Active / Archived / All)

### 2.5 Archive Project

- **API:** `PATCH /api/v1/projects/{id}/archive` — sets `deleted_at`
- **Frontend:** Archive icon on project card (when status = active)
- **Effect:** Project hidden from default list; does not count toward project limit

### 2.6 Restore Project

- **API:** `PATCH /api/v1/projects/{id}/restore` — clears `deleted_at`
- **Frontend:** Restore icon on project card (when status = archived)

### 2.7 Duplicate Project

- **API:** `POST /api/v1/projects/{id}/duplicate` with optional `{ name?: string }`
- **Frontend:** Duplicate icon on project card
- **Copies:** Project, books, chapters, notes, ghostwriter workspace, fiction/nonfiction workspaces, book settings
- **Effect:** Creates new project; user is redirected to it

### 2.8 Delete Project with Safety Confirmation

- **API:** `DELETE /api/v1/projects/{id}?confirm=true` — requires `confirm=true`
- **Frontend:** Delete icon → confirmation dialog → delete
- **Effect:** Hard delete; cascades to books, chapters, notes, etc.

### 2.9 Search Projects

- **API:** `GET /api/v1/projects?q=...` — filters by project name (case-insensitive)
- **Frontend:** Search input with debounce

### 2.10 Sort Projects

- **API:** `GET /api/v1/projects?sort=updated_at|name|created_at|last_accessed_at`
- **Frontend:** Sort dropdown (Recently updated, Recently opened, Name, Date created)

### 2.11 Continue Recent Project

- **API:** `GET /api/v1/projects/recent` — returns most recently accessed project
- **Frontend:** "Continue writing" card at top when multiple projects exist
- **Tracking:** `last_accessed_at` updated on `GET /api/v1/projects/{id}`

### 2.12 Separate Analytics and Progress by Project

- **Progress:** Chapters, word counts, finish mode are per-book (book in project)
- **Gamification:** StreakLog, UserStats record `book_id`; progress is book-scoped
- **Finish mode:** Per-book settings and stats

### 2.13 Separate Accountability by Project

- **Writing plans:** Optional `book_id` — plans can be scoped to a book (in a project)
- **Milestones, recovery plans:** Optional `book_id`
- **Settings:** User-level (daily/weekly goals, style); plans are book-level

### 2.14 Separate Export History by Project

- **Export jobs:** `ExportJob` has `book_id`; each book has its own export history
- **API:** `GET /api/v1/export/books/{book_id}/export-history`
- **Project notes export:** `GET /api/v1/export/projects/{project_id}/notes`

---

## 3. Per-Project Isolation Checklist

| Item           | Scoped By | Location / Model                          |
|----------------|-----------|-------------------------------------------|
| Title          | Book      | `Book.title`                              |
| Metadata       | Book      | `Book.genre`, `Book.planner_data`         |
| Book type      | Book      | `Book.type` (fiction/nonfiction)         |
| Outline        | Book      | GhostwriterWorkspace, Fiction/Nonfiction   |
| Chapters       | Book      | `Chapter`                                 |
| Notes          | Project   | `Note.project_id`, `Note.book_id`         |
| AI history     | Chapter   | AIRevision, GhostwriterSession            |
| Goals          | Book      | WritingPlan, FictionWorkspace goals       |
| Reminders      | User      | Reminder (user-level; plans are book-level)|
| Exports        | Book      | `ExportJob.book_id`                       |
| Progress       | Book      | StreakLog, Finish mode, chapter status   |
| Version history| Chapter   | `ChapterVersion`                          |
| Settings       | Book      | `BookSettings`, finish mode               |

---

## 4. API Summary

| Method | Endpoint                          | Description                    |
|--------|-----------------------------------|--------------------------------|
| GET    | `/projects`                      | List projects (filter, search, sort) |
| GET    | `/projects/recent`               | Most recently accessed project |
| POST   | `/projects`                      | Create project                 |
| GET    | `/projects/{id}`                 | Get project (updates last_accessed_at) |
| PATCH  | `/projects/{id}`                 | Update project name            |
| PATCH  | `/projects/{id}/archive`         | Archive project                |
| PATCH  | `/projects/{id}/restore`         | Restore archived project       |
| POST   | `/projects/{id}/duplicate`       | Duplicate project              |
| DELETE | `/projects/{id}?confirm=true`    | Delete project (requires confirm) |

---

## 5. Fixes Applied

1. **Books routes:** Added missing `project_id` path parameter to handlers that use `get_book_or_404(..., project_id)`.
2. **Project model:** Added `last_accessed_at` for continue-recent.
3. **Billing limits:** Excluded archived projects and books from project/book limit counts.
4. **Migration:** `019_add_project_last_accessed.py` adds `last_accessed_at` to projects.
