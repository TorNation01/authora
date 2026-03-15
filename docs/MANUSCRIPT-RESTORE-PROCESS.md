# Manuscript Restore Process

How to recover work in AUTHORA after a crash, tab close, or accidental overwrite.

## Recovery Flows

### 1. Draft Recovery (Crash / Tab Close / Browser Close)

**When**: User returns to the book studio and a local draft exists that differs from server content.

**UI**: Recovery banner (amber) above the editor.

**Actions**:
- **Restore draft**: Replaces current chapter content with the draft; syncs to server.
- **Dismiss**: Clears the draft; keeps server content.

**Flow**:
1. On load, `loadDraft(chapterId)` compares draft to `activeChapter.content`
2. If different → show banner
3. User chooses Restore or Dismiss

### 2. Recovery Center (All Recoverable Drafts)

**When**: User wants to see all local drafts across chapters.

**UI**: Shield button in toolbar → Recovery Center dialog.

**Actions**:
- **Restore**: Switches to that chapter, loads draft, syncs to server, closes dialog
- **Discard**: Clears the draft from localStorage

**Flow**:
1. `listAllDrafts()` returns all drafts within retention (7 days)
2. User selects Restore or Discard per draft

### 3. Version History Restore

**When**: User wants to restore a previous saved version.

**UI**: History button in toolbar → Version history dialog.

**Actions**:
- **Restore**: Confirmation dialog → replaces current content with selected version
- **Cancel**: Closes without change

**Flow**:
1. Fetch `/chapters/:id/versions`
2. User clicks Restore on a version
3. Confirmation: "Restore this version? Your current draft will be replaced."
4. On confirm: update chapter content, PATCH to server, clear local draft

### 4. Export Backup Restore

**When**: User has exported a backup (.txt) and needs to re-import.

**Flow**: Manual—user opens the .txt file and copies content into the editor, or uses a future import feature.

## Restore Confirmation UX

- **Version restore**: Always shows confirmation dialog before replacing content
- **Draft restore**: Single action (Restore) with clear messaging that draft will replace current
- **Recovery Center restore**: Switches chapter and restores; no extra confirmation (draft is clearly labeled)

## Recovery Timeline

- **Local drafts**: `savedAt` timestamp; shown as "just now", "5m ago", "2h ago", etc.
- **Version history**: `created_at` from server; full date/time
- **Export backup**: Filename includes date (`book-backup-2025-03-15.txt`)
