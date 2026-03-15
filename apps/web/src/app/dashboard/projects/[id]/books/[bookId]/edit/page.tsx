'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { Progress } from '@/components/ui/progress';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  BarChart3,
  FileText,
  Loader2,
  RefreshCw,
  Sparkles,
  ChevronLeft,
} from 'lucide-react';

interface ChapterScorecard {
  chapter_id?: string;
  chapter_title?: string;
  overall_score?: number;
  readability?: { flesch_reading_ease?: number; grade_label?: string };
  sentence_balance?: { balance_score?: number; issues?: string[] };
  filler_words?: { items?: { word: string; count: number }[] };
  passive_voice?: { items?: unknown[] };
  repeated_phrases?: { items?: { phrase: string; count: number }[] };
  grammar_clarity?: { clarity_score?: number; ai_available?: boolean };
  structure?: { opening_strength?: number; ending_strength?: number };
  fiction_hints?: { pacing?: string; dialogue_balance?: string };
  nonfiction_hints?: { teaching_flow?: string; argument_strength?: string };
}

interface ManuscriptHealth {
  overall_score: number;
  chapter_count: number;
  chapters: ChapterScorecard[];
  summary: string;
}

export default function EditPolishPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const bookId = params.bookId as string;
  const [health, setHealth] = useState<ManuscriptHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const { toast } = useToast();

  const fetchHealth = () => {
    setLoading(true);
    api<ManuscriptHealth>(
      `/api/v1/projects/${projectId}/books/${bookId}/editorial/manuscript-health`
    )
      .then(setHealth)
      .catch(() => setHealth(null))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchHealth();
  }, [projectId, bookId]);

  const runAnalysis = async () => {
    setAnalyzing(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/editorial/analyze/book`, {
        method: 'POST',
      });
      toast({ title: 'Analysis complete', description: 'Refreshing report...' });
      fetchHealth();
    } catch (e) {
      toast({
        title: 'Analysis failed',
        description: e instanceof Error ? e.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      <div className="flex items-center gap-4 mb-6">
        <Link href={`/dashboard/projects/${projectId}/books/${bookId}`}>
          <Button variant="ghost" size="sm">
            <ChevronLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
        </Link>
      </div>

      <PageHeader
        title="Edit & Polish"
        description="Editorial insights, readability, and manuscript health."
        actions={
          <Button onClick={runAnalysis} disabled={analyzing}>
            {analyzing ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            {analyzing ? 'Analyzing...' : 'Run analysis'}
          </Button>
        }
      />

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      ) : !health || health.chapter_count === 0 ? (
        <Card variant="soft" className="p-8">
          <div className="text-center">
            <Sparkles className="h-12 w-12 text-primary/60 mx-auto mb-4" />
            <p className="font-medium">No analysis yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Run analysis to get readability scores, filler word detection, passive voice, and more.
            </p>
            <Button onClick={runAnalysis} disabled={analyzing} className="mt-4">
              {analyzing ? 'Analyzing...' : 'Run analysis'}
            </Button>
          </div>
        </Card>
      ) : (
        <>
          <Card variant="sanctuary" className="p-6 mb-6">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
                <BarChart3 className="h-7 w-7 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">{health.overall_score}/100</p>
                <p className="text-sm text-muted-foreground">Manuscript health</p>
              </div>
              <div className="flex-1" />
              <p className="text-sm text-muted-foreground">{health.summary}</p>
            </div>
          </Card>

          <div className="space-y-4">
            <h3 className="font-semibold">Chapter scorecards</h3>
            {health.chapters.map((ch) => (
              <Card key={ch.chapter_id || ''} variant="sanctuary" className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="font-medium">{ch.chapter_title || 'Untitled'}</p>
                    <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                      {ch.overall_score !== undefined && (
                        <span>Score: {ch.overall_score}/100</span>
                      )}
                      {ch.readability?.grade_label && (
                        <span>Readability: {ch.readability.grade_label}</span>
                      )}
                      {ch.grammar_clarity?.clarity_score !== undefined && (
                        <span>Clarity: {ch.grammar_clarity.clarity_score}/100</span>
                      )}
                    </div>
                    {ch.sentence_balance?.issues && ch.sentence_balance.issues.length > 0 && (
                      <ul className="mt-2 text-sm text-muted-foreground list-disc list-inside">
                        {ch.sentence_balance.issues.slice(0, 2).map((i, idx) => (
                          <li key={idx}>{i}</li>
                        ))}
                      </ul>
                    )}
                    {ch.filler_words?.items && ch.filler_words.items.length > 0 && (
                      <p className="mt-1 text-xs text-muted-foreground">
                        Filler words: {ch.filler_words.items.map((f) => `${f.word} (${f.count})`).join(', ')}
                      </p>
                    )}
                    {ch.structure?.opening_strength !== undefined && (
                      <p className="mt-1 text-xs text-muted-foreground">
                        Opening: {ch.structure.opening_strength}/100 · Ending: {ch.structure.ending_strength}/100
                      </p>
                    )}
                  </div>
                  <Link href={`/dashboard/projects/${projectId}/books/${bookId}?chapter=${ch.chapter_id}`}>
                    <Button variant="outline" size="sm">
                      <FileText className="h-3.5 w-3.5 mr-1" />
                      Edit
                    </Button>
                  </Link>
                </div>
                {ch.overall_score !== undefined && (
                  <Progress
                    value={ch.overall_score}
                    size="sm"
                    className="mt-3"
                  />
                )}
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
