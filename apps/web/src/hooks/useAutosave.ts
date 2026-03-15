'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import { saveDraft, clearDraft } from '@/lib/draft-storage';

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
  maxRetries = 3,
  draftKey,
  getDraftPayload,
}: UseAutosaveOptions<T>) {
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [hasPending, setHasPending] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingRef = useRef<T | null>(null);
  const retryCountRef = useRef(0);

  const flush = useCallback(async () => {
    if (pendingRef.current === null) return;
    const data = pendingRef.current;
    pendingRef.current = null;
    setHasPending(false);
    retryCountRef.current = 0;

    setStatus('saving');
    try {
      await onSave(data);
      setStatus('saved');
      setLastSaved(new Date());
      if (draftKey) clearDraft(draftKey);
    } catch (err) {
      setStatus('error');
      pendingRef.current = data;
      setHasPending(true);
      onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  }, [onSave, onError, draftKey]);

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
        flush();
      }, delayMs);
    },
    [delayMs, flush, draftKey, getDraftPayload]
  );

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
    if (pendingRef.current === null) return;
    retryCountRef.current += 1;
    if (retryCountRef.current > maxRetries) {
      setStatus('error');
      return;
    }
    await flush();
  }, [flush, maxRetries]);

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
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  return {
    scheduleSave,
    saveNow,
    status,
    lastSaved,
    hasPending,
    retry,
    flushPending,
    discardPending,
  };
}
