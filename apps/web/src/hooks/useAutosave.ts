'use client';

import { useCallback, useRef, useState } from 'react';

interface UseAutosaveOptions<T> {
  onSave: (data: T) => Promise<void>;
  delayMs?: number;
  onError?: (err: Error) => void;
  maxRetries?: number;
}

export function useAutosave<T>({
  onSave,
  delayMs = 2000,
  onError,
  maxRetries = 3,
}: UseAutosaveOptions<T>) {
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pendingRef = useRef<T | null>(null);
  const retryCountRef = useRef(0);

  const flush = useCallback(async () => {
    if (pendingRef.current === null) return;
    const data = pendingRef.current;
    pendingRef.current = null;
    retryCountRef.current = 0;

    setStatus('saving');
    try {
      await onSave(data);
      setStatus('saved');
      setLastSaved(new Date());
    } catch (err) {
      setStatus('error');
      onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  }, [onSave, onError]);

  const scheduleSave = useCallback(
    (data: T) => {
      pendingRef.current = data;
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => {
        timeoutRef.current = null;
        flush();
      }, delayMs);
    },
    [delayMs, flush]
  );

  const saveNow = useCallback(
    async (data: T) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      pendingRef.current = data;
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

  return { scheduleSave, saveNow, status, lastSaved, retry, flushPending };
}
