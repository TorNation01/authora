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
        'flex items-center gap-3 rounded-lg border border-primary/20 bg-primary/5 px-4 py-2.5',
        className
      )}
      data-first-write-progress
    >
      <CheckCircle2 className="h-5 w-5 shrink-0 text-primary" />
      <div>
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
