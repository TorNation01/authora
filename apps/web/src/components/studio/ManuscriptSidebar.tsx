'use client';

import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import Link from 'next/link';
import { Map, GripVertical, Plus, Sparkles, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export type SectionStatus = 'draft' | 'revising' | 'review' | 'done';

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
  word_count: number;
  section_status?: string | null;
}

interface ManuscriptSidebarProps {
  bookTitle: string;
  bookType?: string;
  projectId: string;
  bookId: string;
  chapters: Chapter[];
  activeChapterId: string | null;
  onSelectChapter: (ch: Chapter) => void;
  onReorder: (chapterIds: string[]) => void;
  onAddChapter: () => void;
  onStatusChange?: (chapterId: string, status: SectionStatus) => void;
}

const STATUS_LABELS: Record<SectionStatus, string> = {
  draft: 'Draft',
  revising: 'Revising',
  review: 'Review',
  done: 'Done',
};

const STATUS_COLORS: Record<SectionStatus, string> = {
  draft: 'bg-muted text-muted-foreground',
  revising: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  review: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  done: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
};

export function ManuscriptSidebar({
  bookTitle,
  bookType,
  projectId,
  bookId,
  chapters,
  activeChapterId,
  onSelectChapter,
  onReorder,
  onAddChapter,
  onStatusChange,
}: ManuscriptSidebarProps) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function handleDragEnd(result: any) {
    if (!result.destination) return;
    const items = Array.from(chapters);
    const [removed] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, removed);
    onReorder(items.map((c) => c.id));
  }

  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      <div className="border-b p-4 space-y-2">
        <Link
          href={`/dashboard/projects/${projectId}`}
          className="text-sm text-muted-foreground hover:text-foreground block"
        >
          ← {bookTitle}
        </Link>
        <Link
          href={`/dashboard/projects/${projectId}/books/${bookId}/ghostwriter`}
          className="flex items-center gap-1.5 text-sm text-primary hover:underline"
        >
          <Bot className="h-3.5 w-3.5" />
          Ghostwriter
        </Link>
        <Link
          href={`/dashboard/projects/${projectId}/books/${bookId}/edit`}
          className="flex items-center gap-1.5 text-sm text-primary hover:underline"
        >
          <Sparkles className="h-3.5 w-3.5" />
          Edit & Polish
        </Link>
        {(bookType === 'fiction' || bookType === 'nonfiction') && (
          <Link
            href={`/dashboard/projects/${projectId}/books/${bookId}/plan`}
            className="flex items-center gap-1.5 text-sm text-primary hover:underline"
          >
            <Map className="h-3.5 w-3.5" />
            {bookType === 'fiction' ? 'Fiction' : 'Non-fiction'} workspace
          </Link>
        )}
      </div>

      <div className="flex-1 overflow-auto p-2">
        <p className="mb-2 px-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Manuscript
        </p>
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="chapters">
            {(provided) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="space-y-1"
              >
                {chapters.map((ch, index) => (
                  <Draggable key={ch.id} draggableId={ch.id} index={index}>
                    {(provided, snapshot) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        className={cn(
                          'group flex items-center gap-1 rounded-md transition-colors',
                          activeChapterId === ch.id && 'bg-primary text-primary-foreground'
                        )}
                      >
                        <div
                          {...provided.dragHandleProps}
                          className="cursor-grab touch-none p-1.5 text-muted-foreground opacity-60 hover:opacity-100 active:cursor-grabbing"
                        >
                          <GripVertical className="h-4 w-4" />
                        </div>
                        <button
                          type="button"
                          onClick={() => onSelectChapter(ch)}
                          className="flex-1 min-w-0 text-left px-2 py-2 rounded-md text-sm hover:bg-muted/50"
                        >
                          <div className="font-medium truncate">{ch.title}</div>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-xs opacity-75">{ch.word_count} words</span>
                            {ch.section_status && (
                              <span
                                className={cn(
                                  'text-[10px] px-1.5 py-0.5 rounded',
                                  STATUS_COLORS[ch.section_status as SectionStatus] ?? STATUS_COLORS.draft
                                )}
                              >
                                {STATUS_LABELS[ch.section_status as SectionStatus] ?? ch.section_status}
                              </span>
                            )}
                          </div>
                        </button>
                      </div>
                    )}
                  </Draggable>
                ))}
                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>
      </div>

      <div className="border-t p-2">
        <Button variant="outline" size="sm" className="w-full" onClick={onAddChapter}>
          <Plus className="h-4 w-4 mr-1" />
          Add chapter
        </Button>
      </div>
    </aside>
  );
}
