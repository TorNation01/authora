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
        'rounded-xl border border-border/60 bg-muted/30 p-5 space-y-5',
        className
      )}
      data-first-write-block
    >
      <p className="text-sm font-medium text-foreground">
        Begin here—choose your path
      </p>

      {/* Main options */}
      <div className="grid gap-2 sm:grid-cols-3">
        <button
          type="button"
          onClick={onStartWriting}
          className="flex items-start gap-3 rounded-lg border border-border/60 bg-background p-4 text-left transition-colors hover:border-primary/40 hover:bg-muted/50"
        >
          <PenLine className="h-5 w-5 shrink-0 text-primary" />
          <div>
            <span className="font-medium text-foreground">
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
          className="flex items-start gap-3 rounded-lg border border-border/60 bg-background p-4 text-left transition-colors hover:border-primary/40 hover:bg-muted/50"
        >
          <Sparkles className="h-5 w-5 shrink-0 text-primary" />
          <div>
            <span className="font-medium text-foreground">
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
          className="flex items-start gap-3 rounded-lg border border-border/60 bg-background p-4 text-left transition-colors hover:border-primary/40 hover:bg-muted/50"
        >
          <List className="h-5 w-5 shrink-0 text-primary" />
          <div>
            <span className="font-medium text-foreground">
              {FIRST_WRITE.options.outlineChapter.label}
            </span>
            <p className="mt-0.5 text-xs text-muted-foreground">
              {FIRST_WRITE.options.outlineChapter.desc}
            </p>
          </div>
        </button>
      </div>

      {/* Optional prompts */}
      <div>
        <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
          Or try
        </p>
        <div className="flex flex-wrap gap-2">
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
        <div>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
            AI assist
          </p>
          <div className="flex flex-wrap gap-2">
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
