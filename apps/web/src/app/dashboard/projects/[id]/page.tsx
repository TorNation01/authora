'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { getEmptyStateConfig } from '@/content/empty-states';
import { PageHeader } from '@/components/layout/PageHeader';
import { BookOpen, Plus, Search, Settings, Users, Library, LayoutGrid } from 'lucide-react';
import { ProjectProgressCard } from '@/components/retention';
import { api } from '@/lib/api';

interface Book {
  id: string;
  title: string;
  type: string;
  genre?: string;
  created_at: string;
}

interface BookProgress {
  id: string;
  word_count: number;
  chapter_count: number;
  chapters_done: number;
}

interface ProjectData {
  name: string;
  guidance_mode?: string;
}

export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [books, setBooks] = useState<Book[]>([]);
  const [progress, setProgress] = useState<Record<string, BookProgress>>({});
  const [projectName, setProjectName] = useState('');
  const [guidanceMode, setGuidanceMode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api<ProjectData>(`/api/v1/projects/${projectId}`),
      api<Book[]>(`/api/v1/projects/${projectId}/books`),
      api<{ books: BookProgress[] }>(`/api/v1/projects/${projectId}/progress`).catch(() => ({ books: [] })),
    ])
      .then(([proj, bks, prog]) => {
        setProjectName(proj.name);
        setGuidanceMode(proj.guidance_mode || null);
        setBooks(bks);
        const map: Record<string, BookProgress> = {};
        (prog.books || []).forEach((b) => {
          map[b.id] = b;
        });
        setProgress(map);
      })
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false));
  }, [projectId, router]);

  return (
    <div className="w-full min-w-0 max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
      <PageHeader
        title={projectName || 'Project'}
        description="Books in this project"
        backHref="/dashboard"
        backLabel="Back to Home"
        actions={
          <div className="flex flex-wrap gap-2">
            {guidanceMode && (
              <span className="rounded-full border bg-muted/50 px-2.5 py-1 text-xs font-medium text-muted-foreground capitalize">
                {guidanceMode}
              </span>
            )}
            <Button variant="outline" asChild>
              <Link href={`/dashboard/projects/${projectId}/sharing`}>
                <Users className="h-4 w-4 mr-2" />
                Sharing
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/dashboard/projects/${projectId}/settings`}>
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/dashboard/projects/${projectId}/characters`}>
                <Users className="h-4 w-4 mr-2" />
                Characters
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/dashboard/projects/${projectId}/vault`}>
                <Library className="h-4 w-4 mr-2" />
                Vault
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/dashboard/projects/${projectId}/search`}>
                <Search className="h-4 w-4 mr-2" />
                Search
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/dashboard/projects/${projectId}/manage`}>
                <LayoutGrid className="h-4 w-4 mr-2" />
                Manage
              </Link>
            </Button>
            <Button asChild>
              <Link href={`/dashboard/projects/${projectId}/books/new`}>
                <Plus className="h-4 w-4 mr-2" />
                New book
              </Link>
            </Button>
          </div>
        }
      />

      {loading ? (
        <p className="text-muted-foreground">Loading...</p>
      ) : (
        <>
          <div className="mb-6">
            <ProjectProgressCard projectId={projectId} projectName={projectName} />
          </div>
          {books.length === 0 ? (
            <EmptyState
              icon={<BookOpen className="h-6 w-6" />}
              title={getEmptyStateConfig('no_books')!.title}
              description={getEmptyStateConfig('no_books')!.description}
              action={{
                label: 'Create book',
                href: `/dashboard/projects/${projectId}/books/new`,
              }}
            />
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {books.map((b) => {
                const stat = progress[b.id];
                const complete = !!stat && stat.chapter_count > 0 && stat.word_count > 0;
                return (
                  <Card
                    key={b.id}
                    variant="sanctuary"
                    className="flex h-full flex-col p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <BookOpen className="h-8 w-8 text-primary" />
                      {complete && (
                        <span className="rounded-full border border-border/60 px-2 py-0.5 text-[11px] text-muted-foreground">
                          Manuscript complete
                        </span>
                      )}
                    </div>
                    <Link href={`/dashboard/projects/${projectId}/books/${b.id}`} className="mt-3">
                      <h3 className="font-semibold text-foreground hover:underline">{b.title}</h3>
                    </Link>
                    <p className="text-sm text-muted-foreground mt-1">
                      {b.type} {b.genre ? `· ${b.genre}` : ''}
                    </p>
                    {stat && stat.word_count > 0 && (
                      <p className="mt-2 text-xs text-muted-foreground">
                        {stat.word_count.toLocaleString()} words · {stat.chapter_count} chapters
                      </p>
                    )}
                    <div className="mt-auto flex items-center justify-between gap-3 pt-4">
                      <Link
                        href={`/dashboard/projects/${projectId}/books/${b.id}`}
                        className="text-sm text-primary font-medium"
                      >
                        Open book →
                      </Link>
                      <Link
                        href={`/dashboard/projects/${projectId}/books/${b.id}/publish`}
                        className="text-sm text-muted-foreground hover:text-foreground"
                      >
                        Publish{complete ? ' & release' : ''} →
                      </Link>
                    </div>
                  </Card>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
