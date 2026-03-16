'use client';

import { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import Link from 'next/link';
import { Map, GripVertical, Plus, Sparkles, Bot, Flag, MoreHorizontal, Copy, Trash2, Pencil } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
  onRenameChapter?: (chapterId: string, newTitle: string) => void;
  onDuplicateChapter?: (chapterId: string) => void;
  onDeleteChapter?: (chapterId: string) => void;
  onStatusChange?: (chapterId: string, status: SectionStatus) => void;
  canEnterFinishMode?: boolean;
  suggestFinishMode?: boolean;
  onEnterFinishMode?: () => void;
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
  onRenameChapter,
  onDuplicateChapter,
  onDeleteChapter,
  canEnterFinishMode,
  suggestFinishMode,
  onEnterFinishMode,
  onStatusChange,
}: ManuscriptSidebarProps) {
  const [renameTarget, setRenameTarget] = useState<{ id: string; title: string } | null>(null);
  const [renameValue, setRenameValue] = useState('');

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
        {suggestFinishMode && onEnterFinishMode && (
          <button
            type="button"
            onClick={onEnterFinishMode}
            className="flex items-center gap-1.5 w-full text-left text-sm font-medium text-primary rounded-lg border border-primary/30 bg-primary/5 px-3 py-2 hover:bg-primary/10 transition-colors"
          >
            <Flag className="h-3.5 w-3.5" />
            Enter Finish Mode — you&apos;re almost there
          </button>
        )}
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
        {canEnterFinishMode && onEnterFinishMode && (
          <button
            type="button"
            onClick={onEnterFinishMode}
            className="flex items-center gap-1.5 text-sm text-primary hover:underline w-full text-left"
          >
            <Flag className="h-3.5 w-3.5" />
            Enter Finish Mode
          </button>
        )}
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
          Chapters
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
                    {(provided) => (
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
                        {(onRenameChapter || onDuplicateChapter || onDeleteChapter) && (
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-7 w-7 opacity-0 group-hover:opacity-100"
                                onClick={(e) => e.stopPropagation()}
                              >
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              {onRenameChapter && (
                                <DropdownMenuItem
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setRenameTarget({ id: ch.id, title: ch.title });
                                    setRenameValue(ch.title);
                                  }}
                                >
                                  <Pencil className="h-4 w-4 mr-2" />
                                  Rename
                                </DropdownMenuItem>
                              )}
                              {onDuplicateChapter && (
                                <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onDuplicateChapter(ch.id); }}>
                                  <Copy className="h-4 w-4 mr-2" />
                                  Duplicate
                                </DropdownMenuItem>
                              )}
                              {onDeleteChapter && (
                                <DropdownMenuItem
                                  className="text-destructive"
                                  onClick={(e) => { e.stopPropagation(); onDeleteChapter(ch.id); }}
                                >
                                  <Trash2 className="h-4 w-4 mr-2" />
                                  Delete
                                </DropdownMenuItem>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        )}
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

      <Dialog open={!!renameTarget} onOpenChange={(open) => !open && setRenameTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Rename chapter</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="rename">Title</Label>
              <Input
                id="rename"
                value={renameValue}
                onChange={(e) => setRenameValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && renameTarget) {
                    onRenameChapter?.(renameTarget.id, renameValue.trim());
                    setRenameTarget(null);
                  }
                }}
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setRenameTarget(null)}>Cancel</Button>
              <Button
                onClick={() => {
                  if (renameTarget && renameValue.trim()) {
                    onRenameChapter?.(renameTarget.id, renameValue.trim());
                    setRenameTarget(null);
                  }
                }}
                disabled={!renameValue.trim()}
              >
                Save
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </aside>
  );
}
