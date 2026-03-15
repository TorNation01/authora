'use client';

import { useState } from 'react';
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
} from 'lucide-react';
import type { SectionStatus } from './ManuscriptSidebar';
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

type PanelMode = 'none' | 'ai' | 'notes' | 'reference';

interface EditorToolbarProps {
  chapterTitle: string;
  chapterWordCount: number;
  totalWordCount: number;
  saveStatus: 'idle' | 'saving' | 'saved' | 'error';
  distractionFree: boolean;
  darkMode: boolean;
  panelMode: PanelMode;
  onToggleDistractionFree: () => void;
  onToggleDarkMode: () => void;
  onTogglePanel: (mode: PanelMode) => void;
  onExport: (format: string) => void;
  onHistory?: () => void;
  onFindReplace?: () => void;
  onQuickInsert?: () => void;
  onStatusChange?: (status: SectionStatus) => void;
  sectionStatus?: string | null;
  showAi?: boolean;
}

export function EditorToolbar({
  chapterTitle,
  chapterWordCount,
  totalWordCount,
  saveStatus,
  distractionFree,
  darkMode,
  panelMode,
  onToggleDistractionFree,
  onToggleDarkMode,
  onTogglePanel,
  onExport,
  onHistory,
  onFindReplace,
  onQuickInsert,
  onStatusChange,
  sectionStatus,
  showAi = true,
}: EditorToolbarProps) {
  const [exportOpen, setExportOpen] = useState(false);

  return (
    <header className="flex items-center justify-between gap-4 border-b px-4 py-2">
      <div className="flex min-w-0 items-center gap-3">
        <h2 className="truncate font-semibold">{chapterTitle || 'Select a chapter'}</h2>
        {onStatusChange && (
          <select
            value={sectionStatus ?? 'draft'}
            onChange={(e) => onStatusChange(e.target.value as SectionStatus)}
            className="rounded border bg-background px-2 py-1 text-xs"
          >
            <option value="draft">Draft</option>
            <option value="revising">Revising</option>
            <option value="review">Review</option>
            <option value="done">Done</option>
          </select>
        )}
        <WritingStats wordCount={chapterWordCount} />
        <span className="text-sm text-muted-foreground">{totalWordCount.toLocaleString()} total</span>
        {saveStatus === 'saving' && (
          <span className="text-xs text-muted-foreground">Saving...</span>
        )}
        {saveStatus === 'saved' && (
          <span className="text-xs text-green-600 dark:text-green-500">Saved</span>
        )}
        {saveStatus === 'error' && (
          <span className="text-xs text-destructive">Failed to save</span>
        )}
      </div>

      <div className="flex items-center gap-1">
        <WritingSprintTimer />
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
          <TooltipContent>{getTooltip('distraction_free') ?? (distractionFree ? 'Exit focus mode' : 'Focus mode')}</TooltipContent>
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
                className="fixed inset-0 z-10"
                onClick={() => setExportOpen(false)}
              />
              <div className="absolute right-0 top-full z-20 mt-1 min-w-[120px] rounded-lg border bg-popover py-1 shadow-lg">
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
