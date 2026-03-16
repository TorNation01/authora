# Beta Reader Preparation

Prepare your manuscript and materials for beta readers. This guide covers what to include, how to package it, and how to get useful feedback.

## Overview

Beta readers read your manuscript before publication and provide feedback on plot, pacing, characters, and reader experience. A well-prepared package makes it easier for them to give focused, actionable feedback.

## Before Sending to Beta Readers Checklist

### 1. Manuscript Quality

- [ ] **Clean manuscript** – No notes, comments, or revision marks visible
- [ ] **Complete draft** – All chapters included (or clearly marked as excerpts)
- [ ] **No placeholders** – Replace [TK], lorem ipsum, or draft placeholders
- [ ] **Consistent formatting** – Chapter breaks, scene breaks, headings

### 2. Package Contents

| Item | Purpose |
|------|---------|
| Manuscript (DOCX) | Main reading file |
| Synopsis | Overview of the story |
| Chapter summaries | Quick reference for feedback |
| Feedback form | Structured questions for readers |

### 3. Export in AUTHORA

Use the **Beta reader package** export. It produces a ZIP containing:

- Manuscript (DOCX)
- Synopsis (DOCX)
- Chapter summaries (TXT)
- Feedback form (TXT)

**Endpoint:** `GET /api/v1/export/books/{book_id}/priority/beta-reader`

### 4. Customize the Feedback Form

The default feedback form includes generic questions. Consider adding:

- What hooked you (or didn’t) in the opening?
- Which scenes felt slow or rushed?
- Were any characters confusing or underdeveloped?
- What did you predict would happen? Were you surprised?
- What would make you recommend this book?

### 5. Instructions for Beta Readers

Include a short note with:

- **Timeline** – When you need feedback
- **Focus areas** – Plot, pacing, characters, clarity, etc.
- **Format** – How to return feedback (comments in DOCX, separate document, etc.)
- **Honesty** – Encourage candid feedback

## Beta Reader Copy Preparation

### What to Exclude

- Internal notes and comments
- Revision marks and track changes
- Placeholder text
- Unfinished sections (or label them clearly)

### What to Include

- Title page
- Table of contents (optional but helpful)
- Full manuscript
- Synopsis

### Front Matter

For beta readers, keep front matter minimal:

- Title page (title, author)
- Optional: brief note (“This is a beta draft. Feedback welcome.”)

Dedication, epigraph, and full copyright can wait for the final version.

## AUTHORA Workflow

1. **Select your book** in the Export center
2. **Run export readiness check** – Fix any errors
3. **Add author name** (and any front matter you want)
4. **Export Beta reader package**
5. **Unzip and review** – Add custom feedback questions if needed
6. **Send to beta readers** with your instructions

## After Beta Feedback

- Log feedback in notes or a separate document
- Prioritize recurring comments
- Use revision passes to address structural or clarity issues
- Consider a second beta round after major revisions
