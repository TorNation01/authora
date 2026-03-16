# Manuscript Editor

The AUTHORA manuscript editor is a production-ready writing studio for authors. It provides a premium, calm, and focused environment for long writing sessions.

## Overview

- **Editor core**: TipTap-based rich text with headings, lists, blockquotes, bold/italic/underline, highlights
- **Manuscript workspace**: Chapter list, drag-and-drop reorder, status indicators, quick add
- **Side panels**: AI, Notes, Reference, Revision queue
- **Autosave**: Debounced save with status indicator and draft recovery
- **Version history**: Chapter-level snapshots with restore
- **Find & replace**: Current chapter or manuscript-wide search

## Editor Features

- **Formatting**: Headings (H1–H3), paragraphs, bullet/numbered lists, blockquotes, bold, italic, underline, highlight
- **Bubble menu**: Appears on text selection for quick formatting
- **Keyboard shortcuts**: Standard shortcuts (Ctrl+B, Ctrl+I, etc.)
- **Placeholder**: "Start writing—your words, your pace."
- **Word count**: Live count per chapter and manuscript total

## Workspace Layout

- **Left sidebar**: Manuscript navigation (chapters, reorder, add, rename, duplicate, delete)
- **Center**: Editor area with optional focus mode
- **Right panel**: AI, Notes, Reference, or Revision (toggleable, one at a time)

## Focus Mode

Toggle via the toolbar. Hides sidebars and extra controls, shows a minimal header with save status and exit. Preserves autosave and stats.

## Keyboard Shortcuts

- **Ctrl/Cmd + D**: Lookup selected word in Reference panel
- **Ctrl/Cmd + F**: Find (via Find & Replace dialog)

## Technical Notes

- Editor content stored as TipTap JSON in `chapters.content`
- Autosave delay: 2 seconds after last change
- Draft recovery uses `localStorage` when available
