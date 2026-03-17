'use client';

import { useCallback, useEffect, useState } from 'react';
import { BookOpen, Loader2, Wind } from 'lucide-react';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';
import { DENSITY_DRAG, DENSITY_ACTIONS } from '@/content/density-copy';

interface ChapterDragScore {
  chapter_index: number;
  chapter_id: string;
  title: string;
  word_count: number;
  movement: number;
  information_density: number;
  drag_score: number;
  is_dragging: boolean;
}

interface DragRun {
  chapter_indices: number[];
  chapter_ids: string[];
  titles: string[];
  total_words: number;
  suggestion: string;
}

interface MergeCandidate {
  chapter_indices: number[];
  chapter_ids: string[];
  titles: string[];
  word_counts: number[];
  combined_words: number;
  suggestion: string;
}

interface ChapterDragAnalysis {
  drag_runs: DragRun[];
  merge_candidates: MergeCandidate[];
  compression_candidates: { chapter_index: number; chapter_id: string; title: string; word_count: number; suggestion: string }[];
  chapter_drag_scores: ChapterDragScore[];
}

interface DensityAnalysis {
  scan_id: string | null;
  last_scan_at: string | null;
  scene_purpose_analysis: unknown;
  chapter_drag_analysis: ChapterDragAnalysis | null;
  repetition_analysis: unknown;
}

interface ChapterDragPanelProps {
  projectId: string;
  bookId: string;
  activeChapterId: string | null;
  onSelectChapter?: (chapterId: string) => void;
}

export function ChapterDragPanel({
  projectId,
  bookId,
  activeChapterId,
  onSelectChapter,
}: ChapterDragPanelProps) {
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

  const drag = analysis?.chapter_drag_analysis;
  if (!drag || !drag.chapter_drag_scores?.length) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        {DENSITY_DRAG.empty}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-2">
          <Wind className="h-4 w-4" />
          <h4 className="text-sm font-medium">{DENSITY_DRAG.heading}</h4>
        </div>
        <p className="text-xs text-muted-foreground">{DENSITY_DRAG.subheading}</p>
      </div>
      {analysis.last_scan_at && (
        <p className="text-xs text-muted-foreground">
          {DENSITY_ACTIONS.fromScan}: {new Date(analysis.last_scan_at).toLocaleString()}
        </p>
      )}

      {drag.drag_runs?.length > 0 && (
        <div>
          <h5 className="text-xs font-medium text-muted-foreground mb-2">{DENSITY_DRAG.consecutiveDrag}</h5>
          <ul className="space-y-2">
            {drag.drag_runs.map((run, i) => (
              <li key={i} className="rounded-lg border border-amber-200 dark:border-amber-800 p-3">
                <p className="text-xs font-medium text-amber-700 dark:text-amber-400">
                  Ch. {run.chapter_indices.map((x) => x + 1).join(', ')}
                </p>
                <p className="text-sm mt-1">{run.titles.join(' → ')}</p>
                <p className="text-xs text-muted-foreground mt-1">{run.total_words} words total</p>
                <p className="text-xs mt-1">{run.suggestion}</p>
                {onSelectChapter && run.chapter_ids[0] && (
                  <button
                    type="button"
                    onClick={() => onSelectChapter(run.chapter_ids[0])}
                    className="mt-2 text-xs text-primary hover:underline flex items-center gap-1"
                  >
                    <BookOpen className="h-3.5 w-3.5" />
                    {DENSITY_DRAG.goToFirstChapter}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {drag.merge_candidates?.length > 0 && (
        <div>
          <h5 className="text-xs font-medium text-muted-foreground mb-2">{DENSITY_DRAG.mergeCandidates}</h5>
          <ul className="space-y-2">
            {drag.merge_candidates.map((mc, i) => (
              <li key={i} className="rounded-lg border p-3">
                <p className="text-xs font-medium">
                  Ch. {mc.chapter_indices.map((x) => x + 1).join(' + ')}
                </p>
                <p className="text-sm mt-1">{mc.titles.join(' + ')}</p>
                <p className="text-xs text-muted-foreground mt-1">{mc.combined_words} words</p>
                <p className="text-xs mt-1">{mc.suggestion}</p>
                {onSelectChapter && mc.chapter_ids[0] && (
                  <button
                    type="button"
                    onClick={() => onSelectChapter(mc.chapter_ids[0])}
                    className="mt-2 text-xs text-primary hover:underline"
                  >
                    {DENSITY_DRAG.goToChapter}
                  </button>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h5 className="text-xs font-medium text-muted-foreground mb-2">{DENSITY_DRAG.allChapters}</h5>
        <div className="space-y-2">
          {drag.chapter_drag_scores.map((cs) => (
            <div
              key={cs.chapter_id}
              className={cn(
                'rounded-lg border p-2 flex items-center justify-between gap-2',
                activeChapterId === cs.chapter_id && 'ring-2 ring-primary',
                cs.is_dragging && 'border-amber-300 dark:border-amber-700'
              )}
            >
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-medium">{cs.title || `Ch. ${cs.chapter_index + 1}`}</p>
                <p className="text-xs text-muted-foreground">{cs.word_count} words</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {cs.is_dragging ? (
                  <span className="text-xs font-medium text-amber-600">{DENSITY_DRAG.dragging}</span>
                ) : (
                  <span className="text-xs text-muted-foreground">{DENSITY_DRAG.ok}</span>
                )}
                <span className={cn(
                  'text-xs',
                  (cs.drag_score || 0) > 0.6 ? 'text-amber-600' : 'text-muted-foreground'
                )}>
                  {Math.round((cs.drag_score || 0) * 100)}%
                </span>
              </div>
              {onSelectChapter && (
                <button
                  type="button"
                  onClick={() => onSelectChapter(cs.chapter_id)}
                  className="text-xs text-primary hover:underline shrink-0"
                >
                  {DENSITY_ACTIONS.goShort}
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
