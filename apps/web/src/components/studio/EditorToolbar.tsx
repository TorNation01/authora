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
  BookOpen,
  Shield,
  ClipboardList,
  Library,
  Activity,
} from 'lucide-react';
import type { SectionStatus } from './ManuscriptSidebar';
import { useConfig } from '@/contexts/ConfigProvider';
import { Button } from '@/components/ui/button';
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
}: EditorToolbarProps) {
  const config = useConfig();
  const storyIntegrityEnabled = config.feature_flags?.story_integrity ?? true;
  const showRetry = saveStatus === 'error' && onRetry;
  const [exportOpen, setExportOpen] = useState(false);
  const sprintStartWordsRef = useRef(0);
  const onSprintStart = useCallback(() => {
    sprintStartWordsRef.current = totalWordCount;
  }, [totalWordCount]);
  const getSprintWordsWritten = useCallback(
    () => Math.max(0, totalWordCount - sprintStartWordsRef.current),
    [totalWordCount]
  );

  return (
    <header className="flex items-center justify-between gap-4 border-b px-4 py-2">
      <div className="flex min-w-0 items-center gap-3">
        <h2 className="truncate font-semibold">{chapterTitle || 'Pick a chapter'}</h2>
        {onStatusChange && (
          <select
            value={sectionStatus ?? 'draft'}
            onChange={(e) => onStatusChange(e.target.value as SectionStatus)}
            className="rounded border bg-background px-2 py-1 text-xs"
          >
            <option value="draft">Draft</option>
            <option value="revising">Revising</option>
            <option value="review">Review</option>
            <option value="done">Complete</option>
          </select>
        )}
        <WritingStats wordCount={chapterWordCount} />
        <span className="text-sm text-muted-foreground">{totalWordCount.toLocaleString()} total</span>
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

      <div className="flex items-center gap-1">
        <WritingSprintTimer
          bookId={bookId}
          getWordsWritten={getSprintWordsWritten}
          onStart={onSprintStart}
        />
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
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
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleDarkMode}
          title={darkMode ? 'Light mode' : 'Dark mode'}
        >
          {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
        {onFindReplace && (
          <Button variant="ghost" size="sm" onClick={onFindReplace} title="Find & replace">
            <Search className="h-4 w-4" />
          </Button>
        )}
        {onHistory && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" onClick={onHistory}>
                <History className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>{getTooltip('version_history') ?? 'Version history'}</TooltipContent>
          </Tooltip>
        )}
        {onRecoveryCenter && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="sm" onClick={onRecoveryCenter}>
                <Shield className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Recovery Center</TooltipContent>
          </Tooltip>
        )}
        {onQuickInsert && (
          <Button variant="ghost" size="sm" onClick={onQuickInsert} title="Quick insert">
            <Type className="h-4 w-4" />
          </Button>
        )}
        {showAi && (
          <Button
            variant={panelMode === 'ai' ? 'secondary' : 'outline'}
            size="sm"
            onClick={() => onTogglePanel(panelMode === 'ai' ? 'none' : 'ai')}
          >
            <Sparkles className="h-4 w-4 mr-1" />
            AI
          </Button>
        )}
        <Button
          variant={panelMode === 'notes' ? 'secondary' : 'outline'}
          size="sm"
          onClick={() => onTogglePanel(panelMode === 'notes' ? 'none' : 'notes')}
        >
          {panelMode === 'notes' ? (
            <PanelRightClose className="h-4 w-4 mr-1" />
          ) : (
            <PanelRight className="h-4 w-4 mr-1" />
          )}
          Notes
        </Button>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant={panelMode === 'reference' ? 'secondary' : 'outline'}
              size="sm"
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
              onClick={() => onTogglePanel(panelMode === 'integrity' ? 'none' : 'integrity')}
            >
              <Activity className="h-4 w-4 mr-1" />
              Story Health
            </Button>
          </TooltipTrigger>
          <TooltipContent>Manuscript integrity and issues</TooltipContent>
        </Tooltip>
        )}
        <Tooltip>
          <TooltipTrigger asChild>
        <div className="relative">
          <Button
            variant="outline"
            size="sm"
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
