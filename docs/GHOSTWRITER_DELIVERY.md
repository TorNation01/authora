# Ghostwriter Delivery

Prepare and deliver a ghostwritten manuscript to your client. A complete delivery package includes the manuscript plus all materials the client needs for editing, marketing, and publication.

## Overview

Ghostwriter delivery is the handoff of a completed manuscript from ghostwriter to client. The package should be approval-ready: clean manuscript, synopsis, summaries, blurb, author bio, and handoff notes for the client’s editor or publisher.

## Before Delivering a Ghostwritten Draft Checklist

### 1. Manuscript Quality

- [ ] **Clean manuscript** – No internal notes, comments, or revision marks
- [ ] **Client voice** – Matches agreed tone and style
- [ ] **Brief compliance** – Meets client’s outline and requirements
- [ ] **No placeholders** – All [TK], [INSERT], and draft text replaced

### 2. Delivery Package Contents

| Item | Purpose |
|------|---------|
| Manuscript (DOCX) | Main deliverable |
| Synopsis | For agents, editors, or marketing |
| Chapter summaries | Quick reference, editorial handoff |
| Back cover blurb | Marketing and cover copy |
| Author bio draft | For back matter and marketing |
| Handoff notes | Context for client’s editor |

### 3. Client-Specific

- [ ] **Pen name** – If client uses one, applied consistently
- [ ] **Sensitivity** – Any requested changes to names, details, or framing
- [ ] **Format** – Client’s preferred formatting (manuscript standard, etc.)

### 4. Approval Readiness

- [ ] Manuscript reads as a complete, coherent book
- [ ] No continuity errors or loose threads
- [ ] Pacing and structure match the brief

## Ghostwriter Delivery Checklist (Detailed)

### Content

- [ ] All chapters complete
- [ ] Scene breaks and chapter breaks in place
- [ ] Front matter (title, copyright, dedication, epigraph) as agreed
- [ ] Back matter (acknowledgements, about author) drafted

### Package Assembly

Use the **Ghostwriter delivery package** export. It produces a ZIP with:

- Manuscript (DOCX)
- Synopsis (DOCX)
- Back cover blurb (TXT)
- Chapter summaries (DOCX)
- Author bio (TXT)
- Handoff notes (TXT)

**Endpoint:** `GET /api/v1/export/books/{book_id}/priority/ghostwriter`

### Handoff Notes

The handoff notes file should cover:

- **Project summary** – What the book is about
- **Structural notes** – Any deviations from the original brief and why
- **Editor guidance** – Suggested focus areas for the client’s editor
- **Timeline** – Draft version, delivery date

## AUTHORA Workflow

1. **Complete manuscript** – All chapters written and revised
2. **Publishing prep** – Generate synopsis, blurb, chapter summaries, author bio (AI)
3. **Export** – Ghostwriter delivery package (ZIP)
4. **Review package** – Ensure all files are correct and complete
5. **Deliver** – Send ZIP to client with brief cover note

## Client Review Package vs. Internal Review Copy

| Type | Use Case | Contents |
|------|----------|----------|
| **Client review package** | Final delivery to client | Clean manuscript + full package |
| **Internal review copy** | Your own QA before delivery | May include notes, draft materials |
| **Approval-ready manuscript** | Ready for client sign-off | Polished, no internal artifacts |

## Delivery Best Practices

- **Version clearly** – e.g., `ClientName_Manuscript_Draft2_2026-03-16.docx`
- **Confirm format** – DOCX is standard; confirm if client wants PDF or other
- **Include a cover email** – Brief summary, what’s in the package, next steps
- **Set expectations** – Revisions round, timeline for feedback
