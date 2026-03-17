'use client';

import { useCallback, useEffect, useState } from 'react';
import * as Tabs from '@radix-ui/react-tabs';
import { Activity, AlertTriangle, BookOpen, CheckCircle2, Loader2, RefreshCw } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { ChapterHealthPanel } from './ChapterHealthPanel';

interface StoryHealthSummary {
  total_issues: number;
  by_severity: Record<string, number>;
  by_category: Record<string, number>;
  open_count: number;
  last_scan_at: string | null;
  last_scan_issue_count: number | null;
}

interface IntegrityIssue {
  id: string;
  issue_type: string;
  category: string;
  severity: string;
  title: string;
  description: string | null;
  chapter_id: string | null;
  status: string;
  fix_suggestions: Array<{ action?: string; label?: string }> | null;
}

interface StoryIntegrityPanelProps {
  projectId: string;
  bookId: string;
  activeChapterId: string | null;
  onSelectChapter?: (chapterId: string) => void;
}

export function StoryIntegrityPanel({
  projectId,
  bookId,
  activeChapterId,
  onSelectChapter,
}: StoryIntegrityPanelProps) {
  const { toast } = useToast();
  const [health, setHealth] = useState<StoryHealthSummary | null>(null);
  const [issues, setIssues] = useState<IntegrityIssue[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);

  const fetchHealth = useCallback(async () => {
    try {
      const h = await api<StoryHealthSummary>(
        `/api/v1/projects/${projectId}/books/${bookId}/integrity/health`
      );
      setHealth(h);
    } catch {
      setHealth(null);
    }
  }, [projectId, bookId]);

  const fetchIssues = useCallback(async () => {
    try {
      const list = await api<IntegrityIssue[]>(
        `/api/v1/projects/${projectId}/books/${bookId}/integrity/issues?status=open&limit=50`
      );
      setIssues(list);
    } catch {
      setIssues([]);
    }
  }, [projectId, bookId]);

  const load = useCallback(async () => {
    setLoading(true);
    await Promise.all([fetchHealth(), fetchIssues()]);
    setLoading(false);
  }, [fetchHealth, fetchIssues]);

  useEffect(() => {
    load();
  }, [load]);

  const handleScan = useCallback(async () => {
    setScanning(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/integrity/scan`, {
        method: 'POST',
        body: JSON.stringify({ scan_type: 'full_project', triggered_by: 'manual' }),
      });
      toast({ title: 'Scan complete', description: 'Story integrity updated.' });
      await load();
    } catch {
      toast({ title: 'Scan failed', variant: 'destructive' });
    } finally {
      setScanning(false);
    }
  }, [projectId, bookId, load, toast]);

  const handleResolve = useCallback(
    async (issueId: string) => {
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/integrity/issues/${issueId}`, {
          method: 'PATCH',
          body: JSON.stringify({ status: 'resolved' }),
        });
        await fetchIssues();
        await fetchHealth();
      } catch {
        toast({ title: 'Failed to update', variant: 'destructive' });
      }
    },
    [projectId, bookId, fetchIssues, fetchHealth, toast]
  );

  const handleMarkIntentional = useCallback(
    async (issueId: string) => {
      try {
        await api(`/api/v1/projects/${projectId}/books/${bookId}/integrity/issues/${issueId}`, {
          method: 'PATCH',
          body: JSON.stringify({ status: 'intentional' }),
        });
        await fetchIssues();
        await fetchHealth();
      } catch {
        toast({ title: 'Failed to update', variant: 'destructive' });
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

  if (loading && !health) {
    return (
      <div className="flex h-full w-full max-w-md flex-col border-l bg-background p-4">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading story health…
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full max-w-md flex-col border-l bg-background">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <h3 className="font-semibold flex items-center gap-2">
          <Activity className="h-4 w-4" />
          Story Health
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
          <span className="ml-1">{scanning ? 'Scanning…' : 'Scan'}</span>
        </Button>
      </div>

      <Tabs.Root defaultValue="issues" className="flex flex-1 flex-col min-h-0">
        <Tabs.List className="flex shrink-0 border-b px-4">
          <Tabs.Trigger
            value="issues"
            className="flex items-center gap-2 px-4 py-2.5 text-sm data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:font-medium"
          >
            <AlertTriangle className="h-4 w-4" />
            Issues
          </Tabs.Trigger>
          <Tabs.Trigger
            value="chapters"
            className="flex items-center gap-2 px-4 py-2.5 text-sm data-[state=active]:border-b-2 data-[state=active]:border-primary data-[state=active]:font-medium"
          >
            <BookOpen className="h-4 w-4" />
            Chapter Health
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
                {health.open_count === 0
                  ? 'No open issues'
                  : `${health.open_count} open issue${health.open_count === 1 ? '' : 's'}`}
              </span>
            </div>
            {health.last_scan_at && (
              <p className="text-xs text-muted-foreground">
                Last scan: {new Date(health.last_scan_at).toLocaleString()}
              </p>
            )}
            {Object.keys(health.by_severity).length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
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
          <h4 className="text-sm font-medium mb-2">Open issues</h4>
          {issues.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Run a scan to detect issues. No open issues right now.
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
                      <span className={cn('text-xs font-medium', severityColor(issue.severity))}>
                        {issue.severity}
                      </span>
                      <p className="text-sm font-medium mt-0.5">{issue.title}</p>
                      {issue.description && (
                        <p className="text-xs text-muted-foreground mt-1">{issue.description}</p>
                      )}
                      {issue.chapter_id && onSelectChapter && (
                        <button
                          type="button"
                          className="text-xs text-primary hover:underline mt-1"
                          onClick={() => onSelectChapter(issue.chapter_id!)}
                        >
                          Go to chapter
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
                        Resolve
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-7 text-xs"
                        onClick={() => handleMarkIntentional(issue.id)}
                      >
                        Intentional
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
        <Tabs.Content value="chapters" className="flex-1 overflow-auto min-h-0">
          <ChapterHealthPanel
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
