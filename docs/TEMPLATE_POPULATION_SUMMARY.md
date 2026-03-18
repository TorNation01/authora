# AUTHORA Template Population Summary

**Date:** March 15, 2025  
**Status:** Production-ready

---

## 1. Template List Summary

### New Templates Added (15)

| Slug | Name | Category |
|------|------|----------|
| `fiction-three-act` | Three Act Structure | fiction |
| `fiction-hero-journey` | Hero's Journey | fiction |
| `fiction-chapter-builder` | Chapter Builder | fiction |
| `fiction-character-builder` | Character Builder | fiction |
| `fiction-world-building` | World Building | fiction |
| `nonfiction-book-blueprint` | Book Blueprint | nonfiction |
| `nonfiction-chapter-template` | Chapter Template | nonfiction |
| `nonfiction-authority-book` | Authority Book | nonfiction |
| `nonfiction-self-help-structured` | Self-Help (Structured) | nonfiction |
| `ai-book-builder` | AI Book Builder | ai_templates |
| `ai-expansion` | AI Expansion | ai_templates |
| `accountability-daily-writing` | Daily Writing | accountability |
| `accountability-weekly-progress` | Weekly Progress | accountability |
| `business-course-book` | Course Book | business |
| `business-lead-magnet` | Lead Magnet | business |

### Total Templates: 51

---

## 2. Category Summary

| Category | Description | Template Count |
|---------|-------------|----------------|
| **fiction** | Build stories with structure, character, tension, and momentum. | 18 (incl. 5 new) |
| **nonfiction** | Turn expertise, ideas, or message into a clear and compelling book. | 18 (incl. 4 new) |
| **ai_templates** | AI-assisted writing from idea to draft. Generate outlines, expand content, refine with AI. | 2 |
| **accountability** | Daily and weekly check-ins to track progress, reflect, and build writing habit. | 2 |
| **business** | Course books, lead magnets, and business content that teaches and converts. | 2 |
| memoir | Shape lived experience into a story with meaning, emotion, and reflection. | 1 |
| hybrid_creative | Blend fact with literary craft. Narrative nonfiction, creative nonfiction, essay collections. | 1 |
| workbook | Create guided content with prompts, exercises, and action-oriented structure. | 1 |
| journal | Design reflective writing experiences with prompts, rhythms, and themes. | 1 |
| poetry | Organize a collection with flow, sequence, and emotional shape. | 1 |
| short_story_collection | Build a cohesive set of stories with shared themes and strong structure. | 1 |
| series_project | Plan connected books with continuity, lore, and long-form story arcs. | 1 |
| ghostwritten_book | Capture a client's message, voice, and source material in a structured writing flow. | 1 |
| custom | Blank project – start from scratch. | 1 |

---

## 3. Production-Ready Confirmation

### Requirements Met

| Requirement | Status |
|-------------|--------|
| **No placeholder content** | All chapter skeletons and planning sections use descriptive guidance text. No `[fill]` or empty placeholders. |
| **Fully structured** | Each template has `default_structure` (planning_sections), `chapter_skeletons`, `default_milestones`, and `setup_questions`. |
| **Includes guidance text** | All planning sections include `guidance` where applicable. Chapter summaries provide clear direction. |
| **AI-ready prompts** | Each template has `ai_prompts` with concrete, copy-paste-ready prompts (e.g. `generate_outline`, `expand`, `refine`). |
| **default_planning_prompts** | All templates include prompts for key planning sections. |

### Template Features (All New Templates)

- **Planning sections** with `id`, `title`, `type`, and `guidance`
- **Chapter skeletons** with `title` and `summary` (descriptive, not placeholder)
- **default_planning_prompts** for AI-assisted planning
- **ai_prompts** for generation, expansion, refinement
- **default_milestones** for progress tracking
- **setup_questions** for project initialization
- **export_recommendations** (docx, pdf, epub as appropriate)

### Seed Status

- **Seeded:** 51 project templates
- **Script:** `python -m authora.scripts.seed_project_templates`

---

## 4. Quick Reference: AI Prompts by Template

| Template | Key AI Prompts |
|----------|----------------|
| Chapter Builder | `chapter_card`, `tension`, `hook` |
| Character Builder | `character`, `voice`, `conflict` |
| World Building | `world`, `consistency`, `sensory` |
| Book Blueprint | `blueprint`, `chapter`, `positioning` |
| Chapter Template | `chapter_card`, `example`, `action_step` |
| Authority Book | `credibility`, `framework`, `case_study` |
| Self-Help (Structured) | `insight`, `exercise`, `transformation` |
| AI Book Builder | `generate_outline`, `generate_chapter`, `expand_section` |
| AI Expansion | `expand`, `refine`, `improve` |
| Daily Writing | `goal`, `reflection`, `momentum` |
| Weekly Progress | `progress`, `blockers`, `planning` |
| Course Book | `module`, `exercise`, `alignment` |
| Lead Magnet | `hook`, `problem`, `cta` |
