'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { saveDraft, clearDraft } from '@/lib/draft-storage';

const RETRY_BASE_MS = 1000;
const RETRY_MAX_MS = 30000;
const SAVE_TIMEOUT_MS = 30000;

export type AutosaveStatus = 'idle' | 'saving' | 'saved' | 'error';

interface UseAutosaveOptions<T> {
  onSave: (data: T) => Promise<void>;
  delayMs?: number;
  onError?: (err: Error) => void;
  maxRetries?: number;
  /** Chapter ID for draft backup (enables localStorage recovery) */
  draftKey?: string;
  /** Extract content for draft backup */
  getDraftPayload?: (data: T) => { content: Record<string, unknown>; wordCount: number };
  /** Return false for errors that must never be retried (409 conflict, 401, 422). */
  isRetryable?: (err: unknown) => boolean;
}

/**
 * Debounced autosave with retry, crash-draft backup and conflict safety.
 *
 * Identity stability is the whole point of this hook. Every callback lives in
 * a ref and the listener effect registers once, so a parent re-render can
 * never cancel a pending debounce. The previous version cleared its timer from
 * an effect that re-ran on every keystroke render (inline onError /
 * getDraftPayload changed identity each time), which is exactly how a chapter
 * could sit on "Unsaved changes" forever while issuing zero requests.
 */
export function useAutosave<T>({
  onSave,
  delayMs = 2000,
  onError,
  maxRetries = 5,
  draftKey,
  getDraftPayload,
  isRetryable,
}: UseAutosaveOptions<T>) {
  const [status, setStatus] = useState<AutosaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [hasPending, setHasPending] = useState(false);
  const [lastError, setLastError] = useState<Error | null>(null);

  // Latest callbacks — read through refs, never used as effect dependencies.
  const onSaveRef = useRef(onSave);
  const onErrorRef = useRef(onError);
  const getDraftPayloadRef = useRef(getDraftPayload);
  const isRetryableRef = useRef(isRetryable);
  const draftKeyRef = useRef(draftKey);
  const maxRetriesRef = useRef(maxRetries);
  onSaveRef.current = onSave;
  onErrorRef.current = onError;
  getDraftPayloadRef.current = getDraftPayload;
  isRetryableRef.current = isRetryable;
  draftKeyRef.current = draftKey;
  maxRetriesRef.current = maxRetries;

  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingRef = useRef<T | null>(null);
  const pendingDraftKeyRef = useRef<string | undefined>(undefined);
  const retryCountRef = useRef(0);
  const versionRef = useRef(0);
  const inFlightRef = useRef(false);
  const mountedRef = useRef(true);

  const clearRetryTimer = useCallback(() => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
  }, []);

  const flushRef = useRef<() => Promise<void>>(async () => {});

  const scheduleRetry = useCallback(() => {
    clearRetryTimer();
    const attempt = retryCountRef.current;
    if (attempt > maxRetriesRef.current) return;
    const delay = Math.min(RETRY_BASE_MS * Math.pow(2, attempt - 1), RETRY_MAX_MS);
    retryTimeoutRef.current = setTimeout(() => {
      retryTimeoutRef.current = null;
      void flushRef.current();
    }, delay);
  }, [clearRetryTimer]);

  /**
   * Save whatever is pending. Safe to call at any time: concurrent calls
   * collapse into the in-flight one, and edits arriving mid-flight are
   * re-flushed when it finishes.
   */
  const flush = useCallback(async () => {
    if (inFlightRef.current) return;
    if (pendingRef.current === null) return;

    const data = pendingRef.current;
    const version = versionRef.current;
    const key = pendingDraftKeyRef.current;
    pendingRef.current = null;
    inFlightRef.current = true;
    if (mountedRef.current) {
      setHasPending(false);
      setStatus('saving');
    }

    try {
      await Promise.race([
        onSaveRef.current(data),
        new Promise<never>((_, reject) =>
          setTimeout(() => reject(new Error('Save timed out')), SAVE_TIMEOUT_MS)
        ),
      ]);

      retryCountRef.current = 0;
      // Only drop the crash-recovery draft if nothing was typed since this save
      // started — otherwise we would discard text that never reached the server.
      if (key && versionRef.current === version) clearDraft(key);

      if (mountedRef.current) {
        setLastError(null);
        setLastSaved(new Date());
        setStatus(pendingRef.current !== null ? 'saving' : 'saved');
      }
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      // Keep the newest text if a later scheduleSave already replaced pending.
      if (pendingRef.current === null) pendingRef.current = data;
      if (mountedRef.current) {
        setLastError(error);
        setStatus('error');
        setHasPending(true);
      }
      onErrorRef.current?.(error);

      const retryable = isRetryableRef.current
        ? isRetryableRef.current(err)
        : (() => {
            const code = (err as { status?: number })?.status;
            if (typeof code !== 'number') return true; // network / unknown
            return code >= 500 || code === 408 || code === 429;
          })();
      retryCountRef.current += 1;
      if (retryable && retryCountRef.current <= maxRetriesRef.current) {
        scheduleRetry();
      }
    } finally {
      inFlightRef.current = false;
      // New text arrived while saving and we are not backing off → go again.
      if (pendingRef.current !== null && retryTimeoutRef.current === null) {
        void flushRef.current();
      }
    }
  }, [scheduleRetry]);

  flushRef.current = flush;

  const scheduleSave = useCallback(
    (data: T) => {
      pendingRef.current = data;
      versionRef.current += 1;
      if (mountedRef.current) setHasPending(true);

      const key = draftKeyRef.current;
      pendingDraftKeyRef.current = key;
      const get = getDraftPayloadRef.current;
      if (key && get) {
        const { content, wordCount } = get(data);
        saveDraft(key, content, wordCount);
      }

      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        timeoutRef.current = null;
        void flushRef.current();
      }, delayMs);
    },
    [delayMs]
  );

  const ensureDraftSaved = useCallback(() => {
    const key = draftKeyRef.current;
    const get = getDraftPayloadRef.current;
    if (pendingRef.current !== null && key && get) {
      const { content, wordCount } = get(pendingRef.current);
      saveDraft(key, content, wordCount);
    }
  }, []);

  const saveNow = useCallback(
    async (data: T) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      clearRetryTimer();
      retryCountRef.current = 0;
      pendingRef.current = data;
      versionRef.current += 1;
      if (mountedRef.current) setHasPending(true);
      await flushRef.current();
    },
    [clearRetryTimer]
  );

  const retry = useCallback(async () => {
    clearRetryTimer();
    retryCountRef.current = 0;
    if (pendingRef.current === null) {
      if (mountedRef.current) setStatus('idle');
      return;
    }
    await flushRef.current();
  }, [clearRetryTimer]);

  const flushPending = useCallback(async () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    await flushRef.current();
  }, []);

  const discardPending = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    clearRetryTimer();
    pendingRef.current = null;
    retryCountRef.current = 0;
    if (mountedRef.current) {
      setHasPending(false);
      setStatus('idle');
    }
    const key = draftKeyRef.current;
    if (key) clearDraft(key);
  }, [clearRetryTimer]);

  // Registered exactly once. Nothing here depends on render-scoped values, so
  // typing cannot tear down the pending timer.
  useEffect(() => {
    mountedRef.current = true;

    const handleVisibility = () => {
      if (document.visibilityState === 'hidden') {
        ensureDraftSaved();
        void flushRef.current();
      } else if (pendingRef.current !== null && navigator.onLine) {
        void flushRef.current();
      }
    };
    const handleOnline = () => {
      if (pendingRef.current !== null) void flushRef.current();
    };
    const handlePageHide = () => {
      ensureDraftSaved();
      void flushRef.current();
    };
    const handleBeforeUnload = () => {
      ensureDraftSaved();
    };

    document.addEventListener('visibilitychange', handleVisibility);
    window.addEventListener('online', handleOnline);
    window.addEventListener('pagehide', handlePageHide);
    window.addEventListener('beforeunload', handleBeforeUnload);

    return () => {
      mountedRef.current = false;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      clearRetryTimer();
      ensureDraftSaved();
      document.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('pagehide', handlePageHide);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [ensureDraftSaved, clearRetryTimer]);

  return {
    scheduleSave,
    saveNow,
    status,
    lastSaved,
    hasPending,
    lastError,
    retry,
    flushPending,
    discardPending,
    ensureDraftSaved,
  };
}
