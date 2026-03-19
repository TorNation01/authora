'use client';

import Link from 'next/link';
import { ChevronRight, Flag, PanelLeftClose, PanelLeft } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import type { FinishModeStats } from './FinishModePanel';

interface FinishModeSidebarProps {
  bookTitle: string;
  projectId: string;
  bookId: string;
  stats: FinishModeStats;
  activeChapterId: string | null;
  onSelectChapter: (chapterId: string) => void;
  onExitFinishMode: () => void;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  position?: 'left' | 'right';
}

export function FinishModeSidebar({
  bookTitle,
  projectId,
  bookId,
  stats,
  activeChapterId,
  onSelectChapter,
  onExitFinishMode,
  collapsed = false,
  onToggleCollapse,
  position = 'left',
}: FinishModeSidebarProps) {
  const remaining = stats.remaining_chapters;
  const isComplete = stats.is_complete ?? false;
  const borderClass = position === 'left' ? 'border-r' : 'border-l';

  if (collapsed && onToggleCollapse) {
    return (
      <aside className={cn('flex w-10 flex-shrink-0 flex-col items-center bg-card sm:w-12', borderClass)}>
        <div className="flex flex-1 flex-col items-center justify-center gap-2 p-2">
          <button
            type="button"
            onClick={onToggleCollapse}
            className="rounded p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title="Expand sidebar"
          >
            <PanelLeft className="h-5 w-5" />
          </button>
          <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider [writing-mode:vertical] [text-orientation:mixed] rotate-180">
            Finish
          </span>
        </div>
      </aside>
    );
  }

  return (
    <aside className={cn('flex w-48 flex-shrink-0 flex-col bg-card sm:w-56 md:w-64', borderClass)}>
      <div className="border-b p-4 space-y-2">
        <div className="flex items-center justify-between gap-2">
          <Link
            href={`/dashboard/projects/${projectId}`}
            className="text-sm text-muted-foreground hover:text-foreground block min-w-0 truncate flex-1"
          >
            ← {bookTitle}
          </Link>
          {onToggleCollapse && (
            <Tooltip>
              <TooltipTrigger asChild>
                <button
                  type="button"
                  onClick={onToggleCollapse}
                  className="shrink-0 rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
                  title="Collapse sidebar"
                >
                  <PanelLeftClose className="h-4 w-4" />
                </button>
              </TooltipTrigger>
              <TooltipContent side={position === 'left' ? 'right' : 'left'}>
                Collapse sidebar for more space
              </TooltipContent>
            </Tooltip>
          )}
        </div>
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
