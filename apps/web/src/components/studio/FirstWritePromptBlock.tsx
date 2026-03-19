'use client';

import { PenLine, Sparkles, List } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FIRST_WRITE } from '@/content/first-write-copy';
import { cn } from '@/lib/utils';

const FIRST_WRITE_KEY = 'authora_first_write_done';

export function hasCompletedFirstWrite(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    return localStorage.getItem(FIRST_WRITE_KEY) === '1';
  } catch {
    return false;
  }
}

export function markFirstWriteDone() {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(FIRST_WRITE_KEY, '1');
  } catch {
    /* ignore */
  }
}

interface FirstWritePromptBlockProps {
  onStartWriting: () => void;
  onGenerateIdea: () => void;
  onOutlineChapter: () => void;
  onPromptClick?: (prompt: 'firstSentence' | 'mainIdea' | 'outlineFirst') => void;
  onAiAssist?: (action: 'generateStarter' | 'rewriteFirstLine' | 'suggestIdeas') => void;
  className?: string;
}

export function FirstWritePromptBlock({
  onStartWriting,
  onGenerateIdea,
  onOutlineChapter,
  onPromptClick,
  onAiAssist,
  className,
}: FirstWritePromptBlockProps) {
  return (
    <div
      className={cn(
        'min-w-0 rounded-xl border border-border/60 bg-muted/30 p-3 space-y-4 sm:p-5 sm:space-y-5',
        className
      )}
      data-first-write-block
    >
      <p className="text-sm font-medium text-foreground">
        Begin here—choose your path
      </p>

      {/* Main options - 1 col on narrow, 2 on md, 3 on lg */}
      <div className="grid min-w-0 grid-cols-1 gap-2 md:grid-cols-2 lg:grid-cols-3">
        <button
          type="button"
          onClick={onStartWriting}
          className="flex min-w-0 items-start gap-2 rounded-lg border border-border/60 bg-background p-3 text-left transition-colors hover:border-primary/40 hover:bg-muted/50 sm:gap-3 sm:p-4"
        >
          <PenLine className="h-4 w-4 shrink-0 text-primary sm:h-5 sm:w-5" />
          <div className="min-w-0 flex-1">
            <span className="block font-medium text-foreground">
              {FIRST_WRITE.options.startWriting.label}
            </span>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {FIRST_WRITE.options.startWriting.desc}
            </p>
          </div>
        </button>
        <button
          type="button"
          onClick={onGenerateIdea}
          className="flex min-w-0 items-start gap-2 rounded-lg border border-border/60 bg-background p-3 text-left transition-colors hover:border-primary/40 hover:bg-muted/50 sm:gap-3 sm:p-4"
        >
          <Sparkles className="h-4 w-4 shrink-0 text-primary sm:h-5 sm:w-5" />
          <div className="min-w-0 flex-1">
            <span className="block font-medium text-foreground">
              {FIRST_WRITE.options.generateIdea.label}
            </span>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {FIRST_WRITE.options.generateIdea.desc}
            </p>
          </div>
        </button>
        <button
          type="button"
          onClick={onOutlineChapter}
          className="flex min-w-0 items-start gap-2 rounded-lg border border-border/60 bg-background p-3 text-left transition-colors hover:border-primary/40 hover:bg-muted/50 sm:gap-3 sm:p-4"
        >
          <List className="h-4 w-4 shrink-0 text-primary sm:h-5 sm:w-5" />
          <div className="min-w-0 flex-1">
            <span className="block font-medium text-foreground">
              {FIRST_WRITE.options.outlineChapter.label}
            </span>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {FIRST_WRITE.options.outlineChapter.desc}
            </p>
          </div>
        </button>
      </div>

      {/* Optional prompts */}
      <div className="min-w-0">
        <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
          Or try
        </p>
        <div className="flex min-w-0 flex-wrap gap-2">
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs"
            onClick={() => onPromptClick?.('firstSentence')}
          >
            {FIRST_WRITE.prompts.firstSentence}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs"
            onClick={() => onPromptClick?.('mainIdea')}
          >
            {FIRST_WRITE.prompts.mainIdea}
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="h-8 text-xs"
            onClick={() => onPromptClick?.('outlineFirst')}
          >
            {FIRST_WRITE.prompts.outlineFirst}
          </Button>
        </div>
      </div>

      {/* AI assist entry */}
      {onAiAssist && (
        <div className="min-w-0">
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            AI assist
          </p>
          <div className="flex min-w-0 flex-wrap gap-2">
            <Button
              variant="secondary"
              size="sm"
              className="h-8 text-xs"
              onClick={() => onAiAssist('generateStarter')}
            >
              <Sparkles className="h-3 w-3 mr-1" />
              {FIRST_WRITE.aiAssist.generateStarter}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              className="h-8 text-xs"
              onClick={() => onAiAssist('suggestIdeas')}
            >
              {FIRST_WRITE.aiAssist.suggestIdeas}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
