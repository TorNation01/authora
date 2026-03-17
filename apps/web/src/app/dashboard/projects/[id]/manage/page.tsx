'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { PageHeader } from '@/components/layout/PageHeader';
import { api } from '@/lib/api';
import { LayoutGrid, List, Calendar, Filter, Tag, BookOpen } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Chapter {
  id: string;
  title: string;
  sort_order: number;
  word_count: number;
  section_status?: string | null;
  section_group?: string | null;
  tags?: string[];
}

interface Book {
  id: string;
  title: string;
  chapters: Chapter[];
}

const STATUS_LABELS: Record<string, string> = {
  draft: 'Draft',
  revising: 'Revising',
  review: 'Review',
  done: 'Done',
};

const STATUS_COLORS: Record<string, string> = {
  draft: 'bg-muted text-muted-foreground',
  revising: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
  review: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  done: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
};

export default function ProjectManagePage() {
  const params = useParams();
  const projectId = params.id as string;
  const [books, setBooks] = useState<Book[]>([]);
  const [projectName, setProjectName] = useState('');
  const [view, setView] = useState<'list' | 'storyboard' | 'timeline'>('storyboard');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterTag, setFilterTag] = useState('');
  const [filterSection, setFilterSection] = useState('');

  useEffect(() => {
    api<{ name: string }>(`/api/v1/projects/${projectId}`)
      .then((p) => setProjectName(p.name))
      .catch(() => {});
  }, [projectId]);

  useEffect(() => {
    api<{ id: string; title: string }[]>(`/api/v1/projects/${projectId}/books`)
      .then((booksList) =>
        Promise.all(
          booksList.map((b) => {
            const params = new URLSearchParams();
            if (filterStatus) params.set('section_status', filterStatus);
            if (filterTag) params.set('tag', filterTag);
            if (filterSection) params.set('section_group', filterSection);
            const q = params.toString();
            return api<Book>(`/api/v1/projects/${projectId}/books/${b.id}${q ? `?${q}` : ''}`);
          })
        )
      )
      .then(setBooks)
      .catch(() => setBooks([]));
  }, [projectId, filterStatus, filterTag, filterSection]);

  const allChapters = books.flatMap((b) => b.chapters.map((c) => ({ ...c, bookTitle: b.title, bookId: b.id })));
  const allTags = [...new Set(allChapters.flatMap((c) => c.tags || []))].sort();
  const allSections = [...new Set(allChapters.map((c) => c.section_group).filter(Boolean))].sort() as string[];

  return (
    <div className="p-6 lg:p-8 max-w-6xl">
      <PageHeader
        title="Project management"
        description="Storyboard, timeline, and organization"
        backHref={`/dashboard/projects/${projectId}`}
        backLabel="Back to project"
      />

      <div className="flex flex-wrap gap-4 mb-6">
        <div className="flex gap-2">
          <Button
            variant={view === 'list' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setView('list')}
          >
            <List className="h-4 w-4 mr-1" />
            List
          </Button>
          <Button
            variant={view === 'storyboard' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setView('storyboard')}
          >
            <LayoutGrid className="h-4 w-4 mr-1" />
            Storyboard
          </Button>
          <Button
            variant={view === 'timeline' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setView('timeline')}
          >
            <Calendar className="h-4 w-4 mr-1" />
            Timeline
          </Button>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="rounded-md border border-input bg-background px-3 py-1.5 text-sm"
          >
            <option value="">All labels</option>
            <option value="draft">Draft</option>
            <option value="revising">Revising</option>
            <option value="review">Review</option>
            <option value="done">Done</option>
          </select>
          <select
            value={filterSection}
            onChange={(e) => setFilterSection(e.target.value)}
            className="rounded-md border border-input bg-background px-3 py-1.5 text-sm"
          >
            <option value="">All sections</option>
            {allSections.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <select
            value={filterTag}
            onChange={(e) => setFilterTag(e.target.value)}
            className="rounded-md border border-input bg-background px-3 py-1.5 text-sm"
          >
            <option value="">All tags</option>
            {allTags.map((t) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {view === 'list' && (
        <div className="space-y-4">
          {books.map((book) => (
            <Card key={book.id} variant="soft">
              <CardHeader>
                <Link href={`/dashboard/projects/${projectId}/books/${book.id}`} className="font-semibold hover:underline">
                  {book.title}
                </Link>
              </CardHeader>
              <CardContent>
                {book.chapters.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No chapters</p>
                ) : (
                  <ul className="space-y-2">
                    {book.chapters.map((ch) => (
                      <li key={ch.id} className="flex items-center gap-2 text-sm">
                        <span className="text-muted-foreground w-6">{ch.sort_order + 1}.</span>
                        <Link
                          href={`/dashboard/projects/${projectId}/books/${book.id}?chapter=${ch.id}`}
                          className="hover:underline truncate flex-1"
                        >
                          {ch.title}
                        </Link>
                        <span className="text-muted-foreground">{ch.word_count} words</span>
                        {ch.section_status && (
                          <span className={cn('text-[10px] px-1.5 py-0.5 rounded', STATUS_COLORS[ch.section_status] ?? STATUS_COLORS.draft)}>
                            {STATUS_LABELS[ch.section_status] ?? ch.section_status}
                          </span>
                        )}
                        {(ch.tags?.length ?? 0) > 0 && (
                          <span className="flex gap-1">
                            {ch.tags?.map((t) => (
                              <Tag key={t} className="h-3 w-3 text-muted-foreground" />
                            ))}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {view === 'storyboard' && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {allChapters.map((ch) => (
            <Link key={ch.id} href={`/dashboard/projects/${projectId}/books/${ch.bookId}?chapter=${ch.id}`}>
              <Card variant="soft" className="h-full hover:border-primary/30 transition-colors cursor-pointer">
                <CardContent className="p-4">
                  <p className="text-xs text-muted-foreground mb-1">{ch.bookTitle}</p>
                  <h4 className="font-medium line-clamp-2">{ch.title}</h4>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {ch.section_status && (
                      <span className={cn('text-[10px] px-1.5 py-0.5 rounded', STATUS_COLORS[ch.section_status] ?? STATUS_COLORS.draft)}>
                        {STATUS_LABELS[ch.section_status] ?? ch.section_status}
                      </span>
                    )}
                    {ch.section_group && (
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted">{ch.section_group}</span>
                    )}
                    {(ch.tags?.length ?? 0) > 0 && (
                      <span className="text-[10px] text-muted-foreground">{ch.tags?.join(', ')}</span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">{ch.word_count} words</p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      {view === 'timeline' && (
        <div className="space-y-6">
          {books.map((book) => (
            <Card key={book.id} variant="soft">
              <CardHeader>
                <Link href={`/dashboard/projects/${projectId}/books/${book.id}`} className="font-semibold hover:underline flex items-center gap-2">
                  <BookOpen className="h-4 w-4" />
                  {book.title}
                </Link>
              </CardHeader>
              <CardContent>
                {book.chapters.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No chapters</p>
                ) : (
                  <div className="relative pl-6 border-l-2 border-muted">
                    {book.chapters.map((ch, i) => (
                      <div key={ch.id} className="relative pb-6 last:pb-0">
                        <div className="absolute -left-6 top-1.5 w-3 h-3 rounded-full bg-primary" />
                        <Link
                          href={`/dashboard/projects/${projectId}/books/${book.id}?chapter=${ch.id}`}
                          className="block hover:underline"
                        >
                          <span className="text-muted-foreground text-sm">{i + 1}.</span>
                          <span className="font-medium ml-1">{ch.title}</span>
                        </Link>
                        <div className="flex gap-2 mt-1 text-xs text-muted-foreground">
                          {ch.section_status && (
                            <span className={cn('px-1.5 py-0.5 rounded', STATUS_COLORS[ch.section_status] ?? STATUS_COLORS.draft)}>
                              {STATUS_LABELS[ch.section_status] ?? ch.section_status}
                            </span>
                          )}
                          {ch.section_group && <span>{ch.section_group}</span>}
                          <span>{ch.word_count} words</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {allChapters.length === 0 && (
        <Card variant="soft" className="p-12 text-center">
          <p className="text-muted-foreground">No chapters match your filters.</p>
          <Button variant="outline" className="mt-4" onClick={() => { setFilterStatus(''); setFilterTag(''); setFilterSection(''); }}>
            Clear filters
          </Button>
        </Card>
      )}
    </div>
  );
}
