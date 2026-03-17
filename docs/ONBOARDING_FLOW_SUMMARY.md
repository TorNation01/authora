# AUTHORA Onboarding Flow — Production-Ready Summary

## Overview

The onboarding system guides new users from first visit to first meaningful writing action with clarity, simplicity, and momentum. It reduces drop-off, adapts to different user types, and creates immediate progress.

---

## 1. Entry Flow

**After signup/login:** User is routed to `/onboarding`.

**Two entry options:**

| Option | Description | Default |
|--------|-------------|---------|
| **Guided Start** (recommended) | Structured help from setup to first words. Asks a few questions and tailors the experience. | ✓ Selected |
| **Quick Start** | Jump straight to the editor. Create a blank project and start writing immediately. | |

- **Guided** = step-by-step, structured help
- **Quick** = immediate writing, minimal friction

---

## 2. User Intent Selection

**Question:** What are you writing?

**Options (large selectable cards):**
- Fiction — Novels, stories, creative writing
- Non-fiction — How-to, business, academic, ideas
- Memoir — Shaping lived experience into story
- Workbook / Guide — Prompts, exercises, action-oriented structure
- Not sure yet — Show me the options and I'll explore

---

## 3. Guidance Level

**Question:** How much guidance do you want?

**Options:**
- **Guided** — Step-by-step. Clear structure and momentum.
- **Balanced** — Some structure where it helps. Freedom where you want it.
- **Freeform** — Write your way. Keep the tools, lose the rails.

User can switch later in settings.

---

## 4. Project Setup

**Collected:**
- **Project name** (required)
- **Description** (optional) — One sentence about what this book is about
- **Goal** (optional) — e.g. Finish first draft by summer

Project is created immediately after the flow completes.

---

## 5. Structure Selection

**Options:**
- **Use a template** — Pre-built structure for your type of book
- **Start blank** — Clean slate. Build your own structure.

Templates are filtered by intent:
- Fiction → fiction templates (novel, romance, fantasy, thriller)
- Non-fiction → nonfiction templates
- Memoir → memoir templates
- Workbook → workbook templates
- Not sure → all templates

---

## 6. First Action Moment

**Question:** What would you like to do first?

| Option | Action |
|--------|--------|
| **Start writing first chapter** | Redirect to editor (`/dashboard/projects/{id}/books/{bookId}`) |
| **Outline first sections** | Redirect to plan page (`/dashboard/projects/{id}/books/{bookId}/plan`) |

Frictionless. One click to writing or outlining.

---

## 7. Quick Intro Overlay

**When:** First-time users who choose "Start writing first chapter" see a minimal intro before the editor.

**Content:**
- Your chapters are in the sidebar—click to switch
- The toolbar has AI, notes, and export
- Just start typing. Your work saves automatically.

**Actions:** "Let's write" or "Skip intro"

Not overwhelming. Dismissible. Stored in `localStorage` so it doesn't show again.

---

## 8. Skip Logic

- **Skip for now** — Link on every step (except entry) → goes to `/dashboard`
- **Resume later** — Progress saved to `localStorage` and API (`/api/v1/journey/onboarding/progress`)
- **Back** — Navigate to previous step (Guided flow only)

---

## 9. Return Users

If onboarding is incomplete:
- Dashboard shows "Complete your setup" or "Resume setup" banner
- Login redirects to `/onboarding` when `onboarding_completed !== true`
- Progress restored from API or `localStorage`

---

## 10. Auth Routing

| Event | Destination |
|-------|-------------|
| Register | `/onboarding` |
| Login (onboarding incomplete) | `/onboarding` |
| Login (onboarding complete) | `/dashboard` |
| Skip onboarding | `/dashboard` |
| Complete onboarding | Editor or Plan page |

---

## UX Flow Diagram

```
                    ┌─────────────────┐
                    │  Signup/Login   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   /onboarding   │
                    │   Entry Step    │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌─────────────────┐           ┌─────────────────┐
     │  Quick Start    │           │  Guided Start   │
     │  (name only)    │           │                 │
     └────────┬────────┘           └────────┬────────┘
              │                             │
              │                    ┌────────┴────────┐
              │                    │ Intent         │
              │                    │ (Fiction, NF,  │
              │                    │  Memoir, etc.) │
              │                    └────────┬────────┘
              │                             │
              │                    ┌────────┴────────┐
              │                    │ Guidance Level  │
              │                    │ (Guided/Balanced│
              │                    │  /Freeform)     │
              │                    └────────┬────────┘
              │                             │
              │                    ┌────────┴────────┐
              │                    │ Project Setup   │
              │                    │ (name, desc,   │
              │                    │  goal)         │
              │                    └────────┬────────┘
              │                             │
              │                    ┌────────┴────────┐
              │                    │ Structure       │
              │                    │ (template/blank)│
              │                    └────────┬────────┘
              │                             │
              │                    ┌────────┴────────┐
              │                    │ First Action    │
              │                    │ (write/outline) │
              │                    └────────┬────────┘
              │                             │
              └──────────────┬─────────────┘
                             │
                    ┌────────┴────────┐
                    │ Create Project  │
                    │ (from-wizard)   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
     ┌─────────────────┐           ┌─────────────────┐
     │ First action:    │           │ First action:    │
     │ Write           │           │ Outline          │
     └────────┬────────┘           └────────┬────────┘
              │                             │
              │  (first time?)              │
              ▼                             ▼
     ┌─────────────────┐           ┌─────────────────┐
     │ Intro Overlay    │           │ Plan Page        │
     │ (optional)      │           │ (/plan)          │
     └────────┬────────┘           └─────────────────┘
              │
              ▼
     ┌─────────────────┐
     │ Editor          │
     │ (/books/{id})   │
     └─────────────────┘
```

---

## Confirmation: Production-Ready

| Requirement | Status |
|-------------|--------|
| Entry flow (Guided vs Quick) | ✅ |
| User intent selection | ✅ Fiction, Non-fiction, Memoir, Workbook, Not sure |
| Guidance level | ✅ Guided, Balanced, Freeform |
| Project setup | ✅ Name, optional description, optional goal |
| Structure selection | ✅ Template (filtered by intent) or Blank |
| First action | ✅ Write first chapter or Outline sections |
| Quick intro overlay | ✅ Minimal, dismissible, localStorage |
| Skip logic | ✅ Skip for now, Resume later |
| Progress persistence | ✅ localStorage + API |
| Return users | ✅ Resume where left off |
| Auth routing | ✅ Register → onboarding; Login → onboarding if incomplete |
| Clean UX | ✅ Large cards, clear copy, no overwhelm |

---

## Files

- `apps/web/src/app/onboarding/page.tsx` — Main onboarding flow
- `apps/web/src/components/onboarding/EditorIntroOverlay.tsx` — Quick intro overlay
- `apps/web/src/content/onboarding-copy.ts` — Copy for new flow
- `apps/web/src/app/(auth)/login/page.tsx` — Login redirect to onboarding if incomplete
