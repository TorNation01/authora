'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { PageHeader } from '@/components/layout/PageHeader';
import { BookOpen, Plus, PenLine, Map, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';
import { Progress } from '@/components/ui/progress';
import { GamificationWidgets } from '@/components/gamification/GamificationWidgets';
import { FirstUseBanner } from '@/components/help';

interface Project {
  id: string;
  name: string;
  created_at: string;
}

interface JourneySummary {
  has_journey: boolean;
  nudge?: { message: string };
  next_step?: {
    phase_name: string;
    task: { id: string; title: string } | null;
    phase_progress: number;
    current_phase_index: number;
    total_phases: number;
    journey_complete?: boolean;
  };
}

export default function DashboardPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [journey, setJourney] = useState<JourneySummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api<Project[]>('/api/v1/projects').catch(() => []),
      api<JourneySummary>('/api/v1/journey').catch(() => ({ has_journey: false })),
    ]).then(([projs, j]) => {
      setProjects(projs);
      setJourney(j);
    }).finally(() => setLoading(false));
  }, []);

  const nextStep = projects.length === 0
    ? { label: 'Create your first project', href: '/dashboard/projects/new' }
    : { label: 'New project', href: '/dashboard/projects/new' };

  const showJourneyPrompt = journey?.has_journey === false;
  const showNextStep = journey?.has_journey && journey?.next_step && !journey.next_step.journey_complete;

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      <PageHeader
        title="Dashboard"
        description="Your writing projects and next steps"
        actions={
          <Button asChild>
            <Link href="/dashboard/projects/new">
              <Plus className="h-4 w-4 mr-2" />
              New project
            </Link>
          </Button>
        }
      />

      <FirstUseBanner />
      <GamificationWidgets />

      {showJourneyPrompt && (
        <Card variant="soft" className="mb-6">
          <div className="p-4 flex flex-row items-center justify-between gap-4 flex-wrap">
            <div>
              <p className="font-medium">Create your writing journey</p>
              <p className="text-sm text-muted-foreground">
                Get a personalized roadmap from idea to finished book.
              </p>
            </div>
            <Button asChild variant="outline" size="sm">
              <Link href="/onboarding">
                <Sparkles className="h-4 w-4 mr-2" />
                Start onboarding
              </Link>
            </Button>
          </div>
        </Card>
      )}

      {showNextStep && journey?.next_step?.task && (
        <Link href="/dashboard/journey">
          <Card variant="elevated" className="mb-6 border-primary/20 hover:border-primary/40 transition-colors cursor-pointer">
            <div className="p-4 flex flex-row items-center justify-between gap-4 flex-wrap">
              <div>
                <p className="text-sm text-muted-foreground flex items-center gap-1">
                  <Map className="h-3.5 w-3.5" />
                  {journey.next_step.phase_name} · Next step
                </p>
                <p className="font-medium">{journey.next_step.task.title}</p>
                <Progress
                  value={journey.next_step.phase_progress * 100}
                  size="sm"
                  className="mt-2 max-w-[200px]"
                />
              </div>
              <Button variant="ghost" size="sm">
                View journey
              </Button>
            </div>
          </Card>
        </Link>
      )}

      {journey?.nudge?.message && !showNextStep && journey.has_journey && (
        <Card variant="soft" className="mb-6">
          <div className="p-4">
            <p className="text-muted-foreground">{journey.nudge.message}</p>
            <Button asChild variant="link" size="sm" className="mt-2 p-0 h-auto">
              <Link href="/dashboard/journey">View your journey</Link>
            </Button>
          </div>
        </Card>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <p className="text-muted-foreground">Loading...</p>
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          icon={<BookOpen className="h-6 w-6" />}
          title="No projects yet"
          description="Create your first project to start your writing journey. We'll guide you through planning and writing."
          action={{ label: 'Create project', href: '/dashboard/projects/new' }}
        />
      ) : (
        <>
          <p className="text-sm text-muted-foreground mb-4">
            Your next step: open a project and start writing, or create a new one.
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <Link key={p.id} href={`/dashboard/projects/${p.id}`}>
                <Card
                  variant="sanctuary"
                  className="block p-6 hover:shadow-md transition-shadow cursor-pointer h-full"
                >
                  <BookOpen className="h-8 w-8 text-primary mb-3" />
                  <h3 className="font-semibold text-foreground">{p.name}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Created {new Date(p.created_at).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-primary font-medium mt-3 flex items-center gap-1">
                    Open project
                    <PenLine className="h-3 w-3" />
                  </p>
                </Card>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
