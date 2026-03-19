'use client';

import { useState } from 'react';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import Link from 'next/link';
import { Map, GripVertical, Plus, Sparkles, Bot, Flag, MoreHorizontal, Copy, Trash2, Pencil, Tag, Layers, PanelLeftClose, PanelLeft } from 'lucide-react';
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
import { getEmptyStateConfig } from '@/content/empty-states';
import { FeatureIntroCard } from '@/components/tutorial/FeatureIntroCard';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { getTooltip } from '@/content/tooltips';
import { useTutorial } from '@/contexts/TutorialContext';
import { FeatureGate } from '@/components/conversion/FeatureGate';

export type SectionStatus = 'draft' | 'revising' | 'review' | 'done';

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
  word_count: number;
  section_status?: string | null;
  section_group?: string | null;
  tags?: string[];
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
  onSectionGroupChange?: (chapterId: string, sectionGroup: string | null) => void;
  onTagsChange?: (chapterId: string, tags: string[]) => void;
  canEnterFinishMode?: boolean;
  suggestFinishMode?: boolean;
  onEnterFinishMode?: () => void;
  /** Sidebar collapsed to a narrow strip for more writing space */
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  /** Sidebar rendered on right side (for left-handed writers) */
  position?: 'left' | 'right';
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
  onSectionGroupChange,
  onTagsChange,
  collapsed = false,
  onToggleCollapse,
  position = 'left',
}: ManuscriptSidebarProps) {
  const { shouldShowIntroCard, markDismissed } = useTutorial();
  const [renameTarget, setRenameTarget] = useState<{ id: string; title: string } | null>(null);
  const [renameValue, setRenameValue] = useState('');
  const [sectionTarget, setSectionTarget] = useState<{ id: string; sectionGroup: string | null } | null>(null);
  const [sectionValue, setSectionValue] = useState('');
  const [tagsTarget, setTagsTarget] = useState<{ id: string; tags: string[] } | null>(null);
  const [tagsValue, setTagsValue] = useState('');

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  function handleDragEnd(result: any) {
    if (!result.destination) return;
    const items = Array.from(chapters);
    const [removed] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, removed);
    onReorder(items.map((c) => c.id));
  }

  const borderClass = position === 'left' ? 'border-r' : 'border-l';

  if (collapsed && onToggleCollapse) {
    return (
      <aside className={cn('flex w-10 flex-shrink-0 flex-col items-center bg-card sm:w-12', borderClass)}>
        <div className="flex flex-1 flex-col items-center justify-center gap-2 p-2">
          <button
            type="button"
            onClick={onToggleCollapse}
            className="rounded p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
            title="Expand chapters"
          >
            <PanelLeft className="h-5 w-5" />
          </button>
          <span className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider [writing-mode:vertical] [text-orientation:mixed] rotate-180">
            Chapters
          </span>
        </div>
      </aside>
    );
  }

  return (
    <aside className={cn('flex w-48 flex-shrink-0 flex-col bg-card sm:w-56 md:w-64', borderClass)}>
      <div className="border-b p-3 space-y-2 sm:p-4">
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
                  title="Collapse sidebar for more space"
                >
                  <PanelLeftClose className="h-4 w-4" />
                </button>
              </TooltipTrigger>
              <TooltipContent side={position === 'left' ? 'right' : 'left'}>
                Collapse sidebar for more writing space
              </TooltipContent>
            </Tooltip>
          )}
        </div>
        {suggestFinishMode && onEnterFinishMode && shouldShowIntroCard('finish_mode_intro') && (
          <FeatureIntroCard
            featureId="finish_mode"
            onDismiss={() => markDismissed('finish_mode_intro')}
            onTry={onEnterFinishMode}
          />
        )}
        {suggestFinishMode && onEnterFinishMode && !shouldShowIntroCard('finish_mode_intro') && (
          <FeatureGate feature="finish_mode" className="w-full">
            <button
              type="button"
              onClick={onEnterFinishMode}
              className="flex items-center gap-1.5 w-full text-left text-sm font-medium text-primary rounded-lg border border-primary/30 bg-primary/5 px-3 py-2 hover:bg-primary/10 transition-colors"
            >
              <Flag className="h-3.5 w-3.5" />
              Enter Finish Mode — you&apos;re almost there
            </button>
          </FeatureGate>
        )}
        <Tooltip>
          <TooltipTrigger asChild>
            <FeatureGate
              feature="ghostwriter"
              className="flex items-center gap-1.5 text-sm w-full text-left"
            >
              <Link
                href={`/dashboard/projects/${projectId}/books/${bookId}/ghostwriter`}
                className="flex items-center gap-1.5 text-sm text-primary hover:underline"
              >
                <Bot className="h-3.5 w-3.5" />
                Ghostwriter
              </Link>
            </FeatureGate>
          </TooltipTrigger>
          <TooltipContent side="right">{getTooltip('ghostwriter_link') ?? 'Ghostwriter'}</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Link
              href={`/dashboard/projects/${projectId}/books/${bookId}/edit`}
              className="flex items-center gap-1.5 text-sm text-primary hover:underline"
            >
              <Sparkles className="h-3.5 w-3.5" />
              Edit & Polish
            </Link>
          </TooltipTrigger>
          <TooltipContent side="right">{getTooltip('edit_polish_link') ?? 'Edit & Polish'}</TooltipContent>
        </Tooltip>
        {canEnterFinishMode && onEnterFinishMode && (
          <Tooltip>
            <TooltipTrigger asChild>
              <FeatureGate feature="finish_mode" className="w-full">
                <button
                  type="button"
                  onClick={onEnterFinishMode}
                  className="flex items-center gap-1.5 text-sm text-primary hover:underline w-full text-left"
                >
                  <Flag className="h-3.5 w-3.5" />
                  Enter Finish Mode
                </button>
              </FeatureGate>
            </TooltipTrigger>
            <TooltipContent side="right">{getTooltip('finish_mode') ?? 'Enter Finish Mode'}</TooltipContent>
          </Tooltip>
        )}
        {(bookType === 'fiction' || bookType === 'nonfiction') && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Link
                href={`/dashboard/projects/${projectId}/books/${bookId}/plan`}
                className="flex items-center gap-1.5 text-sm text-primary hover:underline"
              >
                <Map className="h-3.5 w-3.5" />
                {bookType === 'fiction' ? 'Fiction' : 'Non-fiction'} workspace
              </Link>
            </TooltipTrigger>
            <TooltipContent side="right">{getTooltip('plan_link') ?? 'Plan'}</TooltipContent>
          </Tooltip>
        )}
      </div>

      <div className="flex-1 overflow-auto p-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <p className="mb-2 px-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
              Chapters
            </p>
          </TooltipTrigger>
          <TooltipContent side="right">{getTooltip('chapters_sidebar') ?? 'Chapters'}</TooltipContent>
        </Tooltip>
        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="chapters">
            {(provided) => (
              <div
                ref={provided.innerRef}
                {...provided.droppableProps}
                className="space-y-1 min-h-[80px]"
              >
                {chapters.length === 0 && (
                  <p className="px-2 py-4 text-xs text-muted-foreground text-center">
                    {getEmptyStateConfig('no_chapters')!.description}
                  </p>
                )}
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
                          <div className="flex flex-wrap items-center gap-2 mt-0.5">
                            <span className="text-xs opacity-75">{ch.word_count} words</span>
                            {ch.section_group && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{ch.section_group}</span>
                            )}
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
                        {(onRenameChapter || onDuplicateChapter || onDeleteChapter || onSectionGroupChange || onTagsChange) && (
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
                              {onSectionGroupChange && (
                                <DropdownMenuItem
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setSectionTarget({ id: ch.id, sectionGroup: ch.section_group ?? null });
                                    setSectionValue(ch.section_group ?? '');
                                  }}
                                >
                                  <Layers className="h-4 w-4 mr-2" />
                                  Set section
                                </DropdownMenuItem>
                              )}
                              {onTagsChange && (
                                <DropdownMenuItem
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    setTagsTarget({ id: ch.id, tags: ch.tags ?? [] });
                                    setTagsValue((ch.tags ?? []).join(', '));
                                  }}
                                >
                                  <Tag className="h-4 w-4 mr-2" />
                                  Set tags
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
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="outline" size="sm" className="w-full" onClick={onAddChapter}>
              <Plus className="h-4 w-4 mr-1" />
              Add chapter
            </Button>
          </TooltipTrigger>
          <TooltipContent side="right">{getTooltip('add_chapter') ?? 'Add chapter'}</TooltipContent>
        </Tooltip>
      </div>

      <Dialog open={!!sectionTarget} onOpenChange={(open) => !open && setSectionTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Set section group</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="section">Section (e.g. Part 1, Act 2)</Label>
              <Input
                id="section"
                value={sectionValue}
                onChange={(e) => setSectionValue(e.target.value)}
                placeholder="Part 1"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setSectionTarget(null)}>Cancel</Button>
              <Button
                onClick={() => {
                  if (sectionTarget) {
                    onSectionGroupChange?.(sectionTarget.id, sectionValue.trim() || null);
                    setSectionTarget(null);
                  }
                }}
              >
                Save
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!tagsTarget} onOpenChange={(open) => !open && setTagsTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Set tags</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="tags">Tags (comma-separated)</Label>
              <Input
                id="tags"
                value={tagsValue}
                onChange={(e) => setTagsValue(e.target.value)}
                placeholder="action, pov-john, key-scene"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setTagsTarget(null)}>Cancel</Button>
              <Button
                onClick={() => {
                  if (tagsTarget) {
                    const tags = tagsValue.split(/[,\s]+/).map((t) => t.trim().toLowerCase()).filter(Boolean);
                    onTagsChange?.(tagsTarget.id, tags);
                    setTagsTarget(null);
                  }
                }}
              >
                Save
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

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
