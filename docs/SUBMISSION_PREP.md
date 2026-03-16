# Submission Preparation

Prepare sample chapters and supporting materials for agent or publisher submissions. Most queries require a polished sample plus synopsis and query letter.

## Overview

Submission prep focuses on your best foot forward: strong opening chapters, a clear synopsis, and accurate metadata. This guide covers what to prepare and how to export it from AUTHORA.

## Before Submitting Sample Chapters Checklist

### 1. Sample Content

- [ ] **First 3 chapters** (or agent’s requested sample) polished
- [ ] **Strong opening** – Hook in the first page
- [ ] **No placeholders** – All draft text replaced
- [ ] **No empty sections** – Every included chapter has content

### 2. Supporting Materials

| Material | Purpose |
|----------|---------|
| Sample chapters (DOCX) | Main submission |
| Synopsis | Full story summary |
| Query letter | Pitch (prepared separately) |

### 3. Metadata

- [ ] **Title** – Final or submission title
- [ ] **Author name** – Legal name or pen name
- [ ] **Word count** – Full manuscript and sample (if different)

### 4. Formatting

- [ ] **Manuscript standard** – 12pt, double-spaced, 1" margins
- [ ] **Chapter breaks** – New chapter, new page
- [ ] **No fancy formatting** – Simple, professional

## Submission Sample Preparation

### What to Include in the Sample

- **Chapters 1–3** (typical) or as specified in guidelines
- **Title page** – Title, author, contact
- **No table of contents** for sample (optional for full manuscript)

### What to Exclude

- Notes and comments
- Revision marks
- Unfinished or placeholder chapters

### Export in AUTHORA

Use the **Sample chapters** export. It includes the first 3 chapters (configurable via `max_chapters`).

**Endpoint:** `GET /api/v1/export/books/{book_id}/priority/sample-chapters?max_chapters=3`

## Synopsis Preparation

Agents and publishers expect a synopsis that covers:

- **Setup** – Main character, world, initial situation
- **Inciting incident** – What kicks off the story
- **Rising action** – Key plot points and stakes
- **Climax** – Major turning point
- **Resolution** – How it ends

### AUTHORA Support

Use **Publishing prep → Synopsis** to generate a draft. Edit and tighten for submission.

**Endpoint:** `GET /api/v1/export/books/{book_id}/publishing-prep/synopsis`

## Query Letter (Outside AUTHORA)

The query letter is usually written separately. It typically includes:

- **Hook** – One or two sentences that grab attention
- **Summary** – 2–3 paragraphs on the story
- **Bio** – Brief author credentials
- **Closing** – Thank them, mention sample/synopsis attached

## Submission Copy Export

For a **full manuscript** submission (after request):

- Use **Submission copy** (DOCX)
- Clean manuscript format
- All chapters, front matter, table of contents

**Endpoint:** `GET /api/v1/export/books/{book_id}/priority/submission`

## Checklist Summary

| Step | Action |
|------|--------|
| 1 | Polish first 3 chapters |
| 2 | Run export readiness check |
| 3 | Export sample chapters (DOCX) |
| 4 | Generate and edit synopsis |
| 5 | Write query letter |
| 6 | Verify title, author, word count |
| 7 | Submit per agent/publisher guidelines |

## Agent Guidelines

Always check each agent’s or publisher’s submission guidelines. They may specify:

- Number of sample pages or chapters
- Synopsis length (e.g., 1–2 pages)
- Format (DOCX, PDF)
- Subject line and attachment rules
