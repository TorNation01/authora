/**
 * Local draft storage for crash recovery.
 * Keys: authora:draft:{chapterId}
 * Value: { content, wordCount, savedAt }
 *
 * Retention: 7 days. Drafts are cleared on successful save.
 */

const PREFIX = 'authora:draft:';
export const DRAFT_MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

export interface DraftSnapshot {
  content: Record<string, unknown>;
  wordCount: number;
  savedAt: string;
}

export interface DraftMeta {
  chapterId: string;
  wordCount: number;
  savedAt: string;
}

export function getDraftKey(storageKey: string): string {
  return `${PREFIX}${storageKey}`;
}

export function saveDraft(storageKey: string, content: Record<string, unknown>, wordCount: number): boolean {
  if (!isStorageAvailable()) return false;
  try {
    const key = getDraftKey(storageKey);
    const snapshot: DraftSnapshot = {
      content,
      wordCount,
      savedAt: new Date().toISOString(),
    };
    localStorage.setItem(key, JSON.stringify(snapshot));
    return true;
  } catch {
    return false;
  }
}

export function loadDraft(chapterId: string): DraftSnapshot | null {
  try {
    const key = getDraftKey(chapterId);
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const snapshot = JSON.parse(raw) as DraftSnapshot;
    if (!snapshot?.content || !snapshot.savedAt) return null;
    const age = Date.now() - new Date(snapshot.savedAt).getTime();
    if (age > DRAFT_MAX_AGE_MS) {
      localStorage.removeItem(key);
      return null;
    }
    return snapshot;
  } catch {
    return null;
  }
}

export function clearDraft(storageKey: string): void {
  try {
    localStorage.removeItem(getDraftKey(storageKey));
  } catch {
    /* ignore */
  }
}

/** List all draft keys (chapter IDs) with metadata for recovery center. */
export function listAllDrafts(): DraftMeta[] {
  if (!isStorageAvailable()) return [];
  const meta: DraftMeta[] = [];
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (!key?.startsWith(PREFIX)) continue;
      const chapterId = key.slice(PREFIX.length);
      const raw = localStorage.getItem(key);
      if (!raw) continue;
      try {
        const snapshot = JSON.parse(raw) as DraftSnapshot;
        if (snapshot?.content && snapshot.savedAt) {
          const age = Date.now() - new Date(snapshot.savedAt).getTime();
          if (age <= DRAFT_MAX_AGE_MS) {
            meta.push({
              chapterId,
              wordCount: snapshot.wordCount ?? 0,
              savedAt: snapshot.savedAt,
            });
          } else {
            localStorage.removeItem(key);
          }
        }
      } catch {
        /* skip invalid */
      }
    }
  } catch {
    /* ignore */
  }
  return meta.sort((a, b) => new Date(b.savedAt).getTime() - new Date(a.savedAt).getTime());
}

export function isStorageAvailable(): boolean {
  try {
    const key = '__authora_storage_test__';
    localStorage.setItem(key, '1');
    localStorage.removeItem(key);
    return true;
  } catch {
    return false;
  }
}

/** Validate content structure for document integrity. */
export function validateContent(content: unknown): content is Record<string, unknown> {
  if (content == null || typeof content !== 'object') return false;
  if (Array.isArray(content)) return false;
  return true;
}
