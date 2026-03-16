# AUTHORA Writing Editor — Production Report

This document describes how the production-grade writing editor works in AUTHORA.

## Overview

The AUTHORA writing editor is a full-featured manuscript editor built on **TipTap** (ProseMirror). It supports chapter-based writing, rich formatting, autosave, version history, notes, AI assistance, and more. The main editor lives at `/dashboard/projects/[id]/books/[bookId]`.

---

## Feature Matrix

| Feature | Status | Implementation |
|---------|--------|----------------|
| Rich text editor | ✅ | TipTap with StarterKit, Typography, Underline, Highlight |
| Chapter-based writing | ✅ | ManuscriptSidebar with chapter list |
| Headings (H1, H2, H3) | ✅ | StarterKit + bubble menu dropdown |
| Formatting controls | ✅ | EditorBubbleMenu: Bold, Italic, Underline, Highlight, Lists, Blockquote |
| Autosave | ✅ | `useAutosave` hook, 2s delay, retries on conflict |
| Version history | ✅ | VersionHistoryDialog, restore from API |
| Notes | ✅ | NotesPanel (side panel), chapter-linked notes |
| Comments | ⚠️ | Notes serve as chapter-level comments; inline text-anchored comments not implemented |
| Highlights | ✅ | TipTap Highlight extension + bubble menu |
| Split view | ✅ | Notes, AI, Reference panels toggle beside editor |
| Manuscript sidebar | ✅ | ManuscriptSidebar with chapters, links to plan/ghostwriter |
| Chapter navigation | ✅ | Click chapter in sidebar to switch |
| Drag/reorder chapters | ✅ | @hello-pangea/dnd in ManuscriptSidebar |
| Word count | ✅ | Chapter + total in toolbar (WritingStats) |
| Reading time | ✅ | ~X min read (200 WPM) in WritingStats |
| Find/replace | ✅ | FindReplaceDialog with Find Next/Prev, Replace, Replace All |
| Distraction-free mode | ✅ | Hides sidebar, toolbar; minimal header with save status |
| AI assist | ✅ | AIWritingPanel, AIActionPanel, selection-based actions |

---

## Architecture

### Core Components

- **WritingStudioEditor** (`components/editor/WritingStudioEditor.tsx`) — TipTap editor with extensions, bubble menus, word count
- **EditorToolbar** — Chapter title, word count, save status, panel toggles, export, find/replace, history
- **ManuscriptSidebar** — Chapter list, drag/reorder, add chapter, links to plan/ghostwriter
- **EditorBubbleMenu** — Formatting on text selection (headings, bold, italic, etc.)
- **ReferenceBubbleMenu** — Synonyms + lookup on single-word selection

### Editor Extensions (`components/editor/extensions.ts`)

- **StarterKit** — Paragraphs, headings (1–3), blockquote, bullet/ordered lists
- **Placeholder** — "Start writing—your words, your pace."
- **Typography** — Smart quotes, ellipses, etc.
- **Underline** — Underline formatting
- **Highlight** — Text highlighting (multicolor)

### Panels (Split View)

- **NotesPanel** — Project/book/chapter notes, quick add
- **AIWritingPanel** — AI actions (rewrite, expand, etc.), prompts, ghostwriter
- **ReferencePanel** — Word lookup (definitions, synonyms), document analysis

### Autosave & Recovery

- **useAutosave** — Debounced save (2s), retries on 409 conflict
- **Draft storage** — LocalStorage backup for crash recovery
- **RecoveryBanner** — Offers to restore unsaved draft if it differs from server
- **RecoveryCenterDialog** — Restore from version history across chapters

---

## User Flows

### Writing

1. Select a chapter from the manuscript sidebar (or add one).
2. Type in the editor. Formatting appears via bubble menu on selection.
3. Changes autosave after 2 seconds of inactivity.
4. Word count and reading time update in the toolbar.

### Formatting

- Select text → bubble menu appears with Bold, Italic, Underline, Highlight, Lists, Blockquote
- Heading dropdown (H1/H2/H3) in bubble menu
- Quick Insert (Type icon) — scene break, chapter heading, blockquote, lists

### Find & Replace

- Search icon in toolbar → FindReplaceDialog
- Find Next (Enter) / Find Previous (Shift+Enter) to cycle matches
- Replace / Replace All

### Version History

- History icon → VersionHistoryDialog
- List of saved versions (word count, date)
- Restore replaces current content (with confirmation)

### Notes

- Notes button → NotesPanel (side panel)
- Notes filtered by book/chapter
- Quick add for new notes

### AI Assist

- AI button → AIWritingPanel
- Selection-based: rewrite, expand, improve flow, change tone
- Mode (assist/creative) and level (minimal/moderate/full)
- Insert result into editor

### Distraction-Free Mode

- Maximize icon → Hides sidebar, toolbar, panels
- Minimal header: save status + Exit
- Centered editor, prose-sanctuary styling

---

## Keyboard Shortcuts

- **Ctrl/Cmd + D** — Look up selected word (single word) in Reference panel
- **Enter** (in Find dialog) — Find next
- **Shift+Enter** (in Find dialog) — Find previous

---

## API Endpoints Used

- `PATCH /api/v1/projects/:id/books/:bookId/chapters/:chapterId` — Save chapter content
- `GET /api/v1/projects/:id/books/:bookId/chapters/:chapterId/versions` — Version history
- `POST /api/v1/ai/actions/run` — AI actions (rewrite, expand, etc.)
- `POST /api/v1/ai/complete` — Free-form AI completion
- Notes, export, and other project/book APIs

---

## Enhancements Made (Audit 2025)

1. **Headings in bubble menu** — Added H1/H2/H3 dropdown to EditorBubbleMenu
2. **Find Next/Prev** — FindReplaceDialog now cycles through matches with Enter/Shift+Enter
3. **Dropdown menu component** — Created `components/ui/dropdown-menu.tsx` for heading selector

---

## Future Enhancements

- **Inline comments** — Text-anchored comments (requires backend support for position storage)
- **Collaborative editing** — Real-time multi-user editing (e.g. Yjs/CRDT)
- **Spell check** — Browser or custom dictionary integration
