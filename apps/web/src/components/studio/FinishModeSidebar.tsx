'use client';

import Link from 'next/link';
import { ChevronRight, Flag } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';
import type { FinishModeStats } from './FinishModePanel';

interface FinishModeSidebarProps {
  bookTitle: string;
  projectId: string;
  bookId: string;
  stats: FinishModeStats;
  activeChapterId: string | null;
  onSelectChapter: (chapterId: string) => void;
  onExitFinishMode: () => void;
}

export function FinishModeSidebar({
  bookTitle,
  projectId,
  bookId,
  stats,
  activeChapterId,
  onSelectChapter,
  onExitFinishMode,
}: FinishModeSidebarProps) {
  const remaining = stats.remaining_chapters;
  const isComplete = stats.is_complete ?? false;

  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      <div className="border-b p-4 space-y-2">
        <Link
          href={`/dashboard/projects/${projectId}`}
          className="text-sm text-muted-foreground hover:text-foreground block"
        >
          ← {bookTitle}
        </Link>
        <div className="flex items-center gap-2">
          <Flag className="h-3.5 w-3.5 text-primary" />
          <span className="text-sm font-medium">Finish Mode</span>
        </div>
        <button
          type="button"
          className="text-xs text-muted-foreground hover:text-foreground"
          onClick={onExitFinishMode}
        >
          Exit finish mode
        </button>
      </div>

      {!isComplete && (
        <div className="border-b p-3">
          <div className="flex justify-between text-xs mb-1">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{stats.chapters_done}/{stats.chapters_total}</span>
          </div>
          <Progress value={stats.progress_pct} className="h-2" />
          {stats.work_remaining_estimate > 0 && (
            <p className="text-xs text-muted-foreground mt-1">
              ~{stats.work_remaining_estimate.toLocaleString()} words left
            </p>
          )}
        </div>
      )}

      <div className="flex-1 overflow-auto p-2">
        <p className="mb-2 px-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          {isComplete ? 'All complete' : `${stats.chapters_remaining} remaining`}
        </p>
        {remaining.length > 0 ? (
          <div className="space-y-1">
            {remaining.map((ch) => (
              <button
                key={ch.id}
                type="button"
                onClick={() => onSelectChapter(ch.id)}
                className={cn(
                  'w-full flex items-center gap-2 rounded-md px-2 py-2 text-left text-sm transition-colors',
                  activeChapterId === ch.id
                    ? 'bg-primary text-primary-foreground'
                    : 'hover:bg-muted/50'
                )}
              >
                <span className="flex-1 min-w-0 truncate font-medium">{ch.title}</span>
                <span className="text-xs opacity-75 shrink-0">{ch.word_count}w</span>
                <ChevronRight className="h-3.5 w-3.5 shrink-0 opacity-60" />
              </button>
            ))}
          </div>
        ) : (
          <p className="px-2 text-sm text-muted-foreground italic">
            {stats.progress_message}
          </p>
        )}
      </div>
    </aside>
  );
}
