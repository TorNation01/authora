'use client';

import { useCallback, useEffect, useState } from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  HelpCircle,
  Loader2,
  BookOpen,
  BarChart3,
} from 'lucide-react';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';
import { Progress } from '@/components/ui/progress';

export interface ChapterHealth {
  chapter_id: string;
  chapter_index: number;
  title: string;
  word_count: number;
  health: 'strong' | 'stable' | 'needs_support' | 'weak' | 'critical';
  health_reason: string;
  purpose_clarity: number;
  relationship_to_manuscript: number;
  tension_level: number;
  emotional_movement: number;
  plot_movement: number;
  information_density: number;
  pacing: number;
  transition_quality: number;
  opening_strength: number;
  closing_strength: number;
  chapter_linkage: number;
  repetition: number;
  unresolved_internal: number;
  what_this_chapter_is_doing: string;
  why_feels_off: string | null;
  suggested_fixes: Array<{ action: string; label: string }>;
  issues: Array<{
    type: string;
    severity: string;
    title: string;
    suggestion: string;
  }>;
}

interface ChapterHealthListResponse {
  chapters: ChapterHealth[];
  scan_id: string | null;
  last_scan_at: string | null;
}

interface ChapterHealthPanelProps {
  projectId: string;
  bookId: string;
  activeChapterId: string | null;
  onSelectChapter?: (chapterId: string) => void;
}

function healthColor(health: string): string {
  switch (health) {
    case 'strong':
      return 'text-emerald-600 dark:text-emerald-400';
    case 'stable':
      return 'text-green-600 dark:text-green-400';
    case 'needs_support':
      return 'text-amber-600 dark:text-amber-400';
    case 'weak':
      return 'text-orange-600 dark:text-orange-400';
    case 'critical':
      return 'text-red-600 dark:text-red-400';
    default:
      return 'text-muted-foreground';
  }
}

function healthIcon(health: string) {
  switch (health) {
    case 'strong':
    case 'stable':
      return <CheckCircle2 className="h-4 w-4" />;
    case 'needs_support':
    case 'weak':
      return <HelpCircle className="h-4 w-4" />;
    case 'critical':
      return <AlertTriangle className="h-4 w-4" />;
    default:
      return <HelpCircle className="h-4 w-4" />;
  }
}

function healthLabel(health: string): string {
  switch (health) {
    case 'strong':
      return 'Strong';
    case 'stable':
      return 'Stable';
    case 'needs_support':
      return 'Needs support';
    case 'weak':
      return 'Weak';
    case 'critical':
      return 'Critical';
    default:
      return health;
  }
}

export function ChapterHealthPanel({
  projectId,
  bookId,
  activeChapterId,
  onSelectChapter,
}: ChapterHealthPanelProps) {
  const [data, setData] = useState<ChapterHealthListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const [view, setView] = useState<'list' | 'compare'>('list');

  const fetchChapterHealth = useCallback(async () => {
    try {
      const res = await api<ChapterHealthListResponse>(
        `/api/v1/projects/${projectId}/books/${bookId}/integrity/chapter-health`
      );
      setData(res);
    } catch {
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [projectId, bookId]);

  useEffect(() => {
    fetchChapterHealth();
  }, [fetchChapterHealth]);

  const toggleChapter = (index: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(index)) next.delete(index);
      else next.add(index);
      return next;
    });
  };

  const scoreLabels: Record<string, string> = {
    purpose_clarity: 'Purpose clarity',
    relationship_to_manuscript: 'Relationship to manuscript',
    tension_level: 'Tension',
    emotional_movement: 'Emotional movement',
    plot_movement: 'Plot movement',
    information_density: 'Information density',
    pacing: 'Pacing',
    transition_quality: 'Transition quality',
    opening_strength: 'Opening strength',
    closing_strength: 'Closing strength',
    chapter_linkage: 'Chapter linkage',
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data || data.chapters.length === 0) {
    return (
      <div className="flex flex-col gap-4 p-4">
        <p className="text-sm text-muted-foreground">
          Run a scan to see chapter health and pacing analysis. No chapter data yet.
        </p>
      </div>
    );
  }

  if (view === 'compare') {
    return (
      <div className="flex flex-col gap-4 p-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-medium">Chapter comparison</h4>
          <button
            type="button"
            onClick={() => setView('list')}
            className="text-xs text-primary hover:underline"
          >
            Back to list
          </button>
        </div>
        <div className="space-y-2 overflow-auto">
          {data.chapters.map((ch, i) => (
            <div
              key={ch.chapter_id}
              className={cn(
                'rounded-lg border p-3',
                activeChapterId === ch.chapter_id && 'ring-2 ring-primary'
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <span className="text-xs text-muted-foreground">Ch. {i + 1}</span>
                  <p className="truncate font-medium">{ch.title}</p>
                  <p className="text-xs text-muted-foreground">{ch.word_count} words</p>
                </div>
                <div className={cn('flex items-center gap-1 text-xs font-medium', healthColor(ch.health))}>
                  {healthIcon(ch.health)}
                  {healthLabel(ch.health)}
                </div>
              </div>
              <div className="mt-2 grid grid-cols-2 gap-1 text-xs">
                <div>
                  <span className="text-muted-foreground">Pacing:</span>{' '}
                  <span className={ch.pacing >= 0.7 ? 'text-emerald-600' : ch.pacing >= 0.5 ? 'text-amber-600' : 'text-red-600'}>
                    {Math.round(ch.pacing * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Tension:</span>{' '}
                  <span className={ch.tension_level >= 0.5 ? 'text-emerald-600' : 'text-muted-foreground'}>
                    {Math.round(ch.tension_level * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Emotion:</span>{' '}
                  <span className={ch.emotional_movement >= 0.5 ? 'text-emerald-600' : 'text-muted-foreground'}>
                    {Math.round(ch.emotional_movement * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Opening:</span>{' '}
                  <span className={ch.opening_strength >= 0.6 ? 'text-emerald-600' : 'text-amber-600'}>
                    {Math.round(ch.opening_strength * 100)}%
                  </span>
                </div>
              </div>
              {onSelectChapter && (
                <button
                  type="button"
                  onClick={() => onSelectChapter(ch.chapter_id)}
                  className="mt-2 text-xs text-primary hover:underline"
                >
                  Go to chapter
                </button>
              )}
            </div>
          ))}
        </div>
        <div className="rounded-lg border border-dashed p-4 text-center text-xs text-muted-foreground">
          Pacing heatmap (coming soon)
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium">Chapter health</h4>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setView('compare')}
            className="flex items-center gap-1 text-xs text-primary hover:underline"
          >
            <BarChart3 className="h-3.5 w-3.5" />
            Compare
          </button>
        </div>
      </div>
      {data.last_scan_at && (
        <p className="text-xs text-muted-foreground">
          From scan: {new Date(data.last_scan_at).toLocaleString()}
        </p>
      )}
      <div className="space-y-2 overflow-auto">
        {data.chapters.map((ch, i) => {
          const isExpanded = expanded.has(i);
          return (
            <div
              key={ch.chapter_id}
              className={cn(
                'rounded-lg border overflow-hidden',
                activeChapterId === ch.chapter_id && 'ring-2 ring-primary'
              )}
            >
              <button
                type="button"
                className="flex w-full items-center gap-2 p-3 text-left hover:bg-muted/50"
                onClick={() => toggleChapter(i)}
              >
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
                ) : (
                  <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
                )}
                <div className={cn('flex items-center gap-1.5 shrink-0', healthColor(ch.health))}>
                  {healthIcon(ch.health)}
                  <span className="text-xs font-medium">{healthLabel(ch.health)}</span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{ch.title || `Chapter ${i + 1}`}</p>
                  <p className="text-xs text-muted-foreground">{ch.word_count} words</p>
                </div>
              </button>
              {isExpanded && (
                <div className="border-t bg-muted/30 px-3 py-3 space-y-3">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground">What this chapter is doing</p>
                    <p className="text-sm mt-0.5">{ch.what_this_chapter_is_doing}</p>
                  </div>
                  {ch.why_feels_off && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">Why this chapter feels off</p>
                      <p className="text-sm mt-0.5 text-amber-700 dark:text-amber-400">{ch.why_feels_off}</p>
                    </div>
                  )}
                  {ch.suggested_fixes.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">Suggested fixes</p>
                      <ul className="mt-1 space-y-1">
                        {ch.suggested_fixes.map((f, j) => (
                          <li key={j} className="text-sm flex items-start gap-2">
                            <span className="text-primary">•</span>
                            <span>{f.label}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {ch.issues.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-muted-foreground">Issues</p>
                      <ul className="mt-1 space-y-1">
                        {ch.issues.map((iss, j) => (
                          <li key={j} className="text-sm">
                            <span className="font-medium">{iss.title}</span>
                            {iss.suggestion && (
                              <span className="text-muted-foreground"> — {iss.suggestion}</span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="space-y-2">
                    <p className="text-xs font-medium text-muted-foreground">Scores</p>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(scoreLabels).map(([key, label]) => {
                        const val = (ch as unknown as Record<string, number>)[key];
                        if (typeof val !== 'number') return null;
                        return (
                          <div key={key}>
                            <div className="flex justify-between text-xs text-muted-foreground">
                              <span>{label}</span>
                              <span>{Math.round(val * 100)}%</span>
                            </div>
                            <Progress value={val * 100} max={100} size="sm" className="h-1.5 mt-0.5" />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                  {onSelectChapter && (
                    <button
                      type="button"
                      onClick={() => onSelectChapter(ch.chapter_id)}
                      className="text-xs text-primary hover:underline flex items-center gap-1"
                    >
                      <BookOpen className="h-3.5 w-3.5" />
                      Go to chapter
                    </button>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
