'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { PageHeader } from '@/components/layout/PageHeader';
import { BookOpen, BookMarked } from 'lucide-react';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import { FICTION_GENRES } from '@authora/shared';

export default function NewBookPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [title, setTitle] = useState('');
  const [type, setType] = useState<'fiction' | 'nonfiction'>('fiction');
  const [genre, setGenre] = useState('');
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const book = await api<{ id: string }>(
        `/api/v1/projects/${projectId}/books`,
        {
          method: 'POST',
          body: JSON.stringify({
            title,
            type,
            genre: genre || undefined,
            planner_data: {},
          }),
        }
      );
      toast({ title: 'Book created' });
      router.push(`/dashboard/projects/${projectId}/books/${book.id}/plan`);
    } catch (err) {
      toast({
        title: 'Failed to create book',
        description: err instanceof Error ? err.message : 'Try again',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="p-6 lg:p-8 max-w-xl">
      <PageHeader
        title="New book"
        description="We'll tailor the planning experience to your book type."
        backHref={`/dashboard/projects/${projectId}`}
        backLabel="Project"
      />

      <Card variant="sanctuary">
        <CardHeader>
          <CardTitle className="font-serif">Book details</CardTitle>
          <CardDescription>Choose fiction or non-fiction—your planner will adapt.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                placeholder="My Amazing Novel"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="h-11"
              />
            </div>
            <div className="space-y-2">
              <Label>Type</Label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setType('fiction')}
                  className={`flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-colors ${
                    type === 'fiction'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-border hover:border-muted-foreground/30'
                  }`}
                >
                  <BookOpen className="h-8 w-8" />
                  <span className="font-medium">Fiction</span>
                  <span className="text-xs text-muted-foreground">Novels, stories</span>
                </button>
                <button
                  type="button"
                  onClick={() => setType('nonfiction')}
                  className={`flex flex-col items-center gap-2 rounded-lg border-2 p-4 transition-colors ${
                    type === 'nonfiction'
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-border hover:border-muted-foreground/30'
                  }`}
                >
                  <BookMarked className="h-8 w-8" />
                  <span className="font-medium">Non-fiction</span>
                  <span className="text-xs text-muted-foreground">How-to, memoir, business</span>
                </button>
              </div>
            </div>
            {type === 'fiction' && (
              <div className="space-y-2">
                <Label>Genre</Label>
                <Select value={genre} onValueChange={setGenre}>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select genre (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    {FICTION_GENRES.map((g) => (
                      <SelectItem key={g} value={g}>
                        {g}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            <div className="flex gap-3">
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create & plan'}
              </Button>
              <Button variant="outline" asChild>
                <Link href={`/dashboard/projects/${projectId}`}>Cancel</Link>
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
