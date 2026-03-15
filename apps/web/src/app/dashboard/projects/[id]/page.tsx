'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { EmptyState } from '@/components/ui/empty-state';
import { PageHeader } from '@/components/layout/PageHeader';
import { BookOpen, Plus } from 'lucide-react';
import { api } from '@/lib/api';

interface Book {
  id: string;
  title: string;
  type: string;
  genre?: string;
  created_at: string;
}

export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [books, setBooks] = useState<Book[]>([]);
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api<{ name: string }>(`/api/v1/projects/${projectId}`),
      api<Book[]>(`/api/v1/projects/${projectId}/books`),
    ])
      .then(([proj, bks]) => {
        setProjectName(proj.name);
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
          <Button asChild>
            <Link href={`/dashboard/projects/${projectId}/books/new`}>
              <Plus className="h-4 w-4 mr-2" />
              New book
            </Link>
          </Button>
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
