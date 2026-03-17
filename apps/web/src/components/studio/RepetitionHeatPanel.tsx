'use client';

import { useCallback, useEffect, useState } from 'react';
import { BookOpen, Loader2, Repeat } from 'lucide-react';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';
import { DENSITY_REPETITION, DENSITY_ACTIONS } from '@/content/density-copy';

interface ChapterHeat {
  chapter_index: number;
  chapter_id: string;
  title: string;
  word_count: number;
  in_chapter_repetition: number;
  cross_chapter_overlap: number;
  repetition_heat: number;
  heat_level: 'low' | 'moderate' | 'high' | 'very_high';
}

interface RepeatedPoint {
  phrase: string;
  occurrences: number;
  chapter_indices: number[];
}

interface RepetitionAnalysis {
  chapter_repetition_heat: ChapterHeat[];
  repeated_points: RepeatedPoint[];
  manuscript_repetition_score: number;
}

interface DensityAnalysis {
  scan_id: string | null;
  last_scan_at: string | null;
  scene_purpose_analysis: unknown;
  chapter_drag_analysis: unknown;
  repetition_analysis: RepetitionAnalysis | null;
}

interface RepetitionHeatPanelProps {
  projectId: string;
  bookId: string;
  activeChapterId: string | null;
  onSelectChapter?: (chapterId: string) => void;
}

function heatColor(level: string): string {
  switch (level) {
    case 'very_high':
      return 'bg-red-500/80';
    case 'high':
      return 'bg-amber-500/80';
    case 'moderate':
      return 'bg-amber-300/60';
    default:
      return 'bg-muted';
  }
}

export function RepetitionHeatPanel({
  projectId,
  bookId,
  activeChapterId,
  onSelectChapter,
}: RepetitionHeatPanelProps) {
  const [analysis, setAnalysis] = useState<DensityAnalysis | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchAnalysis = useCallback(async () => {
    try {
      const a = await api<DensityAnalysis>(
        `/api/v1/projects/${projectId}/books/${bookId}/density/analysis`
      );
      setAnalysis(a);
    } catch {
      setAnalysis(null);
    } finally {
      setLoading(false);
    }
  }, [projectId, bookId]);

  useEffect(() => {
    fetchAnalysis();
  }, [fetchAnalysis]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const rep = analysis?.repetition_analysis;
  if (!rep || !rep.chapter_repetition_heat?.length) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        {DENSITY_REPETITION.empty}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-2">
          <Repeat className="h-4 w-4" />
          <h4 className="text-sm font-medium">{DENSITY_REPETITION.heading}</h4>
        </div>
        <p className="text-xs text-muted-foreground">{DENSITY_REPETITION.subheading}</p>
      </div>
      {analysis.last_scan_at && (
        <p className="text-xs text-muted-foreground">
          {DENSITY_ACTIONS.fromScan}: {new Date(analysis.last_scan_at).toLocaleString()}
        </p>
      )}
      {rep.manuscript_repetition_score != null && (
        <div>
          <span className="text-xs text-muted-foreground">{DENSITY_REPETITION.manuscriptScore}: </span>
          <span className={cn(
            'text-sm font-medium',
            rep.manuscript_repetition_score >= 70 ? 'text-green-600' : rep.manuscript_repetition_score >= 50 ? 'text-amber-600' : 'text-red-600'
          )}>
            {Math.round(rep.manuscript_repetition_score)}/100
          </span>
        </div>
      )}

      <div>
        <h5 className="text-xs font-medium text-muted-foreground mb-2">{DENSITY_REPETITION.perChapterHeat}</h5>
        <div className="flex flex-wrap gap-1 mb-2">
          {rep.chapter_repetition_heat.map((ch) => (
            <button
              key={ch.chapter_id}
              type="button"
              onClick={() => onSelectChapter?.(ch.chapter_id)}
              title={`${ch.title}: ${ch.heat_level}`}
              className={cn(
                'h-6 min-w-[24px] rounded transition-colors',
                heatColor(ch.heat_level),
                activeChapterId === ch.chapter_id && 'ring-2 ring-primary ring-offset-1'
              )}
            />
          ))}
        </div>
        <p className="text-xs text-muted-foreground">
          {DENSITY_REPETITION.heatHint}
        </p>
      </div>

      <div className="space-y-2">
        {rep.chapter_repetition_heat.map((ch) => (
          <div
            key={ch.chapter_id}
            className={cn(
              'rounded-lg border p-2 flex items-center justify-between gap-2',
              activeChapterId === ch.chapter_id && 'ring-2 ring-primary'
            )}
          >
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{ch.title || `Ch. ${ch.chapter_index + 1}`}</p>
              <p className="text-xs text-muted-foreground">{ch.word_count} words</p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className={cn(
                'rounded px-2 py-0.5 text-xs font-medium',
                ch.heat_level === 'very_high' && 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
                ch.heat_level === 'high' && 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
                ch.heat_level === 'moderate' && 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-500',
                ch.heat_level === 'low' && 'text-muted-foreground'
              )}>
                {DENSITY_REPETITION.heatLevels[ch.heat_level] ?? ch.heat_level}
              </span>
              <span className="text-xs text-muted-foreground">
                {Math.round((ch.repetition_heat || 0) * 100)}%
              </span>
            </div>
            {onSelectChapter && (
              <button
                type="button"
                onClick={() => onSelectChapter(ch.chapter_id)}
                className="text-xs text-primary hover:underline shrink-0"
              >
                {DENSITY_ACTIONS.goShort}
              </button>
            )}
          </div>
        ))}
      </div>

      {rep.repeated_points?.length > 0 && (
        <div>
          <h5 className="text-xs font-medium text-muted-foreground mb-2">{DENSITY_REPETITION.repeatedPhrases}</h5>
          <ul className="space-y-1 max-h-32 overflow-auto">
            {rep.repeated_points.slice(0, 10).map((rp, i) => (
              <li key={i} className="text-xs">
                <span className="text-muted-foreground">&quot;{rp.phrase.length > 45 ? rp.phrase.slice(0, 42) + '...' : rp.phrase}&quot;</span>
                <span className="ml-1">×{rp.occurrences}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
