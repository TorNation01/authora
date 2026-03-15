'use client';

import { Flag, Target, ChevronRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';
import { WritingSprintTimer } from './WritingSprintTimer';

export interface FinishModeStats {
  enabled: boolean;
  target_date: string | null;
  words_per_day: number;
  chapters_done: number;
  chapters_total: number;
  chapters_remaining: number;
  progress_pct: number;
  total_words: number;
  work_remaining_estimate: number;
  days_to_finish: number | null;
  days_until_target: number | null;
  daily_plan_words: number;
  next_chapter_id: string | null;
  next_chapter_title: string | null;
  remaining_chapters: Array<{ id: string; title: string; sort_order: number; word_count: number }>;
  progress_message: string;
  milestone_message: string | null;
  can_enter_finish_mode: boolean;
}

interface FinishModePanelProps {
  stats: FinishModeStats;
  onJumpToNext: (chapterId: string) => void;
  onExitFinishMode: () => void;
  bookId?: string | null;
  getWordsWritten?: () => number;
  compact?: boolean;
  className?: string;
}

export function FinishModePanel({
  stats,
  onJumpToNext,
  onExitFinishMode,
  bookId,
  getWordsWritten,
  compact = false,
  className,
}: FinishModePanelProps) {
  const { progress_pct, chapters_remaining, next_chapter_title, next_chapter_id } = stats;

  if (compact) {
    return (
      <div className={cn('flex flex-wrap items-center gap-3', className)}>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{stats.chapters_done}/{stats.chapters_total}</span>
          <div className="w-20">
            <Progress value={progress_pct} className="h-1.5" />
          </div>
        </div>
        {next_chapter_id && (
          <Button
            variant="default"
            size="sm"
            onClick={() => onJumpToNext(next_chapter_id)}
          >
            Next: {next_chapter_title || 'chapter'}
          </Button>
        )}
        {stats.days_to_finish != null && stats.days_to_finish > 0 && (
          <span className="text-sm text-muted-foreground">
            {stats.days_to_finish} days left · ~{stats.daily_plan_words}w/day
          </span>
        )}
        {bookId && getWordsWritten && (
          <WritingSprintTimer bookId={bookId} getWordsWritten={getWordsWritten} />
        )}
        <Button variant="ghost" size="sm" onClick={onExitFinishMode}>
          Exit
        </Button>
      </div>
    );
  }

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Flag className="h-5 w-5 text-primary" />
          <span className="font-semibold">Finish Mode</span>
        </div>
        <Button variant="ghost" size="sm" onClick={onExitFinishMode}>
          Exit
        </Button>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-medium">{stats.chapters_done}/{stats.chapters_total} chapters</span>
        </div>
        <Progress value={progress_pct} className="h-2" />
      </div>

      <p className="text-sm text-muted-foreground italic">
        {stats.progress_message}
      </p>

      {stats.milestone_message && (
        <div className="rounded-lg border border-green-500/30 bg-green-500/5 px-3 py-2 text-sm text-green-800 dark:text-green-200">
          <Sparkles className="h-4 w-4 inline mr-1.5" />
          {stats.milestone_message}
        </div>
      )}

      {chapters_remaining > 0 && next_chapter_id && (
        <div className="rounded-lg border bg-card p-3">
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-2">
            Next up
          </p>
          <Button
            variant="default"
            className="w-full justify-between"
            onClick={() => onJumpToNext(next_chapter_id)}
          >
            <span className="truncate">{next_chapter_title || 'Next chapter'}</span>
            <ChevronRight className="h-4 w-4 shrink-0" />
          </Button>
        </div>
      )}

      {stats.days_to_finish != null && stats.days_to_finish > 0 && (
        <div className="rounded-lg border bg-muted/30 p-3">
          <div className="flex items-center gap-2 mb-1">
            <Target className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Days to finish</span>
          </div>
          <p className="text-2xl font-bold">{stats.days_to_finish}</p>
          <p className="text-xs text-muted-foreground mt-1">
            Aim for ~{stats.daily_plan_words.toLocaleString()} words today
          </p>
        </div>
      )}

      {bookId && getWordsWritten && (
        <WritingSprintTimer
          bookId={bookId}
          getWordsWritten={getWordsWritten}
          className="mt-2"
        />
      )}
    </div>
  );
}
