# Version Control System — Final Outputs

## 1. Version System Summary

AUTHORA provides a full version control system for manuscript chapters.

### Version Snapshots

- **Automatic**: A new version is created before each content overwrite (on every save/PATCH).
- **Manual checkpoints**: Users can create explicit checkpoints via "Create checkpoint" in Version History.
- **Storage**: `ChapterVersion` model stores `content`, `word_count`, `content_source`, `created_by`, `created_at`.
- **Limit**: Up to 50 versions per chapter (oldest pruned when exceeded).
- **Scope**: Per chapter; versions are immutable once created.

### Auto-Save Checkpoints

- **Trigger**: Content changes in the editor.
- **Debounce**: 2 seconds after last change.
- **Behavior**: Each save creates a version of the previous content before overwriting.
- **Status**: "Saving…", "Saved", "Unsaved changes", "Failed to save".

### Compare Versions

- **UI**: Version History dialog → select two versions (checkboxes) → "Compare selected".
- **Display**: Side-by-side plain-text comparison of the two versions.
- **Source**: Uses `tiptapToPlainText` to render TipTap JSON as readable text.

---

## 2. Restore Flow Summary

### User Flow

1. User opens **Version History** (History icon in toolbar).
2. List of versions loads (word count, date per version).
3. User selects a version and clicks **Restore**.
4. Confirmation dialog: "Restore this version? Your current draft will be replaced."
5. User confirms → current content is replaced with the selected version.
6. Chapter is saved (PATCH) with the restored content.
7. Local draft is cleared; toast: "Version restored".

### Technical Flow

1. `GET /api/v1/projects/{id}/books/{bookId}/chapters/{chapterId}/versions` → list versions.
2. User confirms restore → `handleRestoreVersion`:
   - Updates local state (`activeChapter`, `book.chapters`) with version content.
   - Calls `saveChapter({ content, wordCount })` → PATCH chapter.
   - PATCH handler creates a new `ChapterVersion` with the *previous* content (before overwrite), then overwrites chapter content.
   - Clears draft storage for the chapter.
   - Closes dialog and shows success toast.

### Safety

- Restore is reversible: the current state becomes a new version before overwrite.
- Confirmation dialog prevents accidental restores.
- Conflict handling: if `if_unchanged_since` fails (409), user is prompted to refresh or use version history.

---

## 3. Production-Ready Confirmation

### Implemented Features

| Feature | Status | Notes |
|---------|--------|-------|
| Version snapshots | ✅ | Automatic on save; manual via "Create checkpoint" |
| Restore previous versions | ✅ | VersionHistoryDialog + confirmation |
| Compare versions | ✅ | Select two versions → side-by-side diff |
| Auto-save checkpoints | ✅ | 2s debounce; each save creates version |

### API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/projects/{id}/books/{bookId}/chapters/{chapterId}/versions` | List version history |
| POST | `/projects/{id}/books/{bookId}/chapters/{chapterId}/snapshot` | Create manual checkpoint |
| PATCH | `/projects/{id}/books/{bookId}/chapters/{chapterId}` | Update chapter (creates version before overwrite) |

### Components

- **VersionHistoryDialog**: List versions, restore, compare, create checkpoint.
- **CompareVersionHistoryDialog**: Side-by-side comparison of two versions.
- **RecoveryCenterDialog**: Restore drafts from local storage across chapters
- **RecoveryBanner**: Restore or discard unsaved draft when it differs from server.

### Production readiness

- **Data integrity**: Versions are immutable; restore creates a new version of the previous state.
- **Conflict handling**: 409 on concurrent edits; user can refresh or restore from history.
- **Limits**: 50 versions per chapter to avoid unbounded growth.
- **UX**: Confirmation dialogs, clear status messages, and toast feedback.

---

## Related Documentation

- [VERSION_HISTORY_AND_AUTOSAVE.md](./VERSION_HISTORY_AND_AUTOSAVE.md) — Autosave and draft recovery
- [MANUSCRIPT-RESTORE-PROCESS.md](./MANUSCRIPT-RESTORE-PROCESS.md) — Recovery banner and flow
