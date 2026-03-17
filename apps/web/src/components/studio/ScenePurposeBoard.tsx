'use client';

import { useCallback, useEffect, useState } from 'react';
import { BookOpen, Loader2, Target } from 'lucide-react';
import { api } from '@/lib/api';
import { cn } from '@/lib/utils';
import { DENSITY_PURPOSE, DENSITY_ACTIONS } from '@/content/density-copy';

interface ChapterPurpose {
  chapter_index: number;
  chapter_id: string;
  title: string;
  word_count: number;
  primary_jobs: string[];
  purpose_clarity: number;
  flags: string[];
}

interface ScenePurpose {
  section_index: number;
  chapter_id: string;
  chapter_title: string;
  word_count: number;
  primary_jobs: string[];
  flags: string[];
  suggestion: string | null;
}

interface ScenePurposeAnalysis {
  chapter_purposes: ChapterPurpose[];
  scene_purposes: ScenePurpose[];
}

interface DensityAnalysis {
  scan_id: string | null;
  last_scan_at: string | null;
  scene_purpose_analysis: ScenePurposeAnalysis | null;
  chapter_drag_analysis: unknown;
  repetition_analysis: unknown;
}

interface ScenePurposeBoardProps {
  projectId: string;
  bookId: string;
  activeChapterId: string | null;
  onSelectChapter?: (chapterId: string) => void;
}

const JOB_LABELS: Record<string, string> = {
  move_plot: 'Move plot',
  deepen_character: 'Deepen character',
  escalate_tension: 'Escalate tension',
  deliver_payoff: 'Deliver payoff',
  build_setup: 'Build setup',
  deliver_reflection: 'Deliver reflection',
  explain_concept: 'Explain concept',
  provide_example: 'Provide example',
  create_transition: 'Create transition',
  provide_exercise: 'Provide exercise',
  reinforce_theme: 'Reinforce theme',
  unclear: 'Unclear',
};

export function ScenePurposeBoard({
  projectId,
  bookId,
  activeChapterId,
  onSelectChapter,
}: ScenePurposeBoardProps) {
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

  const purpose = analysis?.scene_purpose_analysis;
  if (!purpose || !purpose.chapter_purposes?.length) {
    return (
      <div className="p-4 text-sm text-muted-foreground">
        {DENSITY_PURPOSE.empty}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4" />
          <h4 className="text-sm font-medium">{DENSITY_PURPOSE.heading}</h4>
        </div>
        <p className="text-xs text-muted-foreground">{DENSITY_PURPOSE.subheading}</p>
      </div>
      {analysis.last_scan_at && (
        <p className="text-xs text-muted-foreground">
          {DENSITY_ACTIONS.fromScan}: {new Date(analysis.last_scan_at).toLocaleString()}
        </p>
      )}
      <div className="space-y-3 overflow-auto">
        {purpose.chapter_purposes.map((cp) => (
          <div
            key={cp.chapter_id}
            className={cn(
              'rounded-lg border p-3',
              activeChapterId === cp.chapter_id && 'ring-2 ring-primary'
            )}
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-muted-foreground">Ch. {cp.chapter_index + 1}</span>
              <span className="text-xs font-medium">{cp.word_count} words</span>
            </div>
            <p className="font-medium truncate mt-0.5">{cp.title || `Chapter ${cp.chapter_index + 1}`}</p>
            <div className="flex flex-wrap gap-1 mt-2">
              {(cp.primary_jobs || []).map((j) => (
                <span
                  key={j}
                  className="rounded px-2 py-0.5 text-xs bg-muted"
                >
                  {JOB_LABELS[j] ?? j}
                </span>
              ))}
            </div>
            {cp.purpose_clarity != null && (
              <div className="mt-2">
                <span className="text-xs text-muted-foreground">{DENSITY_PURPOSE.purposeClarity}: </span>
                <span className={cn(
                  'text-xs font-medium',
                  cp.purpose_clarity >= 0.7 ? 'text-green-600' : cp.purpose_clarity >= 0.5 ? 'text-amber-600' : 'text-red-600'
                )}>
                  {Math.round(cp.purpose_clarity * 100)}%
                </span>
              </div>
            )}
            {cp.flags?.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {cp.flags.map((f) => (
                  <span key={f} className="text-xs text-amber-600 dark:text-amber-400">
                    {f.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            )}
            {onSelectChapter && (
              <button
                type="button"
                onClick={() => onSelectChapter(cp.chapter_id)}
                className="mt-2 text-xs text-primary hover:underline flex items-center gap-1"
              >
                <BookOpen className="h-3.5 w-3.5" />
                {DENSITY_PURPOSE.goToChapter}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
