'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  BookOpen,
  Check,
  Circle,
  Loader2,
  Map,
  PenLine,
  Sparkles,
} from 'lucide-react';
import { FIRST_BOOK_JOURNEY } from '@/content/onboarding-copy';

interface JourneyTask {
  id: string;
  title: string;
  description: string | null;
  task_type: string;
  completed_at: string | null;
}

interface NextStep {
  phase: string;
  phase_name: string;
  task: {
    id: string;
    title: string;
    description: string | null;
    task_type: string;
  } | null;
  phase_progress: number;
  total_phases: number;
  current_phase_index: number;
  phase_advanced?: boolean;
  journey_complete?: boolean;
}

interface JourneyData {
  has_journey: boolean;
  message?: string;
  journey?: {
    id: string;
    book_type: string;
    writing_mode: string;
    current_phase: string;
    roadmap?: { phases: { id: string; name: string; description: string }[] };
  };
  tasks?: JourneyTask[];
  nudge?: { type: string; message: string };
  next_step?: NextStep;
}

const PHASE_LABELS: Record<string, string> = {
  idea: FIRST_BOOK_JOURNEY.phases.define,
  concept: FIRST_BOOK_JOURNEY.phases.structure,
  outline: FIRST_BOOK_JOURNEY.phases.structure,
  chapter_planning: FIRST_BOOK_JOURNEY.phases.opening,
  drafting: FIRST_BOOK_JOURNEY.phases.moving,
  revision: FIRST_BOOK_JOURNEY.phases.revise,
  polish: FIRST_BOOK_JOURNEY.phases.revise,
  export_prep: FIRST_BOOK_JOURNEY.phases.export,
};

export default function JourneyPage() {
  const [data, setData] = useState<JourneyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [completingId, setCompletingId] = useState<string | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    api<JourneyData>('/api/v1/journey')
      .then(setData)
      .catch(() => setData({ has_journey: false }))
      .finally(() => setLoading(false));
  }, []);

  async function completeTask(taskId: string) {
    setCompletingId(taskId);
    try {
      await api('/api/v1/journey/tasks/complete', {
        method: 'POST',
        body: JSON.stringify({ task_id: taskId }),
      });
      toast({ title: 'Task completed!', description: 'Great progress.' });
      const updated = await api<JourneyData>('/api/v1/journey');
      setData(updated);
    } catch (e) {
      toast({
        title: 'Could not complete task',
        description: e instanceof Error ? e.message : 'Please try again.',
        variant: 'destructive',
      });
    } finally {
      setCompletingId(null);
    }
  }

  if (loading) {
    return (
      <div className="p-6 lg:p-8 max-w-5xl flex items-center justify-center min-h-[40vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (!data?.has_journey) {
    return (
      <div className="p-6 lg:p-8 max-w-5xl">
        <PageHeader
          title={FIRST_BOOK_JOURNEY.heading}
          description={FIRST_BOOK_JOURNEY.subheading}
        />
        <Card variant="sanctuary" className="max-w-md">
          <CardHeader>
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mb-2">
              <Map className="h-6 w-6" />
            </div>
            <CardTitle className="text-xl font-serif">Start your journey</CardTitle>
            <CardDescription>
              Take a quick tour to get your personalized roadmap. We&apos;ll guide you through each phase—no rush.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/onboarding">
                <Sparkles className="h-4 w-4 mr-2" />
                Take the tour
              </Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const { journey, tasks = [], nudge, next_step } = data;
  const isComplete = next_step?.journey_complete;

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      <PageHeader
        title="Your writing journey"
        description={journey ? `${journey.book_type === 'fiction' ? 'Fiction' : 'Non-fiction'} · ${journey.writing_mode === 'solo' ? 'Solo' : journey.writing_mode === 'cowrite' ? 'Co-write' : 'Ghostwriter'}` : ''}
      />

      {nudge && (
        <Card variant="soft" className="mb-6">
          <CardContent className="py-4">
            <p className="text-muted-foreground">{nudge.message}</p>
          </CardContent>
        </Card>
      )}

      {isComplete ? (
        <Card variant="sanctuary">
          <CardHeader>
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary mb-2">
              <Check className="h-7 w-7" />
            </div>
            <CardTitle className="text-2xl font-serif">You did it!</CardTitle>
            <CardDescription className="text-base">
              You&apos;ve finished all phases. Your book is ready for export and publishing. Celebrate.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild>
              <Link href="/dashboard/export">
                <PenLine className="h-4 w-4 mr-2" />
                Go to export
              </Link>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Phase progress */}
          {next_step && (
            <Card variant="sanctuary" className="mb-6">
              <CardHeader>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-muted-foreground">
                    Phase {next_step.current_phase_index + 1} of {next_step.total_phases}
                  </span>
                  <span className="text-sm font-medium">{next_step.phase_name}</span>
                </div>
                <Progress
                  value={(next_step.current_phase_index / next_step.total_phases) * 100}
                  max={100}
                  showLabel
                  size="sm"
                />
              </CardHeader>
            </Card>
          )}

          {/* Next step CTA */}
          {next_step?.task && (
            <Card variant="elevated" className="mb-6 border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  Your next step
                </CardTitle>
                <CardDescription>{next_step.task.title}</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  onClick={() => completeTask(next_step.task!.id)}
                  disabled={completingId === next_step.task.id}
                >
                  {completingId === next_step.task.id ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <Check className="h-4 w-4 mr-2" />
                  )}
                  Done
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Roadmap phases */}
          {journey?.roadmap?.phases && (
            <div className="space-y-4">
              <h3 className="font-semibold flex items-center gap-2">
                <Map className="h-4 w-4" />
                Roadmap
              </h3>
              <div className="grid gap-2">
                {journey.roadmap.phases.map((phase: { id: string; name: string; description: string }, idx: number) => {
                  const isCurrent = phase.id === journey.current_phase;
                  const isPast = next_step && idx < next_step.current_phase_index;
                  return (
                    <div
                      key={phase.id}
                      className={`flex items-center gap-3 rounded-lg border p-3 ${
                        isCurrent ? 'border-primary bg-primary/5' : isPast ? 'opacity-75' : ''
                      }`}
                    >
                      <div
                        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                          isPast ? 'bg-primary/20 text-primary' : isCurrent ? 'bg-primary text-primary-foreground' : 'bg-muted'
                        }`}
                      >
                        {isPast ? <Check className="h-4 w-4" /> : idx + 1}
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="font-medium">{phase.name}</p>
                        <p className="text-sm text-muted-foreground truncate">{phase.description}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Current phase checklist */}
          {tasks.length > 0 && (
            <div className="mt-8 space-y-4">
              <h3 className="font-semibold flex items-center gap-2">
                <BookOpen className="h-4 w-4" />
                {PHASE_LABELS[journey?.current_phase || ''] || journey?.current_phase} checklist
              </h3>
              <div className="space-y-2">
                {tasks.map((t) => (
                  <div
                    key={t.id}
                    className={`flex items-center gap-3 rounded-lg border p-3 ${
                      t.completed_at ? 'opacity-60' : ''
                    }`}
                  >
                    <button
                      onClick={() => !t.completed_at && completeTask(t.id)}
                      disabled={!!t.completed_at || completingId === t.id}
                      className="shrink-0 rounded-full p-1 hover:bg-muted transition-colors"
                      aria-label={t.completed_at ? 'Completed' : 'Mark complete'}
                    >
                      {t.completed_at ? (
                        <Check className="h-5 w-5 text-primary" />
                      ) : (
                        <Circle className="h-5 w-5 text-muted-foreground" />
                      )}
                    </button>
                    <div className="min-w-0 flex-1">
                      <p className={t.completed_at ? 'line-through text-muted-foreground' : ''}>
                        {t.title}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
