# Manuscript Backup Strategy

AUTHORA protects writer work through multiple layers of backup and recovery. Losing user work is unacceptable.

## Backup Layers

### 1. Autosave (Server)

- **Trigger**: 2 seconds after last edit (debounced)
- **Destination**: PostgreSQL via API (`PATCH /chapters/:id`)
- **Behavior**: Creates a `ChapterVersion` snapshot before each content update
- **Retention**: 50 versions per chapter (server-side)

### 2. Local Draft Storage (localStorage)

- **Trigger**: Every keystroke (debounced) + `pagehide` / `beforeunload`
- **Key pattern**: `authora:draft:{chapterId}`
- **Payload**: `{ content, wordCount, savedAt }`
- **Retention**: 7 days (`DRAFT_MAX_AGE_MS`)
- **Purpose**: Crash recovery, tab close, browser close, offline resilience

### 3. Export Backup

- **Trigger**: User-initiated via Export → Backup (.txt)
- **Format**: Plain text
- **Filename**: `{bookTitle}-backup-{YYYY-MM-DD}.txt`
- **Purpose**: Manual snapshot for peace of mind

### 4. Version History (Server)

- **Created**: Before each chapter content update
- **Stored**: `chapter_versions` table
- **Limit**: 50 versions per chapter
- **Purpose**: Restore previous versions, chapter-level rollback

## Backup Retention Policy

| Layer        | Retention      | Notes                          |
|-------------|----------------|--------------------------------|
| Server save | Indefinite     | Primary source of truth        |
| Local draft | 7 days         | Cleared on successful sync     |
| Version history | 50 per chapter | Oldest pruned on new save  |
| Export backup | User-managed | Stored on user's device        |

## Storage Health

- **localStorage check**: On load, `isStorageAvailable()` verifies write/read
- **Unavailable**: Banner warns user; draft recovery disabled
- **Recommendation**: Export backup if storage is unavailable

## Offline / Intermittent Connection

- **Pending changes**: Kept in memory and localStorage
- **Retry**: Exponential backoff (1s → 2s → 4s … up to 30s), max 5 retries
- **Online event**: Flush pending when connection returns
- **Visibility change**: Flush when tab becomes visible (e.g. user returns)

## No Silent Failures

- Save failures surface via status (`error`), toast, and sync-failed banner
- Retry button available for manual retry
- Draft remains in localStorage until successfully synced
