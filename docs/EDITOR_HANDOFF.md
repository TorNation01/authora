# Editor Handoff

Prepare your manuscript and supporting materials for a developmental or copy editor. A clear handoff helps the editor understand your goals and work efficiently.

## Overview

An editor handoff typically includes the manuscript plus context: synopsis, chapter summaries, author bio, and any specific notes. This gives the editor a roadmap and clarifies your expectations.

## Before Sending to an Editor Checklist

### 1. Manuscript

- [ ] **Clean or review copy** – Depending on whether you want comments visible
- [ ] **Chapter breaks** – Each chapter starts on a new page
- [ ] **Table of contents** – Included and accurate
- [ ] **Consistent formatting** – Scene breaks, headings, spacing

### 2. Supporting Materials

| Material | Purpose |
|----------|---------|
| Synopsis | Overall story arc and structure |
| Chapter summary sheet | One-paragraph summary per chapter |
| Author bio | For back matter or marketing |
| Style notes | Preferences (e.g., -ise vs -ize, serial comma) |

### 3. Front and Back Matter

- [ ] **Acknowledgements** – Draft ready (editor may suggest tweaks)
- [ ] **About the author** – Draft for back matter
- [ ] **Dedication / epigraph** – If including, finalized or near-final

### 4. Handoff Note

Include a brief note covering:

- **Timeline** – When you need the edit back
- **Scope** – Developmental, copy edit, proofread, or combination
- **Focus areas** – Pacing, voice, continuity, etc.
- **Questions** – Specific concerns you want addressed

## Editor Handoff Checklist (Detailed)

### Content Readiness

- [ ] Manuscript is at the stage you want edited (draft, revised draft, etc.)
- [ ] No placeholder text ([TK], lorem ipsum, etc.)
- [ ] Unresolved comments resolved or removed from export

### Export Options

- [ ] **Review copy** – If you want the editor to add comments and suggestions
- [ ] **Clean manuscript** – If you prefer a clean file and separate feedback document

### Package Assembly

1. **Manuscript** – Editor review copy (DOCX) or Clean manuscript (DOCX)
2. **Chapter summary sheet** – `GET /api/v1/export/books/{book_id}/packages/chapter-summary-sheet`
3. **Synopsis** – `GET /api/v1/export/books/{book_id}/packages/synopsis`
4. **Handoff note** – Written separately (email or document)

## AUTHORA Workflow

1. **Publishing prep** – Generate synopsis and chapter summaries (AI)
2. **Export** – Editor review copy (DOCX)
3. **Export** – Chapter summary sheet (DOCX)
4. **Export** – Synopsis (DOCX)
5. **Write handoff note** – Timeline, scope, focus areas
6. **Send package** – Manuscript + summaries + synopsis + note

## What Editors Expect

- **Consistent formatting** – Same font, spacing, chapter style throughout
- **Complete manuscript** – No missing chapters or sections
- **Clear brief** – What kind of edit, timeline, and priorities
- **Reasonable timeline** – Developmental edits often take weeks; copy edits less

## After the Edit

- Review editor’s comments and suggestions
- Use revision passes to work through changes systematically
- Track acceptance/rejection of suggestions if using Word’s review features
