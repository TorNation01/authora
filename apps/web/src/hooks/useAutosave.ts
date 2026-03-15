'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { saveDraft, clearDraft } from '@/lib/draft-storage';

const RETRY_BASE_MS = 1000;
const RETRY_MAX_MS = 30000;

interface UseAutosaveOptions<T> {
  onSave: (data: T) => Promise<void>;
  delayMs?: number;
  onError?: (err: Error) => void;
  maxRetries?: number;
  /** Chapter ID for draft backup (enables localStorage recovery) */
  draftKey?: string;
  /** Extract content for draft backup */
  getDraftPayload?: (data: T) => { content: Record<string, unknown>; wordCount: number };
}

export function useAutosave<T>({
  onSave,
  delayMs = 2000,
  onError,
  maxRetries = 5,
  draftKey,
  getDraftPayload,
}: UseAutosaveOptions<T>) {
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [hasPending, setHasPending] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingRef = useRef<T | null>(null);
  const retryCountRef = useRef(0);

  const flush = useCallback(async () => {
    if (pendingRef.current === null) return;
    const data = pendingRef.current;
    pendingRef.current = null;
    setHasPending(false);

    setStatus('saving');
    try {
      await onSave(data);
      setStatus('saved');
      setLastSaved(new Date());
      retryCountRef.current = 0;
      if (draftKey) clearDraft(draftKey);
    } catch (err) {
      setStatus('error');
      pendingRef.current = data;
      setHasPending(true);
      onError?.(err instanceof Error ? err : new Error(String(err)));
      retryCountRef.current += 1;
      if (retryCountRef.current <= maxRetries) {
        const delay = Math.min(RETRY_BASE_MS * Math.pow(2, retryCountRef.current - 1), RETRY_MAX_MS);
        retryTimeoutRef.current = setTimeout(() => {
          retryTimeoutRef.current = null;
          void flush();
        }, delay);
      }
    }
  }, [onSave, onError, draftKey, maxRetries]);

  const scheduleSave = useCallback(
    (data: T) => {
      pendingRef.current = data;
      setHasPending(true);
      if (draftKey && getDraftPayload) {
        const { content, wordCount } = getDraftPayload(data);
        saveDraft(draftKey, content, wordCount);
      }
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        timeoutRef.current = null;
        void flush();
      }, delayMs);
    },
    [delayMs, flush, draftKey, getDraftPayload]
  );

  const ensureDraftSaved = useCallback(() => {
    if (pendingRef.current && draftKey && getDraftPayload) {
      const { content, wordCount } = getDraftPayload(pendingRef.current);
      saveDraft(draftKey, content, wordCount);
    }
  }, [draftKey, getDraftPayload]);

  const saveNow = useCallback(
    async (data: T) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      pendingRef.current = data;
      setHasPending(true);
      await flush();
    },
    [flush]
  );

  const retry = useCallback(async () => {
    if (retryTimeoutRef.current) {
      clearTimeout(retryTimeoutRef.current);
      retryTimeoutRef.current = null;
    }
    retryCountRef.current = 0;
    if (pendingRef.current === null) return;
    await flush();
  }, [flush]);

  const flushPending = useCallback(async () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    await flush();
  }, [flush]);

  const discardPending = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    pendingRef.current = null;
    setHasPending(false);
    setStatus('idle');
    if (draftKey) clearDraft(draftKey);
  }, [draftKey]);

  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === 'visible' && pendingRef.current && navigator.onLine) {
        void flush();
      }
    };
    const handleOnline = () => {
      if (pendingRef.current) void flush();
    };
    const handlePageHide = () => {
      ensureDraftSaved();
    };
    const handleBeforeUnload = () => {
      ensureDraftSaved();
    };
    document.addEventListener('visibilitychange', handleVisibility);
    window.addEventListener('online', handleOnline);
    window.addEventListener('pagehide', handlePageHide);
    window.addEventListener('beforeunload', handleBeforeUnload);
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (retryTimeoutRef.current) clearTimeout(retryTimeoutRef.current);
      document.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('pagehide', handlePageHide);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [flush, ensureDraftSaved]);

  return {
    scheduleSave,
    saveNow,
    status,
    lastSaved,
    hasPending,
    retry,
    flushPending,
    discardPending,
    ensureDraftSaved,
  };
}
