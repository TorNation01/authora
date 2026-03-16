# Version History and Autosave

AUTHORA provides robust autosave and version history for manuscript safety.

## Autosave

- **Trigger**: Content changes in the editor
- **Delay**: 2 seconds after last change (debounced)
- **Scope**: Per chapter
- **Status**: "Saving…", "Saved", "Unsaved changes", "Failed to save"

## Save Status

- **Idle**: No pending changes
- **Saving**: Request in flight
- **Saved**: Last save succeeded (with "just now" / "Xm ago" / "Xh ago")
- **Error**: Save failed; Retry available

## Draft Recovery

- **Local storage**: Drafts stored per chapter when storage is available
- **Recovery banner**: Shown when local draft differs from server (e.g. after crash)
- **Actions**: Restore draft or Dismiss (discard local)

## Sync Failed

- **Banner**: Shown when save fails (e.g. network error)
- **Actions**: Retry or Dismiss

## Version History

- **Snapshots**: Created before each content overwrite (on PATCH)
- **Limit**: 50 versions per chapter
- **Restore**: Replace current content with a previous version (with confirmation)

**API**: `GET /projects/{id}/books/{id}/chapters/{id}/versions`

## Recovery Center

- **Scope**: All chapters in the book
- **Purpose**: Restore drafts from local storage across chapters
- **Access**: Toolbar (shield icon)
