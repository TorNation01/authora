# AUTHORA Advanced Project Management System – Final Outputs

This document provides the three deliverables for the production-ready project management system.

---

## 1. Project System Summary

The advanced project management system helps users manage complex books and large writing projects through organization, filtering, and multiple views.

### Features

| Feature | Description |
|---------|-------------|
| **Chapter drag-and-drop** | Reorder chapters in the manuscript sidebar via @hello-pangea/dnd |
| **Section grouping** | Assign chapters to section groups (e.g. Part 1, Act 2) via `section_group` |
| **Storyboards** | Card-grid view of all chapters across books with labels and tags |
| **Timeline view** | Sequential chapter list with status labels |
| **Tagging system** | Custom tags per chapter (JSONB array) |
| **Labels** | Status labels: draft, revising, review, done (`section_status`) |
| **Custom tags** | Free-form tags (e.g. action, pov-john, key-scene) |
| **Filtering** | Filter by label, section group, or tag |

### API

- `GET /api/v1/projects/{id}/books/{bookId}` – Get book with chapters. Query params: `section_status`, `section_group`, `tag`
- `PATCH /api/v1/projects/{id}/books/{bookId}/chapters/{chapterId}` – Update chapter (title, sort_order, section_status, section_group, tags)
- `POST /api/v1/projects/{id}/books/{bookId}/chapters/reorder` – Reorder chapters by id list

### Schema

**Chapter** (new fields):

- `section_group` – string, nullable (e.g. "Part 1", "Act 2")
- `tags` – list of strings (e.g. ["action", "pov-john"])

### Migration

- `036_add_project_management_columns` – Adds `section_group` and `tags` to `chapters` table

---

## 2. UI Summary

### Project Page

- **Manage** button – Links to `/dashboard/projects/{id}/manage`

### Manage Page (`/dashboard/projects/{id}/manage`)

- **View modes** – List | Storyboard | Timeline
- **Filters** – Label (draft/revising/review/done), Section (section_group), Tag
- **List view** – Books with chapters grouped by book
- **Storyboard view** – Card grid of chapters with title, book, word count, labels, tags
- **Timeline view** – Timeline-style list per book with status indicators

### Manuscript Sidebar

- **Chapter display** – Section group badge, status label, tags
- **Chapter menu** – Rename, Duplicate, Delete, **Set section**, **Set tags**
- **Set section** – Dialog to assign section group (e.g. Part 1)
- **Set tags** – Dialog for comma-separated tags
- **Drag-and-drop** – Reorder chapters via grip handle

### Organization

- **Labels** – draft, revising, review, done (via section_status)
- **Custom tags** – Per-chapter; filter by tag in Manage view
- **Section groups** – Group chapters (Part 1, Act 2); filter by section

---

## 3. Production-Ready Confirmation

The advanced project management system is **production-ready**.

### Checklist

- [x] Chapter drag-and-drop
- [x] Section grouping (section_group)
- [x] Storyboards (card grid view)
- [x] Timeline view
- [x] Tagging system (custom tags)
- [x] Labels (draft, revising, review, done)
- [x] Custom tags
- [x] Filtering (status, section, tag)
- [x] API endpoints
- [x] Migration
- [x] UI integration
- [x] Documentation

### Status

**Production-ready.** Users can organize chapters with section groups and tags, filter by label/section/tag, and use List, Storyboard, and Timeline views to manage complex books.
