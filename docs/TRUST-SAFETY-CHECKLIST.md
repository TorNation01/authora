# Trust & Safety Validation Checklist

Use this checklist to validate that AUTHORA manuscript safety features work as intended.

## Save Status & Messaging

- [ ] **Visible save status**: Toolbar shows "Saving...", "Saved just now", "Saved 5m ago", or "Failed to save"
- [ ] **Last saved timestamp**: Displayed when status is `saved`
- [ ] **Focus mode**: Save status visible in distraction-free mode
- [ ] **No silent failures**: Save errors show toast and sync-failed banner
- [ ] **Retry button**: Available when save fails

## Unsaved Change Protection

- [ ] **beforeunload**: Browser shows "Leave site?" when closing tab with unsaved changes
- [ ] **Draft on pagehide**: Pending content written to localStorage before tab/browser close

## Draft Recovery

- [ ] **Crash recovery**: After simulated crash (kill tab), draft appears on return
- [ ] **Tab close recovery**: Close tab with unsaved edits; reopen; draft banner appears
- [ ] **Browser close recovery**: Same as tab close
- [ ] **Recovery banner**: Restore and Dismiss work correctly
- [ ] **Recovery Center**: Lists all drafts; Restore and Discard work

## Version History

- [ ] **Version list**: Loads and displays versions with word count and date
- [ ] **Restore confirmation**: Dialog appears before restore
- [ ] **Restore flow**: Content updates; syncs to server; draft cleared

## Backup & Export

- [ ] **Export backup**: Backup (.txt) downloads with dated filename
- [ ] **Storage health**: Warning shown when localStorage unavailable

## Offline / Intermittent

- [ ] **Offline**: Pending changes stay in memory and localStorage
- [ ] **Back online**: Pending flushes when `online` event fires
- [ ] **Tab visibility**: Pending flushes when tab becomes visible
- [ ] **Retry logic**: Exponential backoff; manual retry works

## Document Integrity

- [ ] **Content validation**: `validateContent()` rejects invalid structures
- [ ] **No destructive overwrite without recovery**: Version created before overwrite; draft available locally

## Safety Messaging

- [ ] **Recovery Center**: "Your work is backed up automatically"
- [ ] **Sync failed**: "Your work is stored locally"
- [ ] **Storage unavailable**: Clear warning with export recommendation
