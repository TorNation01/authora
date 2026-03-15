/**
 * Local draft storage for crash recovery.
 * Keys: authora:draft:{chapterId}
 * Value: { content, wordCount, savedAt }
 */

const PREFIX = 'authora:draft:';
const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

export interface DraftSnapshot {
  content: Record<string, unknown>;
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
    if (age > MAX_AGE_MS) {
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
