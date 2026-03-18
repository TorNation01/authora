# AUTHORA Template System – Production Ready

## 1. Template System Summary

The AUTHORA template system provides **fully structured, ready-to-use templates** for fiction, non-fiction, and guided writing flows. Every template is production-ready with no placeholders.

### What Each Template Includes

| Component | Description |
|-----------|-------------|
| **Structure** | Planning sections with titles, types, and guidance text |
| **Section prompts** | `default_planning_prompts` – prompts for each planning section |
| **Guidance text** | `guidance` on planning sections – in-context help for writers |
| **AI assistance hooks** | `ai_prompts` – optional AI task triggers (brainstorm, scene, outline, etc.) |
| **Chapter skeletons** | Pre-defined chapters with titles and summaries |
| **Milestones** | Default milestones (planning → draft → revision → feedback) |
| **Setup questions** | Wizard questions for project creation |
| **Export recommendations** | docx, epub, pdf, etc. |

### Template Library Features

| Feature | Status |
|---------|--------|
| Template library UI | ✅ `/dashboard/templates` |
| Category filtering | ✅ Sidebar filter by category |
| Template preview | ✅ Dialog with full details |
| Structure preview | ✅ Planning sections + chapter list in preview |
| Apply template to project | ✅ "Use template" → `/dashboard/projects/new?templateId=...` |
| Duplicate template (admin) | ✅ Duplicate button in preview for admins |
| Edit template (admin) | ✅ PATCH `/api/v1/admin/templates/{id}` |

---

## 2. Template Categories

Templates are organized into the following categories:

### Fiction

| Slug | Name | Sub-templates |
|------|------|---------------|
| fiction | Fiction Novel | Romance, Fantasy, Thriller, Sci-Fi, Horror, Historical, Literary, YA, Contemporary, Short Story, Series, General |

**Description**: Build stories with structure, character, tension, and momentum.

### Non-Fiction

| Slug | Name | Sub-templates |
|------|------|---------------|
| nonfiction | Non-Fiction Book | Self-Help, Business, Finance, Health, Parenting, Relationships, Educational, Thought Leadership, How-to, Personal Story, Faith, Professional, General |
| memoir | Memoir | — |

**Description**: Turn your expertise, ideas, or message into a clear and compelling book.

### Hybrid / Creative

| Slug | Name | Sub-templates |
|------|------|---------------|
| hybrid_creative | Hybrid / Creative Nonfiction | — |

**Description**: Blend fact with literary craft. Narrative nonfiction, creative nonfiction, and essay collections with story-driven structure.

### Business / Authority

Business and authority templates live under **Non-Fiction**:

- `nonfiction-business` – Business book for professionals
- `nonfiction-professional` – Professional Authority Book
- `nonfiction-thought-leadership` – Positioning as industry authority

### Journals / Guided

| Slug | Name | Sub-templates |
|------|------|---------------|
| workbook | Workbook | — |
| journal | Journal | — |

**Description**: Create guided content with prompts, exercises, and action-oriented structure. Design reflective writing experiences with prompts, rhythms, and themes.

### Other Categories

| Slug | Name |
|------|------|
| poetry | Poetry Collection |
| short_story_collection | Short Story Collection |
| series_project | Series Project |
| ghostwritten_book | Ghostwritten Book |
| custom | Custom / Blank Project |

---

## 3. Production Readiness Confirmation

### Core Requirements

| Requirement | Status |
|-------------|--------|
| Templates fully usable (no placeholders) | ✅ All chapter skeletons and planning sections have concrete content |
| Structure included | ✅ `default_structure.planning_sections` |
| Section prompts included | ✅ `default_planning_prompts` |
| Guidance text included | ✅ `guidance` on planning sections (fiction, nonfiction, premium, hybrid) |
| Optional AI assistance hooks | ✅ `ai_prompts` on all templates |

### Template System Features

| Feature | Status |
|---------|--------|
| Template library UI | ✅ |
| Category filtering | ✅ |
| Template preview | ✅ |
| Apply template to project | ✅ |
| Duplicate template (admin) | ✅ |
| Edit template (admin) | ✅ |
| Structure preview in dialog | ✅ Planning sections + chapter list |

### Categories Delivered

| Category | Status |
|----------|--------|
| Fiction | ✅ |
| Non-Fiction | ✅ |
| Hybrid / Creative | ✅ |
| Business / Authority | ✅ (under Nonfiction) |
| Journals / Guided | ✅ (Workbook, Journal) |

### Premium Templates (Flagship)

Romance, Fantasy, Thriller, Sci-Fi, Memoir, Self-Help, Business, Workbook – each with:

- Polished planning sections with guidance
- Genre-specific chapter skeletons
- Revision checklists
- Export readiness checklists
- Writing prompts
- Setup questions
- AI prompts

---

## 4. Seed and API

**Seed command**: `npm run db:seed` (includes `seed_project_templates`)

**Template API**:
- `GET /api/v1/templates/categories` – Categories with top-level templates and children
- `GET /api/v1/templates/{id}` – Full template details
- `POST /api/v1/admin/templates/{id}/duplicate` – Duplicate (admin only)

---

## 5. Related Documentation

- [TEMPLATE_SYSTEM_SUMMARY.md](./TEMPLATE_SYSTEM_SUMMARY.md) – High-level summary
- [ADMIN_TEMPLATE_MANAGEMENT.md](./ADMIN_TEMPLATE_MANAGEMENT.md) – Admin API
- [PROJECT_TEMPLATES.md](./PROJECT_TEMPLATES.md) – Template creation flow
- [GENRE_TEMPLATE_ARCHITECTURE.md](./GENRE_TEMPLATE_ARCHITECTURE.md) – Architecture
