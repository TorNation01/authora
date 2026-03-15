'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Timer, Square } from 'lucide-react';
import { cn } from '@/lib/utils';
import { api } from '@/lib/api';

interface WritingSprintTimerProps {
  bookId?: string | null;
  getWordsWritten?: () => number;
  onStart?: () => void;
  onComplete?: () => void;
  className?: string;
}

export function WritingSprintTimer({
  bookId,
  getWordsWritten,
  onStart,
  onComplete,
  className,
}: WritingSprintTimerProps) {
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const sessionIdRef = useRef<string | null>(null);
  const targetMinutesRef = useRef<number>(15);

  useEffect(() => {
    if (!isRunning || secondsLeft === null) return;
    if (secondsLeft <= 0) {
      setIsRunning(false);
      const mins = targetMinutesRef.current;
      const words = getWordsWritten?.() ?? 0;
      if (sessionIdRef.current) {
        api(`/api/v1/gamification/focus/${sessionIdRef.current}/complete`, {
          method: 'POST',
          body: JSON.stringify({ actual_minutes: mins, words_written: Math.max(0, words) }),
        }).catch(() => {});
      }
      sessionIdRef.current = null;
      onComplete?.();
      return;
    }
    const id = setInterval(() => setSecondsLeft((s) => (s ?? 0) - 1), 1000);
    return () => clearInterval(id);
  }, [isRunning, secondsLeft, getWordsWritten, onComplete]);

  const start = useCallback(
    (minutes: number) => {
      targetMinutesRef.current = minutes;
      onStart?.(); // Capture word count at start before any async
      if (bookId) {
        api<{ id: string }>('/api/v1/gamification/focus/start', {
          method: 'POST',
          body: JSON.stringify({ book_id: bookId, target_minutes: minutes }),
        })
          .then((r) => {
            sessionIdRef.current = r.id;
          })
          .catch(() => {});
      }
      setSecondsLeft(minutes * 60);
      setIsRunning(true);
    },
    [bookId, onStart]
  );

  const stop = useCallback(() => {
    setIsRunning(false);
    setSecondsLeft(null);
    sessionIdRef.current = null;
  }, []);

  const format = (s: number) => {
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m}:${sec.toString().padStart(2, '0')}`;
  };

  if (secondsLeft !== null && isRunning) {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <span className="text-sm font-mono tabular-nums">
          {format(secondsLeft)}
        </span>
        <Button variant="ghost" size="sm" onClick={stop}>
          <Square className="h-4 w-4" />
        </Button>
      </div>
    );
  }

  return (
    <div className={cn('flex items-center gap-1', className)}>
      <Timer className="h-4 w-4 text-muted-foreground" />
      {[5, 15, 25].map((m) => (
        <Button
          key={m}
          variant="ghost"
          size="sm"
          className="h-7 px-2 text-xs"
          onClick={() => start(m)}
        >
          {m}m
        </Button>
      ))}
    </div>
  );
}
