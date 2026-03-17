# AUTHORA Help Center & Documentation System

Production-ready help center and documentation system that provides clear, helpful, easy-to-read guidance for users.

---

## 1. Help System Summary

### Architecture

| Component | Purpose |
|-----------|---------|
| **Public help pages** | Standalone pages at `/help` and `/help/[slug]` with full guides |
| **In-app HelpCenter** | Sheet/drawer with searchable articles, opens from sidebar |
| **HelpLink** | Contextual links from app to relevant help pages |
| **Help pages content** | `help-pages.ts` — full page content with sections |
| **Help center articles** | `help-center.ts` — in-app articles with tags and search |

### Content Style

- Simple language, non-technical
- Step-by-step instructions
- Friendly tone
- Clear headings, short sections

---

## 2. Page List

| Route | Title | Description |
|-------|-------|--------------|
| `/help` | Help center | Overview with links to all guides |
| `/help/getting-started` | Getting started | How to start a book, choose guidance level |
| `/help/writing-with-authora` | Writing with Authora | How to write chapters, stay in flow |
| `/help/story-integrity-engine` | Story Integrity Engine | What it does, how to use it, examples |
| `/help/story-density-engine` | Story Density Engine | What it does, when to trim vs expand |
| `/help/ai-assistance` | AI assistance | How to use AI properly, keep your voice |
| `/help/account-and-billing` | Account and billing | Account settings, plans, billing |
| `/help/export-and-publishing` | Export and publishing | Export formats, publishing prep, finishing |

---

## 3. Content Summary

### Getting Started
- How to start a book (project → book → chapters → write)
- How to choose guidance level (Guided, Flexible, Freeform)

### Writing with Authora
- How to write chapters (click, type, toolbar, briefs)
- How to stay in flow (Focus mode, word goals, notes, version history)

### Story Integrity Engine
- What it does (unresolved threads, weak arcs, gaps)
- How to use it (Story Health panel, Scan, review, resolve)
- Examples (unresolved threads, weak arcs, structural gaps)

### Story Density Engine
- What it does (filler, repetition, weak sections)
- When to trim vs expand (trim redundant, expand thin transitions)

### AI Assistance
- How to use AI properly (select text, AI menu, describe needs)
- How to keep your voice (approve/edit/reject, AI level, privacy)

### Account and Billing
- Account settings (profile, AI key)
- Billing and plans (view plan, upgrade, invoices)

### Export and Publishing
- Export formats (DOCX, PDF, EPUB, TXT)
- Publishing prep (synopsis, blurb, query letter)
- Finishing a book (Finish Mode, scans before export)

---

## 4. Search Function

- **Help layout** (`/help`): Search bar with keyword matching across page titles, descriptions, keywords, and section content
- **In-app HelpCenter**: Search bar with keyword matching across article titles, summaries, tags, and body text
- Results shown in dropdown (help layout) or inline list (HelpCenter)

---

## 5. Contextual Help Links

| Location | Link | Destination |
|----------|------|--------------|
| **BrandedSidebar** | Help, Help center | Opens HelpCenter sheet; link to `/help` |
| **Story Integrity panel** | Learn more | `/help/story-integrity-engine` or `/help/story-density-engine` (tab-aware) |
| **HelpCenter article view** | Read full guide | `/help/[slug]` (when article maps to a page) |
| **HelpCenter list view** | Browse full help center | `/help` |
| **Marketing nav** | Help | `/help` |
| **Marketing footer** | Help | `/help` |

---

## 6. Production Readiness Confirmation

| Requirement | Status |
|-------------|--------|
| Public help pages at specified routes | ✅ |
| Simple, non-technical, step-by-step content | ✅ |
| Friendly tone, clear headings, short sections | ✅ |
| Core guides (Getting Started, Writing, Integrity, Density, AI, Finishing) | ✅ |
| Search bar with keyword matching | ✅ |
| Contextual help links from inside app | ✅ |
| In-app HelpCenter with articles and search | ✅ |
| Article-to-page mapping for "Read full guide" | ✅ |

### Files

- `apps/web/src/content/help-pages.ts` — Public help page content
- `apps/web/src/content/help-center.ts` — In-app articles, categories, search, article-to-slug mapping
- `apps/web/src/app/(marketing)/help/layout.tsx` — Help layout with sidebar + search
- `apps/web/src/app/(marketing)/help/page.tsx` — Help index
- `apps/web/src/app/(marketing)/help/[slug]/page.tsx` — Dynamic help pages
- `apps/web/src/components/help/HelpCenter.tsx` — In-app help sheet
- `apps/web/src/components/help/HelpLink.tsx` — Contextual help link component
