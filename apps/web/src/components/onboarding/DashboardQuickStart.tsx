'use client';

import Link from 'next/link';
import { Card } from '@/components/ui/card';
import {
  PenLine,
  Maximize2,
  StickyNote,
  ClipboardList,
  FileDown,
  Plus,
  Map,
} from 'lucide-react';
import { QUICK_START_OPTIONS } from '@/content/onboarding-copy';

interface DashboardQuickStartProps {
  projectId?: string | null;
  recentProjectName?: string;
  hasJourney?: boolean;
  nextStepTitle?: string | null;
}

export function DashboardQuickStart({
  projectId,
  recentProjectName,
  hasJourney,
  nextStepTitle,
}: DashboardQuickStartProps) {
  const hasProject = !!projectId;

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {hasProject && (
        <Link href={`/dashboard/projects/${projectId}`}>
          <Card
            variant="elevated"
            className="h-full p-4 border-primary/20 hover:border-primary/40 transition-colors cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-primary/10 p-2">
                <PenLine className="h-5 w-5 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{QUICK_START_OPTIONS.continueWriting}</p>
                <p className="text-sm text-muted-foreground truncate">{recentProjectName || 'Open project'}</p>
              </div>
            </div>
          </Card>
        </Link>
      )}

      {hasJourney && nextStepTitle && (
        <Link href="/dashboard/journey">
          <Card
            variant="elevated"
            className="h-full p-4 border-primary/20 hover:border-primary/40 transition-colors cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-primary/10 p-2">
                <Map className="h-5 w-5 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{QUICK_START_OPTIONS.todaysGoal}</p>
                <p className="text-sm text-muted-foreground truncate">{nextStepTitle}</p>
              </div>
            </div>
          </Card>
        </Link>
      )}

      {hasProject && (
        <Link href={`/dashboard/projects/${projectId}`}>
          <Card variant="soft" className="h-full p-4 hover:bg-muted/50 transition-colors cursor-pointer">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2">
                <Maximize2 className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{QUICK_START_OPTIONS.focusMode}</p>
                <p className="text-sm text-muted-foreground">Clear the noise. Stay with the page.</p>
              </div>
            </div>
          </Card>
        </Link>
      )}

      {hasProject && (
        <Link href={`/dashboard/projects/${projectId}/notes`}>
          <Card variant="soft" className="h-full p-4 hover:bg-muted/50 transition-colors cursor-pointer">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2">
                <StickyNote className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{QUICK_START_OPTIONS.openNotes}</p>
                <p className="text-sm text-muted-foreground">Notes & research</p>
              </div>
            </div>
          </Card>
        </Link>
      )}

      {hasProject && (
        <Link href={`/dashboard/projects/${projectId}`}>
          <Card variant="soft" className="h-full p-4 hover:bg-muted/50 transition-colors cursor-pointer">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-muted p-2">
                <ClipboardList className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{QUICK_START_OPTIONS.continueRevision}</p>
                <p className="text-sm text-muted-foreground">Work through the manuscript</p>
              </div>
            </div>
          </Card>
        </Link>
      )}

      <Link href="/dashboard/export">
        <Card variant="soft" className="h-full p-4 hover:bg-muted/50 transition-colors cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-muted p-2">
              <FileDown className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-medium">{QUICK_START_OPTIONS.exportManuscript}</p>
              <p className="text-sm text-muted-foreground">Word, PDF, EPUB</p>
            </div>
          </div>
        </Card>
      </Link>

      <Link href="/dashboard/projects/new">
        <Card variant="soft" className="h-full p-4 hover:bg-muted/50 transition-colors cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-muted p-2">
              <Plus className="h-5 w-5 text-muted-foreground" />
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-medium">{QUICK_START_OPTIONS.newProject}</p>
              <p className="text-sm text-muted-foreground">Start fresh</p>
            </div>
          </div>
        </Card>
      </Link>
    </div>
  );
}
