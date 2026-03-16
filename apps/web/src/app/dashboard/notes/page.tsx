'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { getEmptyStateConfig } from '@/content/empty-states';
import { PageHeader } from '@/components/layout/PageHeader';
import { StickyNote, BookOpen } from 'lucide-react';
import { api } from '@/lib/api';

interface Project {
  id: string;
  name: string;
  created_at: string;
}

export default function NotesPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Project[]>('/api/v1/projects')
      .then(setProjects)
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false));
  }, [router]);

  return (
    <div className="p-6 lg:p-8 max-w-4xl">
      <PageHeader
        title="Ideas & notes"
        description="Your ideas, research, and scratch notes. Pick a project to begin."
      />

      {loading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : projects.length === 0 ? (
        <EmptyState
          icon={<StickyNote className="h-6 w-6" />}
          title={getEmptyStateConfig('no_projects_notes')!.title}
          description={getEmptyStateConfig('no_projects_notes')!.description}
          action={{ label: 'Back to Home', href: '/dashboard' }}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <Link key={p.id} href={`/dashboard/projects/${p.id}/notes`}>
              <Card
                variant="sanctuary"
                className="block p-6 hover:shadow-md transition-shadow cursor-pointer h-full"
              >
                <BookOpen className="h-8 w-8 text-primary mb-3" />
                <h3 className="font-semibold text-foreground">{p.name}</h3>
                <p className="text-sm text-primary font-medium mt-3">Open notes →</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
