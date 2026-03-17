'use client';

import { useCallback, useEffect, useState } from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  RefreshCw,
  Scissors,
  Target,
  Wind,
  Repeat,
  Zap,
  Layers,
} from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';
import {
  DENSITY_HEADING,
  DENSITY_TABS,
  DENSITY_ISSUE_LABELS,
  DENSITY_EXPLANATIONS,
  DENSITY_ACTION_LABELS,
  DENSITY_ACTIONS,
  DENSITY_ISSUES,
  DENSITY_CHAPTER_SUMMARY,
  DENSITY_TOAST,
  getDensitySummaryLabel,
  DENSITY_SEVERITY_LABELS,
} from '@/content/density-copy';
import { ScenePurposeBoard } from './ScenePurposeBoard';
import { ChapterDragPanel } from './ChapterDragPanel';
import { RepetitionHeatPanel } from './RepetitionHeatPanel';

interface DensityHealthSummary {
  total_issues: number;
  by_severity: Record<string, number>;
  by_category: Record<string, number>;
  by_action: Record<string, number>;
  open_count: number;
  manuscript_density_score: number | null;
  last_scan_at: string | null;
  last_scan_issue_count: number | null;
}

interface DensityIssue {
  id: string;
  issue_type: string;
  category: string;
  action_category: string;
  severity: string;
  title: string;
  description: string | null;
  chapter_id: string | null;
  status: string;
  fix_suggestions: Array<{ action?: string; label?: string }> | null;
}

interface StoryDensityPanelProps {
  projectId: string;
  bookId: string;
  activeChapterId: string | null;
  onSelectChapter?: (chapterId: string) => void;
}

const ACTION_LABELS: Record<string, { label: string; icon: React.ReactNode }> = {
  trim: { label: DENSITY_ACTION_LABELS.trim, icon: <Scissors className="h-3.5 w-3.5" /> },
  compress: { label: DENSITY_ACTION_LABELS.compress, icon: <Layers className="h-3.5 w-3.5" /> },
  strengthen: { label: DENSITY_ACTION_LABELS.strengthen, icon: <Zap className="h-3.5 w-3.5" /> },
  expand: { label: DENSITY_ACTION_LABELS.expand, icon: <Zap className="h-3.5 w-3.5" /> },
  bridge: { label: DENSITY_ACTION_LABELS.bridge, icon: <Layers className="h-3.5 w-3.5" /> },
  clarify: { label: DENSITY_ACTION_LABELS.clarify, icon: <Zap className="h-3.5 w-3.5" /> },
  merge: { label: DENSITY_ACTION_LABELS.merge, icon: <Layers className="h-3.5 w-3.5" /> },
  keep_as_intentional: { label: DENSITY_ACTION_LABELS.keep_as_intentional, icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
};

export function StoryDensityPanel({
  projectId,
  bookId,
  activeChapterId,
  onSelectChapter,
}: StoryDensityPanelProps) {
  const { toast } = useToast();
  const [health, setHealth] = useState<DensityHealthSummary | null>(null);
  const [issues, setIssues] = useState<DensityIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const fetchHealth = useCallback(async () => {
    try {
      const h = await api<DensityHealthSummary>(
        `/api/v1/projects/${projectId}/books/${bookId}/density/health`
      );
      setHealth(h);
    } catch {
      setHealth(null);
    }
  }, [projectId, bookId]);

  const fetchIssues = useCallback(async () => {
    try {
      const list = await api<DensityIssue[]>(
        `/api/v1/projects/${projectId}/books/${bookId}/density/issues?status=open&limit=50`
      );
      setIssues(list);
    } catch {
      setIssues([]);
    }
  }, [projectId, bookId]);

  const fetchChapterSummary = useCallback(async () => {
    if (!activeChapterId) {
      setChapterSummary(null);
      return;
    }
    try {
      const s = await api<{
        what_this_chapter_is_doing: string | null;
        where_this_chapter_is_dragging: { is_dragging: boolean; suggestion?: string } | null;
        which_parts_feel_repetitive: { heat_level: string; repetition_heat: number } | null;
      }>(
        `/api/v1/projects/${projectId}/books/${bookId}/density/chapters/${activeChapterId}/summary`
      );
      setChapterSummary(s);
    } catch {
      setChapterSummary(null);
    }
  }, [projectId, bookId, activeChapterId]);

  const load = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchHealth(), fetchIssues()]);
    setLoading(false);
    if (activeChapterId) {
      fetchChapterSummary();
    }
  }, [fetchHealth, fetchIssues, activeChapterId, fetchChapterSummary]);

  useEffect(() => {
    load();
  }, [load]);

  const handleScan = useCallback(async () => {
    setScanning(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/density/scan`, {
        method: 'POST',
        body: JSON.stringify({ scan_type: 'full_project', triggered_by: 'manual' }),
      });
      toast({ title: DENSITY_TOAST.scanComplete, description: DENSITY_TOAST.scanCompleteDesc });
      await load();
    } catch {
      toast({ title: DENSITY_TOAST.scanFailed, variant: 'destructive' });
    } finally {
      setScanning(false);
    }
  }, [projectId, bookId, load, toast]);

  const handleResolve = useCallback(
    async (issueId: string) => {
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/density/issues/${issueId}`, {
          method: 'PATCH',
          body: JSON.stringify({ status: 'resolved' }),
        });
        await fetchIssues();
        await fetchHealth();
      } catch {
        toast({ title: DENSITY_TOAST.updateFailed, variant: 'destructive' });
      }
    },
    [projectId, bookId, fetchIssues, fetchHealth, toast]
  );

  const handleMarkIntentional = useCallback(
    async (issueId: string) => {
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/density/issues/${issueId}`, {
          method: 'PATCH',
          body: JSON.stringify({ status: 'intentional' }),
        });
        await fetchIssues();
        await fetchHealth();
      } catch {
        toast({ title: DENSITY_TOAST.updateFailed, variant: 'destructive' });
      }
    },
    [projectId, bookId, fetchIssues, fetchHealth, toast]
  );

  const severityColor = (s: string) => {
    switch (s) {
      case 'critical':
        return 'text-red-600 dark:text-red-400';
      case 'high':
        return 'text-orange-600 dark:text-orange-400';
      case 'moderate':
        return 'text-amber-600 dark:text-amber-400';
      default:
        return 'text-muted-foreground';
    }
  };

  const actionLabel = (a: string) => ACTION_LABELS[a]?.label ?? a;

  const [chapterSummary, setChapterSummary] = useState<{
    what_this_chapter_is_doing: string | null;
    where_this_chapter_is_dragging: { is_dragging: boolean; suggestion?: string } | null;
    which_parts_feel_repetitive: { heat_level: string; repetition_heat: number } | null;
  } | null>(null);

  useEffect(() => {
    if (activeChapterId) {
      fetchChapterSummary();
    } else {
      setChapterSummary(null);
    }
  }, [activeChapterId, fetchChapterSummary]);

  if (loading && !health) {
    return (
      <div className="flex h-full w-full flex-col border-l bg-background p-4">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          {DENSITY_ISSUES.loading}
        </div>
      </div>
    );
  }

  const getIssueDisplayLabel = (issue: DensityIssue) =>
    DENSITY_ISSUE_LABELS[issue.issue_type] ??
    DENSITY_ISSUE_LABELS[issue.category] ??
    issue.title;
  const getIssueDescription = (issue: DensityIssue) =>
    issue.description ??
    DENSITY_EXPLANATIONS[issue.issue_type] ??
    DENSITY_EXPLANATIONS[issue.category];
  const getSeverityLabel = (s: string) =>
    DENSITY_SEVERITY_LABELS[s] ?? s;

  return (
    <div className="flex h-full w-full max-w-md flex-col border-l bg-background">
      <div className="flex flex-col gap-1 border-b px-4 py-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold flex items-center gap-2">
            <Activity className="h-4 w-4" />
            {DENSITY_HEADING.title}
          </h3>
          <Button
            variant="outline"
            size="sm"
            onClick={handleScan}
            disabled={scanning}
          >
            {scanning ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            <span className="ml-1">{scanning ? DENSITY_ACTIONS.scanning : DENSITY_ACTIONS.scan}</span>
          </Button>
        </div>
        <p className="text-xs text-muted-foreground">{DENSITY_HEADING.subheading}</p>
      </div>

      {activeChapterId && chapterSummary && (
        <div className="border-b px-4 py-3 bg-muted/30 space-y-2">
          <h4 className="text-xs font-medium text-muted-foreground">{DENSITY_CHAPTER_SUMMARY.heading}</h4>
          {chapterSummary.what_this_chapter_is_doing && (
            <p className="text-sm">
              <span className="font-medium">{DENSITY_CHAPTER_SUMMARY.whatDoing}: </span>
              {chapterSummary.what_this_chapter_is_doing}
            </p>
          )}
          {chapterSummary.where_this_chapter_is_dragging?.is_dragging && (
            <p className="text-sm text-amber-700 dark:text-amber-400">
              <Wind className="h-3.5 w-3.5 inline mr-1" />
              {chapterSummary.where_this_chapter_is_dragging.suggestion || 'This chapter may be doing less than its size suggests.'}
            </p>
          )}
          {chapterSummary.which_parts_feel_repetitive && chapterSummary.which_parts_feel_repetitive.heat_level !== 'low' && (
            <p className="text-sm text-amber-700 dark:text-amber-400">
              <Repeat className="h-3.5 w-3.5 inline mr-1" />
              {DENSITY_CHAPTER_SUMMARY.repetition}: {chapterSummary.which_parts_feel_repetitive.heat_level} ({Math.round((chapterSummary.which_parts_feel_repetitive.repetition_heat || 0) * 100)}%)
            </p>
          )}
        </div>
      )}

      <Tabs.Root defaultValue="issues" className="flex flex-1 flex-col min-h-0">
        <Tabs.List className="flex shrink-0 border-b px-2">
          <Tabs.Trigger
            value="issues"
            className="flex items-center gap-1.5 px-3 py-2 text-xs data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:font-medium"
          >
            <AlertTriangle className="h-3.5 w-3.5" />
            {DENSITY_TABS.issues}
          </Tabs.Trigger>
          <Tabs.Trigger
            value="purpose"
            className="flex items-center gap-1.5 px-3 py-2 text-xs data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:font-medium"
          >
            <Target className="h-3.5 w-3.5" />
            {DENSITY_TABS.purpose}
          </Tabs.Trigger>
          <Tabs.Trigger
            value="drag"
            className="flex items-center gap-1.5 px-3 py-2 text-xs data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:font-medium"
          >
            <Wind className="h-3.5 w-3.5" />
            {DENSITY_TABS.drag}
          </Tabs.Trigger>
          <Tabs.Trigger
            value="repetition"
            className="flex items-center gap-1.5 px-3 py-2 text-xs data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:font-medium"
          >
            <Repeat className="h-3.5 w-3.5" />
            {DENSITY_TABS.repetition}
          </Tabs.Trigger>
        </Tabs.List>
        <Tabs.Content value="issues" className="flex-1 overflow-auto min-h-0">
        <div className="p-4 space-y-4">
          {health && (
            <div className="rounded-lg border p-4 space-y-2">
              <div className="flex items-center gap-2">
                {health.open_count === 0 ? (
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-amber-800 dark:text-amber-200" />
                )}
                <span className="font-medium">
                  {getDensitySummaryLabel(health.open_count, health.manuscript_density_score)}
                  {health.open_count > 0 && (
                    <span className="font-normal text-muted-foreground ml-1">
                      ({DENSITY_ISSUES.issuesToReview(health.open_count)})
                    </span>
                  )}
                </span>
              </div>
              {health.manuscript_density_score != null && (
                <div>
                  <div className="flex justify-between text-xs text-muted-foreground mb-1">
                    <span>{DENSITY_ISSUES.densityScore}</span>
                    <span>{Math.round(health.manuscript_density_score)}</span>
                  </div>
                  <Progress
                    value={health.manuscript_density_score}
                    max={100}
                    className="h-2"
                  />
                </div>
              )}
              {health.last_scan_at && (
                <p className="text-xs text-muted-foreground">
                  {DENSITY_ACTIONS.lastScan}: {new Date(health.last_scan_at).toLocaleString()}
                </p>
              )}
              {(Object.keys(health.by_action).length > 0 || Object.keys(health.by_severity).length > 0) && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {Object.entries(health.by_action).map(([act, count]) => (
                    <span
                      key={act}
                      className="rounded px-2 py-0.5 text-xs font-medium bg-muted"
                    >
                      {actionLabel(act)}: {count}
                    </span>
                  ))}
                  {Object.entries(health.by_severity).map(([sev, count]) => (
                    <span
                      key={sev}
                      className={cn(
                        'rounded px-2 py-0.5 text-xs font-medium',
                        severityColor(sev)
                      )}
                    >
                      {sev}: {count}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          <div>
            <h4 className="text-sm font-medium mb-2">{DENSITY_ISSUES.heading}</h4>
            <p className="text-xs text-muted-foreground mb-2">
              {DENSITY_ISSUES.subheading}
            </p>
            {issues.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                {DENSITY_ISSUES.empty}
              </p>
            ) : (
              <ul className="space-y-2">
                {issues.map((issue) => (
                  <li
                    key={issue.id}
                    className={cn(
                      'rounded-lg border p-3',
                      activeChapterId && issue.chapter_id === activeChapterId && 'ring-2 ring-primary'
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={cn('text-xs font-medium', severityColor(issue.severity))}>
                            {getSeverityLabel(issue.severity)}
                          </span>
                          <span className="text-xs font-medium text-muted-foreground">
                            {actionLabel(issue.action_category)}
                          </span>
                        </div>
                        <p className="text-sm font-medium mt-0.5">{getIssueDisplayLabel(issue)}</p>
                        {getIssueDescription(issue) && (
                          <p className="text-xs text-muted-foreground mt-1">{getIssueDescription(issue)}</p>
                        )}
                        {issue.chapter_id && onSelectChapter && (
                          <button
                            type="button"
                            className="text-xs text-primary hover:underline mt-1"
                            onClick={() => onSelectChapter(issue.chapter_id!)}
                          >
                            {DENSITY_ACTIONS.goToChapter}
                          </button>
                        )}
                      </div>
                      <div className="flex flex-col gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => handleResolve(issue.id)}
                        >
                          {DENSITY_ACTIONS.resolveLater}
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 text-xs"
                          onClick={() => handleMarkIntentional(issue.id)}
                        >
                          {DENSITY_ACTIONS.markAsIntentional}
                        </Button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
        </Tabs.Content>
        <Tabs.Content value="purpose" className="flex-1 overflow-auto min-h-0">
          <ScenePurposeBoard
            projectId={projectId}
            bookId={bookId}
            activeChapterId={activeChapterId}
            onSelectChapter={onSelectChapter}
          />
        </Tabs.Content>
        <Tabs.Content value="drag" className="flex-1 overflow-auto min-h-0">
          <ChapterDragPanel
            projectId={projectId}
            bookId={bookId}
            activeChapterId={activeChapterId}
            onSelectChapter={onSelectChapter}
          />
        </Tabs.Content>
        <Tabs.Content value="repetition" className="flex-1 overflow-auto min-h-0">
          <RepetitionHeatPanel
            projectId={projectId}
            bookId={bookId}
            activeChapterId={activeChapterId}
            onSelectChapter={onSelectChapter}
          />
        </Tabs.Content>
      </Tabs.Root>
    </div>
  );
}
