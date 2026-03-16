'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { PageHeader } from '@/components/layout/PageHeader';
import { BookOpen, Plus, Search, Settings, Users, Library } from 'lucide-react';
import { api } from '@/lib/api';

interface Book {
  id: string;
  title: string;
  type: string;
  genre?: string;
  created_at: string;
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
  const [projectName, setProjectName] = useState('');
  const [guidanceMode, setGuidanceMode] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api<ProjectData>(`/api/v1/projects/${projectId}`),
      api<Book[]>(`/api/v1/projects/${projectId}/books`),
    ])
      .then(([proj, bks]) => {
        setProjectName(proj.name);
        setGuidanceMode(proj.guidance_mode || null);
        setBooks(bks);
      })
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false));
  }, [projectId, router]);

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      <PageHeader
        title={projectName || 'Project'}
        description="Books in this project"
        backHref="/dashboard"
        backLabel="Back to Home"
        actions={
          <div className="flex gap-2">
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
      ) : books.length === 0 ? (
        <EmptyState
          icon={<BookOpen className="h-6 w-6" />}
          title="No books yet"
          description="Add your first book to start planning and writing. Choose fiction or non-fiction—we'll tailor the experience."
          action={{
            label: 'Create book',
            href: `/dashboard/projects/${projectId}/books/new`,
          }}
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {books.map((b) => (
            <Link key={b.id} href={`/dashboard/projects/${projectId}/books/${b.id}`}>
              <Card
                variant="sanctuary"
                className="block p-6 hover:shadow-md transition-shadow cursor-pointer h-full"
              >
                <BookOpen className="h-8 w-8 text-primary mb-3" />
                <h3 className="font-semibold text-foreground">{b.title}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {b.type} {b.genre ? `· ${b.genre}` : ''}
                </p>
                <p className="text-sm text-primary font-medium mt-3">Open book →</p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
