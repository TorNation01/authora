'use client';

import { useState, useRef, useCallback } from 'react';
import {
  Sparkles,
  FileDown,
  ChevronDown,
  Maximize2,
  Minimize2,
  Sun,
  Moon,
  Search,
  History,
  Type,
  PanelRightClose,
  PanelRight,
  PanelLeft,
  PanelLeftClose,
  BookOpen,
  Shield,
  ClipboardList,
  Library,
  Activity,
  MoreHorizontal,
} from 'lucide-react';
import type { SectionStatus } from './ManuscriptSidebar';
import type { SidebarPosition } from '@/hooks/useWriterStudioPreferences';
import { useConfig } from '@/contexts/ConfigProvider';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { getTooltip } from '@/content/tooltips';
import { WritingStats } from './WritingStats';
import { WritingSprintTimer } from './WritingSprintTimer';
import { cn } from '@/lib/utils';

export type PanelMode = 'none' | 'ai' | 'notes' | 'reference' | 'revision' | 'vault' | 'integrity';

interface EditorToolbarProps {
  chapterTitle: string;
  chapterWordCount: number;
  totalWordCount: number;
  bookId?: string | null;
  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
  lastSaved?: Date | null;
  hasPending?: boolean;
  onRetry?: () => void;
  distractionFree: boolean;
  darkMode: boolean;
  panelMode: PanelMode;
  onToggleDistractionFree: () => void;
  onToggleDarkMode: () => void;
  onTogglePanel: (mode: PanelMode) => void;
  onExport: (format: string, backupFilename?: boolean) => void;
  onHistory?: () => void;
  onRecoveryCenter?: () => void;
  onFindReplace?: () => void;
  onQuickInsert?: () => void;
  onStatusChange?: (status: SectionStatus) => void;
  sectionStatus?: string | null;
  showAi?: boolean;
  /** Sidebar position (left/right) for dominant-hand preference */
  sidebarPosition?: SidebarPosition;
  onSidebarPositionChange?: (position: SidebarPosition) => void;
}

function formatLastSaved(d: Date): string {
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  if (diffMs < 60_000) return 'Last saved just now';
  if (diffMs < 3600_000) return `Saved ${Math.floor(diffMs / 60_000)}m ago`;
  if (diffMs < 86400_000) return `Saved ${Math.floor(diffMs / 3600_000)}h ago`;
  return `Saved ${d.toLocaleDateString()}`;
}

export function EditorToolbar({
  chapterTitle,
  chapterWordCount,
  totalWordCount,
  bookId,
  saveStatus,
  lastSaved,
  hasPending,
  onRetry,
  distractionFree,
  darkMode,
  panelMode,
  onToggleDistractionFree,
  onToggleDarkMode,
  onTogglePanel,
  onExport,
  onHistory,
  onRecoveryCenter,
  onFindReplace,
  onQuickInsert,
  onStatusChange,
  sectionStatus,
  showAi = true,
  sidebarPosition = 'left',
  onSidebarPositionChange,
}: EditorToolbarProps) {
  const config = useConfig();
  const storyIntegrityEnabled = config.feature_flags?.story_integrity ?? true;
  const showRetry = saveStatus === 'error' && onRetry;
  const [exportOpen, setExportOpen] = useState(false);
  const [moreOpen, setMoreOpen] = useState(false);
  const sprintStartWordsRef = useRef(0);
  const onSprintStart = useCallback(() => {
    sprintStartWordsRef.current = totalWordCount;
  }, [totalWordCount]);
  const getSprintWordsWritten = useCallback(
    () => Math.max(0, totalWordCount - sprintStartWordsRef.current),
    [totalWordCount]
  );

  return (
    <header className="flex flex-col gap-2 border-b px-3 py-2 sm:flex-row sm:flex-wrap sm:items-center sm:justify-between sm:gap-x-4 sm:gap-y-2 sm:px-4">
      <div className="flex min-w-0 flex-1 shrink items-center gap-2 overflow-hidden sm:gap-3">
        <h2 className="min-w-0 truncate text-sm font-semibold sm:text-base">{chapterTitle || 'Pick a chapter'}</h2>
        {onStatusChange && (
          <select
            value={sectionStatus ?? 'draft'}
            onChange={(e) => onStatusChange(e.target.value as SectionStatus)}
            className="shrink-0 rounded border bg-background px-1.5 py-0.5 text-xs sm:px-2 sm:py-1"
          >
            <option value="draft">Draft</option>
            <option value="revising">Revising</option>
            <option value="review">Review</option>
            <option value="done">Complete</option>
          </select>
        )}
        <span className="shrink-0 text-xs text-muted-foreground sm:hidden">
          {chapterWordCount.toLocaleString()}w · {totalWordCount.toLocaleString()} total
        </span>
        <WritingStats wordCount={chapterWordCount} className="hidden shrink-0 sm:flex" />
        <span className="hidden shrink-0 text-xs text-muted-foreground sm:inline sm:text-sm">{totalWordCount.toLocaleString()} total</span>
        {saveStatus === 'saving' && (
          <span className="text-xs text-muted-foreground">Saving…</span>
        )}
        {saveStatus === 'saved' && (
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="text-xs text-green-600 dark:text-green-500 cursor-default">
                {lastSaved ? formatLastSaved(lastSaved) : 'Saved'}
              </span>
            </TooltipTrigger>
            <TooltipContent>
              All changes saved automatically.
            </TooltipContent>
          </Tooltip>
        )}
        {saveStatus === 'error' && (
          <span className="flex items-center gap-1">
            <span className="text-xs text-destructive">Failed to save</span>
            {showRetry && (
              <Button variant="ghost" size="sm" className="h-6 px-2 text-xs" onClick={onRetry}>
                Retry
              </Button>
            )}
          </span>
        )}
        {saveStatus === 'idle' && hasPending && (
          <span className="text-xs text-muted-foreground">Unsaved changes</span>
        )}
      </div>

      <div className="flex min-w-0 flex-shrink flex-wrap items-center justify-end gap-1 overflow-visible">
        <WritingSprintTimer
          bookId={bookId}
          getWordsWritten={getSprintWordsWritten}
          onStart={onSprintStart}
        />
        <DropdownMenu open={moreOpen} onOpenChange={setMoreOpen}>
          <Tooltip>
            <TooltipTrigger asChild>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="md:hidden h-8 shrink-0 px-2">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
            </TooltipTrigger>
            <TooltipContent>More tools and panels</TooltipContent>
          </Tooltip>
          <DropdownMenuContent align="end" className="max-h-[70vh] overflow-y-auto">
            <DropdownMenuItem onClick={() => { onToggleDarkMode(); setMoreOpen(false); }}>
              <Sun className="h-4 w-4 mr-2" />
              {darkMode ? 'Light mode' : 'Dark mode'}
            </DropdownMenuItem>
            {onSidebarPositionChange && (
              <DropdownMenuItem onClick={() => { onSidebarPositionChange(sidebarPosition === 'left' ? 'right' : 'left'); setMoreOpen(false); }}>
                <PanelLeft className="h-4 w-4 mr-2" />
                Sidebar: {sidebarPosition === 'left' ? 'Right' : 'Left'}
              </DropdownMenuItem>
            )}
            {onFindReplace && (
              <DropdownMenuItem onClick={() => { onFindReplace(); setMoreOpen(false); }}>
                <Search className="h-4 w-4 mr-2" />
                Find & replace
              </DropdownMenuItem>
            )}
            {onHistory && (
              <DropdownMenuItem onClick={() => { onHistory(); setMoreOpen(false); }}>
                <History className="h-4 w-4 mr-2" />
                Version history
              </DropdownMenuItem>
            )}
            {onRecoveryCenter && (
              <DropdownMenuItem onClick={() => { onRecoveryCenter(); setMoreOpen(false); }}>
                <Shield className="h-4 w-4 mr-2" />
                Recovery Center
              </DropdownMenuItem>
            )}
            {onQuickInsert && (
              <DropdownMenuItem onClick={() => { onQuickInsert(); setMoreOpen(false); }}>
                <Type className="h-4 w-4 mr-2" />
                Quick insert
              </DropdownMenuItem>
            )}
            {showAi && (
              <DropdownMenuItem onClick={() => { onTogglePanel(panelMode === 'ai' ? 'none' : 'ai'); setMoreOpen(false); }}>
                <Sparkles className="h-4 w-4 mr-2" />
                AI panel
              </DropdownMenuItem>
            )}
            <DropdownMenuItem onClick={() => { onTogglePanel(panelMode === 'notes' ? 'none' : 'notes'); setMoreOpen(false); }}>
              <PanelRight className="h-4 w-4 mr-2" />
              Notes panel
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => { onTogglePanel(panelMode === 'reference' ? 'none' : 'reference'); setMoreOpen(false); }}>
              <BookOpen className="h-4 w-4 mr-2" />
              Reference panel
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => { onTogglePanel(panelMode === 'revision' ? 'none' : 'revision'); setMoreOpen(false); }}>
              <ClipboardList className="h-4 w-4 mr-2" />
              Revision panel
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => { onTogglePanel(panelMode === 'vault' ? 'none' : 'vault'); setMoreOpen(false); }}>
              <Library className="h-4 w-4 mr-2" />
              Vault panel
            </DropdownMenuItem>
            {storyIntegrityEnabled && (
              <DropdownMenuItem onClick={() => { onTogglePanel(panelMode === 'integrity' ? 'none' : 'integrity'); setMoreOpen(false); }}>
                <Activity className="h-4 w-4 mr-2" />
                Story Health panel
              </DropdownMenuItem>
            )}
          </DropdownMenuContent>
        </DropdownMenu>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              className="h-8 shrink-0 px-2 md:h-9"
              onClick={onToggleDistractionFree}
            >
          {distractionFree ? (
            <Minimize2 className="h-4 w-4" />
          ) : (
            <Maximize2 className="h-4 w-4" />
          )}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{getTooltip('distraction_free') ?? (distractionFree ? 'Exit focus mode' : 'Hide distractions')}</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="sm" className="hidden md:flex h-8 shrink-0 px-2 md:h-9" onClick={onToggleDarkMode}>
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </TooltipTrigger>
          <TooltipContent>{getTooltip('dark_mode') ?? (darkMode ? 'Light mode' : 'Dark mode')}</TooltipContent>
        </Tooltip>
        {onSidebarPositionChange && (
          <DropdownMenu>
            <Tooltip>
              <TooltipTrigger asChild>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="hidden md:flex h-8 shrink-0 px-2 md:h-9">
                    {sidebarPosition === 'left' ? (
                      <PanelLeft className="h-4 w-4" />
                    ) : (
                      <PanelLeftClose className="h-4 w-4" />
                    )}
                  </Button>
                </DropdownMenuTrigger>
              </TooltipTrigger>
              <TooltipContent>Sidebar position (left or right for dominant hand)</TooltipContent>
            </Tooltip>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={() => onSidebarPositionChange('left')}
                className={cn(sidebarPosition === 'left' && 'bg-accent')}
              >
                <PanelLeft className="h-4 w-4 mr-2" />
                Left (right-handed)
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => onSidebarPositionChange('right')}
                className={cn(sidebarPosition === 'right' && 'bg-accent')}
              >
                <PanelLeftClose className="h-4 w-4 mr-2" />
                Right (left-handed)
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
        {onFindReplace && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" className="hidden md:flex h-8 shrink-0 px-2 md:h-9" onClick={onFindReplace}>
                <Search className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>{getTooltip('find_replace') ?? 'Find and replace'}</TooltipContent>
          </Tooltip>
        )}
        {onHistory && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" className="hidden md:flex h-8 shrink-0 px-2 md:h-9" onClick={onHistory}>
                <History className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>{getTooltip('version_history') ?? 'Version history'}</TooltipContent>
          </Tooltip>
        )}
        {onRecoveryCenter && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" className="hidden md:flex h-8 shrink-0 px-2 md:h-9" onClick={onRecoveryCenter}>
                <Shield className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Recovery Center</TooltipContent>
          </Tooltip>
        )}
        {onQuickInsert && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" className="hidden md:flex h-8 shrink-0 px-2 md:h-9" onClick={onQuickInsert}>
                <Type className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>{getTooltip('quick_insert') ?? 'Insert placeholder or scene break'}</TooltipContent>
          </Tooltip>
        )}
        {showAi && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant={panelMode === 'ai' ? 'secondary' : 'outline'}
                size="sm"
                className="hidden md:flex h-8 shrink-0 px-2 md:h-9"
                onClick={() => onTogglePanel(panelMode === 'ai' ? 'none' : 'ai')}
              >
                <Sparkles className="h-4 w-4 mr-1" />
                AI
              </Button>
            </TooltipTrigger>
            <TooltipContent>{getTooltip('ai_panel') ?? 'Brainstorm, rewrite, expand. Select text or describe.'}</TooltipContent>
          </Tooltip>
        )}
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={panelMode === 'notes' ? 'secondary' : 'outline'}
              size="sm"
              className="hidden md:flex h-8 shrink-0 px-2 md:h-9"
              onClick={() => onTogglePanel(panelMode === 'notes' ? 'none' : 'notes')}
            >
              {panelMode === 'notes' ? (
                <PanelRightClose className="h-4 w-4 mr-1" />
              ) : (
                <PanelRight className="h-4 w-4 mr-1" />
              )}
              Notes
            </Button>
          </TooltipTrigger>
          <TooltipContent>{getTooltip('notes') ?? 'Idea bank. Research, character notes.'}</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={panelMode === 'reference' ? 'secondary' : 'outline'}
              size="sm"
              className="hidden md:flex h-8 shrink-0 px-2 md:h-9"
              onClick={() => onTogglePanel(panelMode === 'reference' ? 'none' : 'reference')}
            >
              <BookOpen className="h-4 w-4 mr-1" />
              Reference
            </Button>
          </TooltipTrigger>
          <TooltipContent>{getTooltip('reference_panel') ?? 'Reference (Ctrl+D)'}</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={panelMode === 'revision' ? 'secondary' : 'outline'}
              size="sm"
              className="hidden md:flex h-8 shrink-0 px-2 md:h-9"
              onClick={() => onTogglePanel(panelMode === 'revision' ? 'none' : 'revision')}
            >
              <ClipboardList className="h-4 w-4 mr-1" />
              Revision
            </Button>
          </TooltipTrigger>
          <TooltipContent>Work through the manuscript one issue at a time</TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={panelMode === 'vault' ? 'secondary' : 'outline'}
              size="sm"
              className="hidden md:flex h-8 shrink-0 px-2 md:h-9"
              onClick={() => onTogglePanel(panelMode === 'vault' ? 'none' : 'vault')}
            >
              <Library className="h-4 w-4 mr-1" />
              Vault
            </Button>
          </TooltipTrigger>
          <TooltipContent>{getTooltip('vault_panel') ?? 'Chapter-linked characters, locations, sources & research'}</TooltipContent>
        </Tooltip>
        {storyIntegrityEnabled && (
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={panelMode === 'integrity' ? 'secondary' : 'outline'}
              size="sm"
              className="hidden md:flex h-8 shrink-0 px-2 md:h-9"
              onClick={() => onTogglePanel(panelMode === 'integrity' ? 'none' : 'integrity')}
            >
              <Activity className="h-4 w-4 mr-1" />
              Story Health
            </Button>
          </TooltipTrigger>
          <TooltipContent>{getTooltip('story_health') ?? 'Find plot gaps, weak arcs, missing payoff'}</TooltipContent>
        </Tooltip>
        )}
        <Tooltip>
          <TooltipTrigger asChild>
        <div className="relative shrink-0">
          <Button
            variant="outline"
            size="sm"
            className="h-8 shrink-0 px-2 md:h-9 md:px-3"
            onClick={() => setExportOpen((o) => !o)}
          >
            <FileDown className="h-4 w-4 mr-1" />
            Export
            <ChevronDown className="h-4 w-4 ml-1" />
          </Button>
          {exportOpen && (
            <>
              <div
                className="fixed inset-0 z-[99988]"
                onClick={() => setExportOpen(false)}
              />
              <div className="absolute right-0 top-full z-[99989] mt-1 min-w-[160px] rounded-lg border bg-popover py-1 shadow-lg">
                {['docx', 'pdf', 'epub', 'txt'].map((f) => (
                  <button
                    key={f}
                    type="button"
                    className="block w-full px-4 py-2 text-left text-sm hover:bg-muted"
                    onClick={() => {
                      onExport(f);
                      setExportOpen(false);
                    }}
                  >
                    .{f.toUpperCase()}
                  </button>
                ))}
                <div className="my-1 border-t" />
                <button
                  type="button"
                  className="block w-full px-4 py-2 text-left text-sm hover:bg-muted font-medium"
                  onClick={() => {
                    onExport('backup', true);
                    setExportOpen(false);
                  }}
                >
                  Backup (.txt)
                </button>
              </div>
            </>
          )}
        </div>
          </TooltipTrigger>
          <TooltipContent>{getTooltip('export') ?? 'Export manuscript'}</TooltipContent>
        </Tooltip>
      </div>
    </header>
  );
}
