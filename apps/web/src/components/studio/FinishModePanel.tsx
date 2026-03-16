'use client';

import { Flag, Target, ChevronRight, Sparkles, Zap, Calendar } from 'lucide-react';
import { FINISH_MODE_COPY } from '@/content/framework-copy';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';
import { WritingSprintTimer } from './WritingSprintTimer';

export interface DailyPlanToday {
  chapter_id: string;
  chapter_title: string;
  target_words: number;
  suggested_session_minutes: number;
}

export interface FinishModeForecast {
  on_track: boolean;
  estimated_completion_date: string | null;
  avg_daily_this_week: number;
}

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
  daily_plan_today: DailyPlanToday | null;
  next_chapter_id: string | null;
  next_chapter_title: string | null;
  remaining_chapters: Array<{ id: string; title: string; sort_order: number; word_count: number }>;
  progress_message: string;
  milestone_message: string | null;
  final_stretch_message: string | null;
  is_final_stretch: boolean;
  is_complete: boolean;
  can_enter_finish_mode: boolean;
  suggest_finish_mode?: boolean;
  forecast?: FinishModeForecast;
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

  const dailyPlan = stats.daily_plan_today;
  const forecast = stats.forecast;
  const isFinalStretch = stats.is_final_stretch ?? false;
  const finalStretchMsg = stats.final_stretch_message;

  if (compact) {
    return (
      <div className={cn('flex flex-wrap items-center gap-3', className)}>
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{stats.chapters_done}/{stats.chapters_total}</span>
          <div className="w-24">
            <Progress value={progress_pct} className="h-2" />
          </div>
        </div>
        {next_chapter_id && (
          <Button
            variant="default"
            size="sm"
            onClick={() => onJumpToNext(next_chapter_id)}
            className="gap-1"
          >
            <Zap className="h-3.5 w-3.5" />
            Just finish: {next_chapter_title || 'chapter'}
          </Button>
        )}
        {stats.days_to_finish != null && stats.days_to_finish > 0 && (
          <span className="text-sm text-muted-foreground">
            {stats.days_to_finish} days left · ~{stats.daily_plan_words}w/day
          </span>
        )}
        {dailyPlan && (
          <span className="text-xs text-muted-foreground">
            Today: {dailyPlan.target_words}w in &quot;{dailyPlan.chapter_title}&quot;
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

      <p className="text-xs text-muted-foreground italic">
        {FINISH_MODE_COPY.imperfectProgress}
      </p>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-medium">{stats.chapters_done}/{stats.chapters_total} chapters</span>
        </div>
        <Progress value={progress_pct} className="h-2.5" />
        {stats.work_remaining_estimate > 0 && (
          <p className="text-xs text-muted-foreground">
            ~{stats.work_remaining_estimate.toLocaleString()} words remaining
          </p>
        )}
      </div>

      <p className="text-sm text-muted-foreground italic">
        {stats.progress_message}
      </p>

      {finalStretchMsg && isFinalStretch && (
        <div className="rounded-lg border-2 border-primary/40 bg-primary/5 px-3 py-2.5 text-sm font-medium text-primary">
          <Sparkles className="h-4 w-4 inline mr-1.5" />
          {finalStretchMsg}
        </div>
      )}

      {stats.milestone_message && !finalStretchMsg && (
        <div className="rounded-lg border border-green-500/30 bg-green-500/5 px-3 py-2 text-sm text-green-800 dark:text-green-200">
          <Sparkles className="h-4 w-4 inline mr-1.5" />
          {stats.milestone_message}
        </div>
      )}

      {dailyPlan && chapters_remaining > 0 && (
        <div className="rounded-lg border-2 border-primary/30 bg-primary/5 p-3">
          <p className="text-xs font-medium text-primary uppercase tracking-wider mb-2">
            Today&apos;s focus
          </p>
          <p className="text-sm mb-2">
            Write ~{dailyPlan.target_words} words in &quot;{dailyPlan.chapter_title}&quot;
          </p>
          <Button
            variant="default"
            className="w-full justify-between"
            onClick={() => onJumpToNext(dailyPlan.chapter_id)}
          >
            <span>{FINISH_MODE_COPY.finishThisStage}</span>
            <ChevronRight className="h-4 w-4 shrink-0" />
          </Button>
          <p className="text-xs text-muted-foreground mt-2">
            {FINISH_MODE_COPY.oneFinishedBeatsTen}
          </p>
        </div>
      )}

      {chapters_remaining > 0 && next_chapter_id && !dailyPlan && (
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

      {forecast && forecast.estimated_completion_date && (
        <div className="rounded-lg border bg-muted/30 p-3">
          <div className="flex items-center gap-2 mb-1">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-medium">Completion forecast</span>
          </div>
          <p className="text-sm">
            {forecast.on_track ? (
              <span className="text-green-600 dark:text-green-500">On track</span>
            ) : (
              <span className="text-amber-600 dark:text-amber-500">Adjust pace or date</span>
            )}
            {' · '}
            Est. {new Date(forecast.estimated_completion_date).toLocaleDateString()}
          </p>
          {forecast.avg_daily_this_week > 0 && (
            <p className="text-xs text-muted-foreground mt-1">
              ~{Math.round(forecast.avg_daily_this_week)} words/day this week
            </p>
          )}
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
