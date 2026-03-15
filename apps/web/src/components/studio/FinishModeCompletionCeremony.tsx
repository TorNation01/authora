'use client';

import { Trophy, Sparkles, Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FinishModeCompletionCeremonyProps {
  bookTitle: string;
  totalWords: number;
  chaptersTotal: number;
  onExport: (format: string) => void;
  onExit: () => void;
  className?: string;
}

export function FinishModeCompletionCeremony({
  bookTitle,
  totalWords,
  chaptersTotal,
  onExport,
  onExit,
  className,
}: FinishModeCompletionCeremonyProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center min-h-[60vh] px-6 py-12 text-center',
        className
      )}
    >
      <div className="rounded-full bg-primary/10 p-6 mb-6">
        <Trophy className="h-16 w-16 text-primary" />
      </div>
      <h1 className="text-3xl font-bold tracking-tight mb-2">
        You did it.
      </h1>
      <p className="text-xl text-muted-foreground mb-1">
        <span className="font-semibold text-foreground">{bookTitle}</span> is complete.
      </p>
      <p className="text-muted-foreground mb-8">
        {chaptersTotal} chapters · {totalWords.toLocaleString()} words
      </p>
      <div className="flex items-center gap-2 text-primary mb-8">
        <Sparkles className="h-5 w-5" />
        <span className="font-medium">Manuscript complete</span>
        <Sparkles className="h-5 w-5" />
      </div>
      <p className="text-sm text-muted-foreground max-w-md mb-8">
        You crossed the finish line. Take a moment. Then export your manuscript, share it, or start
        your next project.
      </p>
      <div className="flex flex-wrap gap-3 justify-center">
        <Button onClick={() => onExport('docx')} size="lg" className="gap-2">
          <Download className="h-4 w-4" />
          Export manuscript (.docx)
        </Button>
        <Button variant="outline" size="lg" onClick={() => onExport('backup')}>
          Download backup
        </Button>
        <Button variant="ghost" size="lg" onClick={onExit}>
          Exit Finish Mode
        </Button>
      </div>
    </div>
  );
}
