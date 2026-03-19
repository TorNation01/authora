'use client';

import { CheckCircle2 } from 'lucide-react';
import { FIRST_WRITE } from '@/content/first-write-copy';
import { cn } from '@/lib/utils';

interface FirstWriteProgressProps {
  wordCount: number;
  className?: string;
}

export function FirstWriteProgress({ wordCount, className }: FirstWriteProgressProps) {
  const words = FIRST_WRITE.progress.words(wordCount);

  return (
    <div
      className={cn(
        'flex min-w-0 items-center gap-2 rounded-lg border border-primary/20 bg-primary/5 px-3 py-2 sm:gap-3 sm:px-4 sm:py-2.5',
        className
      )}
      data-first-write-progress
    >
      <CheckCircle2 className="h-4 w-4 shrink-0 text-primary sm:h-5 sm:w-5" />
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-foreground">
          {FIRST_WRITE.progress.started} {words}
        </p>
        <p className="text-xs text-muted-foreground">
          {FIRST_WRITE.progress.keepGoing}
        </p>
      </div>
    </div>
  );
}
