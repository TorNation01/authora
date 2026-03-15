'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Timer, Square } from 'lucide-react';
import { cn } from '@/lib/utils';

interface WritingSprintTimerProps {
  defaultMinutes?: number;
  onComplete?: () => void;
  className?: string;
}

export function WritingSprintTimer({
  defaultMinutes = 15,
  onComplete,
  className,
}: WritingSprintTimerProps) {
  const [secondsLeft, setSecondsLeft] = useState<number | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    if (!isRunning || secondsLeft === null) return;
    if (secondsLeft <= 0) {
      setIsRunning(false);
      onComplete?.();
      return;
    }
    const id = setInterval(() => setSecondsLeft((s) => (s ?? 0) - 1), 1000);
    return () => clearInterval(id);
  }, [isRunning, secondsLeft, onComplete]);

  const start = useCallback((minutes: number) => {
    setSecondsLeft(minutes * 60);
    setIsRunning(true);
  }, []);

  const stop = useCallback(() => {
    setIsRunning(false);
    setSecondsLeft(null);
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
