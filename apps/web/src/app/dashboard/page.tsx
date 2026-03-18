'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { getEmptyStateConfig } from '@/content/empty-states';
import { Input } from '@/components/ui/input';
import { PageHeader } from '@/components/layout/PageHeader';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { BookOpen, Plus, PenLine, Map, Sparkles, Search, Archive, ArchiveRestore, Copy, Trash2 } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { Progress } from '@/components/ui/progress';
import { GamificationWidgets } from '@/components/gamification/GamificationWidgets';
import { RetentionProgressWidget, DailyPromptCard } from '@/components/retention';
import { FirstUseBanner } from '@/components/help';
import { DashboardQuickStart } from '@/components/onboarding/DashboardQuickStart';
import { UsageDisplay } from '@/components/billing/UsageDisplay';
import { UpgradeCallout } from '@/components/billing/UpgradeCallout';

interface Project {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  last_accessed_at: string | null;
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

interface UserPreferences {
  preferences?: {
    onboarding_completed?: boolean;
    onboarding_progress?: { step_index: number };
  };
}

function buildProjectsUrl(params: { status?: string; q?: string; sort?: string }) {
  const searchParams = new URLSearchParams();
  if (params.status) searchParams.set('status', params.status);
  if (params.q) searchParams.set('q', params.q);
  if (params.sort) searchParams.set('sort', params.sort);
  const qs = searchParams.toString();
  return `/api/v1/projects${qs ? `?${qs}` : ''}`;
}

export default function DashboardPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [recentProject, setRecentProject] = useState<Project | null>(null);
  const [resumeSession, setResumeSession] = useState<{
    project_id: string;
    book_id: string;
    chapter_id: string;
    project_name: string;
    book_title: string;
    chapter_title: string;
  } | null>(null);
  const [journey, setJourney] = useState<JourneySummary | null>(null);
  const [preferences, setPreferences] = useState<UserPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('active');
  const [sort, setSort] = useState<string>('updated_at');
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchProjects = useCallback(() => {
    const url = buildProjectsUrl({
      status: statusFilter === 'all' ? 'all' : statusFilter,
      q: search.trim() || undefined,
      sort,
    });
    return api<Project[]>(url).then(setProjects).catch(() => setProjects([]));
  }, [statusFilter, search, sort]);

  useEffect(() => {
    Promise.all([
      fetchProjects(),
      api<Project | null>('/api/v1/projects/recent').catch(() => null).then(setRecentProject),
      api<{ resume: { project_id: string; book_id: string; chapter_id: string; project_name: string; book_title: string; chapter_title: string } | null }>('/api/v1/projects/resume')
        .then((r) => setResumeSession(r.resume))
        .catch(() => setResumeSession(null)),
      api<JourneySummary>('/api/v1/journey').catch(() => ({ has_journey: false })),
      api<UserPreferences>('/api/v1/auth/me/preferences').catch(() => ({ preferences: {} })),
    ]).then(([, , , j, p]) => {
      setJourney(j);
      setPreferences(p);
    }).finally(() => setLoading(false));
  }, [fetchProjects]);

  useEffect(() => {
    const t = setTimeout(() => fetchProjects(), 300);
    return () => clearTimeout(t);
  }, [search, statusFilter, sort, fetchProjects]);

  const handleArchive = async (p: Project) => {
    try {
      await api(`/api/v1/projects/${p.id}/archive`, { method: 'PATCH' });
      toast({ title: 'Project archived' });
      fetchProjects();
    } catch (e) {
      toast({ title: 'Failed to archive', variant: 'destructive' });
    }
  };

  const handleRestore = async (p: Project) => {
    try {
      await api(`/api/v1/projects/${p.id}/restore`, { method: 'PATCH' });
      toast({ title: 'Project restored' });
      fetchProjects();
    } catch (e) {
      toast({ title: 'Failed to restore', variant: 'destructive' });
    }
  };

  const handleDuplicate = async (p: Project) => {
    try {
      const created = await api<Project>(`/api/v1/projects/${p.id}/duplicate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({}),
      });
      toast({ title: 'Project duplicated' });
      fetchProjects();
      if (created?.id) router.push(`/dashboard/projects/${created.id}`);
    } catch (e) {
      toast({ title: 'Failed to duplicate', variant: 'destructive' });
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await api(`/api/v1/projects/${deleteTarget.id}?confirm=true`, { method: 'DELETE' });
      toast({ title: 'Project deleted' });
      setDeleteTarget(null);
      fetchProjects();
    } catch (e) {
      toast({ title: 'Failed to delete', variant: 'destructive' });
    } finally {
      setDeleting(false);
    }
  };

  const nextStep = projects.length === 0
    ? { label: 'Create your first project', href: '/dashboard/projects/new' }
    : { label: 'New project', href: '/dashboard/projects/new' };

  const onboardingComplete = preferences?.preferences?.onboarding_completed === true;
  const hasOnboardingProgress = (preferences?.preferences?.onboarding_progress?.step_index ?? 0) > 0;
  const showResumeSetup = !onboardingComplete && hasOnboardingProgress;
  const showJourneyPrompt = journey?.has_journey === false && !showResumeSetup;
  const showNextStep = journey?.has_journey && journey?.next_step && !journey.next_step.journey_complete;

  return (
    <div className="w-full min-w-0 max-w-5xl mx-auto p-4 sm:p-6 lg:p-8">
      <PageHeader
        title="Home"
        description="Your projects and what's next—we're here when you're ready"
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
      <UsageDisplay />
      <UpgradeCallout />
      <DailyPromptCard />
      <RetentionProgressWidget />
      <GamificationWidgets />

      {showResumeSetup && (
        <Card variant="soft" className="mb-6 border-primary/20">
          <div className="p-4 flex flex-row items-center justify-between gap-4 flex-wrap">
            <div>
              <p className="font-medium">Complete your setup</p>
              <p className="text-sm text-muted-foreground">
                You started setting up your writing space. Pick up where you left off—a few minutes to finish.
              </p>
            </div>
            <Button asChild variant="outline" size="sm">
              <Link href="/onboarding">
                <Sparkles className="h-4 w-4 mr-2" />
                Resume setup
              </Link>
            </Button>
          </div>
        </Card>
      )}

      {showJourneyPrompt && (
        <Card variant="soft" className="mb-6">
          <div className="p-4 flex flex-row items-center justify-between gap-4 flex-wrap">
            <div>
              <p className="font-medium">Get your personalized roadmap</p>
              <p className="text-sm text-muted-foreground">
                A gentle guide from idea to finished book. A few minutes, no pressure.
              </p>
            </div>
            <Button asChild variant="outline" size="sm">
              <Link href="/onboarding">
                <Sparkles className="h-4 w-4 mr-2" />
                Start the tour
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
                See journey
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
              <Link href="/dashboard/journey">View journey</Link>
            </Button>
          </div>
        </Card>
      )}

      {projects.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Quick start</h3>
          <DashboardQuickStart
            projectId={(recentProject && !recentProject.deleted_at ? recentProject : projects[0])?.id}
            recentProjectName={(recentProject && !recentProject.deleted_at ? recentProject : projects[0])?.name}
            hasJourney={journey?.has_journey}
            nextStepTitle={journey?.next_step?.task?.title}
            resumeSession={resumeSession}
          />
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <p className="text-muted-foreground">Loading your writing space...</p>
        </div>
      ) : projects.length === 0 ? (
        <EmptyState
          icon={<BookOpen className="h-6 w-6" />}
          title={getEmptyStateConfig('no_projects')!.title}
          description={getEmptyStateConfig('no_projects')!.description}
          action={{ label: 'Create project', href: '/dashboard/projects/new' }}
        />
      ) : (
        <>
          <div className="flex flex-wrap gap-4 mb-4">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search projects..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
                <SelectItem value="all">All</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sort} onValueChange={setSort}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="updated_at">Recently updated</SelectItem>
                <SelectItem value="last_accessed_at">Recently opened</SelectItem>
                <SelectItem value="name">Name</SelectItem>
                <SelectItem value="created_at">Date created</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <p className="text-sm text-muted-foreground mb-4">
            Open a project to start writing, or create a new one. We're here when you're ready.
          </p>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <Card
                key={p.id}
                variant="sanctuary"
                className="group relative block p-6 hover:shadow-md transition-shadow h-full"
              >
                <Link href={`/dashboard/projects/${p.id}`} className="block absolute inset-0 z-0" />
                <div className="relative z-10">
                  <div className="flex items-start justify-between gap-2">
                    <BookOpen className="h-8 w-8 text-primary mb-3 shrink-0" />
                    <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      {p.deleted_at ? (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={(e) => { e.preventDefault(); handleRestore(p); }}
                          title="Restore"
                        >
                          <ArchiveRestore className="h-4 w-4" />
                        </Button>
                      ) : (
                        <>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={(e) => { e.preventDefault(); handleArchive(p); }}
                            title="Archive"
                          >
                            <Archive className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={(e) => { e.preventDefault(); handleDuplicate(p); }}
                            title="Duplicate"
                          >
                            <Copy className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive hover:text-destructive"
                            onClick={(e) => { e.preventDefault(); setDeleteTarget(p); }}
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>
                  <h3 className="font-semibold text-foreground">{p.name}</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    {p.deleted_at ? 'Archived' : 'Created'} {new Date(p.deleted_at || p.created_at).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-primary font-medium mt-3 flex items-center gap-1">
                    Open and write
                    <PenLine className="h-3 w-3" />
                  </p>
                </div>
              </Card>
            ))}
          </div>
        </>
      )}

      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete project?</DialogTitle>
            <DialogDescription>
              This will permanently delete &quot;{deleteTarget?.name}&quot; and all its books, chapters, and notes. This cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)} disabled={deleting}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete} disabled={deleting}>
              {deleting ? 'Deleting...' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
