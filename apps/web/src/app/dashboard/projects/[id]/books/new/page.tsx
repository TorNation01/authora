'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
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

const POV_OPTIONS = ['First person', 'Third limited', 'Third omniscient', 'Second person', 'Multiple POV'];
const TENSE_OPTIONS = ['Past', 'Present'];
const RATINGS = ['Clean', 'PG-13', 'Mature'];

export default function NewBookPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const [title, setTitle] = useState('');
  const [type, setType] = useState<'fiction' | 'nonfiction'>('fiction');
  const [genre, setGenre] = useState('');
  const [premise, setPremise] = useState('');
  const [hook, setHook] = useState('');
  const [pov, setPov] = useState('Third limited');
  const [tense, setTense] = useState('Past');
  const [audience, setAudience] = useState('');
  const [tone, setTone] = useState('');
  const [rating, setRating] = useState('PG-13');
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

      // Seed the bible with the answers given here so nothing is typed twice.
      const sections: Record<string, Record<string, unknown>> = {
        book_details: {
          title,
          genre: genre || '',
          target_audience: audience,
          content_rating: rating,
        },
        story_foundation: {
          premise,
          reader_hook: hook,
        },
        tone_and_voice: {
          overall_tone: tone,
        },
      };
      if (type === 'fiction') {
        sections.narrative_format = { pov, tense };
      }
      try {
        await api(`/api/v1/projects/${projectId}/books/${book.id}/bible`, {
          method: 'PATCH',
          body: JSON.stringify({ sections }),
        });
      } catch {
        // The book exists; a failed seed must not block creation.
      }

      toast({ title: 'Book created', description: 'The bible is ready for the rest of the questions.' });
      router.push(`/dashboard/projects/${projectId}/books/${book.id}/bible`);
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
    <div className="p-6 lg:p-8 max-w-2xl">
      <PageHeader
        title="New book"
        description="Six answers now save you a hundred later. The rest of the bible waits inside."
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

            <div className="space-y-5 border-t border-border pt-5">
              <div>
                <h3 className="font-serif text-base font-semibold">The story in brief</h3>
                <p className="text-sm text-muted-foreground">
                  If these are wrong, every chapter written from them is wrong too. Rough answers
                  beat blank ones.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="premise">What is this book about?</Label>
                <Textarea
                  id="premise"
                  rows={3}
                  placeholder="Who wants what, and what stands in their way."
                  value={premise}
                  onChange={(e) => setPremise(e.target.value)}
                />
                <p className="text-xs text-muted-foreground">
                  Two or three sentences: the person, the want, the obstacle.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="hook">What makes a reader keep turning pages?</Label>
                <Textarea
                  id="hook"
                  rows={2}
                  placeholder="The question the first page plants that only the last page answers."
                  value={hook}
                  onChange={(e) => setHook(e.target.value)}
                />
              </div>

              {type === 'fiction' && (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2">
                    <Label>Point of view</Label>
                    <Select value={pov} onValueChange={setPov}>
                      <SelectTrigger className="h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {POV_OPTIONS.map((o) => (
                          <SelectItem key={o} value={o}>
                            {o}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Tense</Label>
                    <Select value={tense} onValueChange={setTense}>
                      <SelectTrigger className="h-11">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {TENSE_OPTIONS.map((o) => (
                          <SelectItem key={o} value={o}>
                            {o}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="audience">Who is it for?</Label>
                <Input
                  id="audience"
                  placeholder="e.g. adult readers of literary thrillers"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  className="h-11"
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="tone">Tone</Label>
                  <Input
                    id="tone"
                    placeholder="Dark, wry, hopeful…"
                    value={tone}
                    onChange={(e) => setTone(e.target.value)}
                    className="h-11"
                  />
                </div>
                <div className="space-y-2">
                  <Label>Content rating</Label>
                  <Select value={rating} onValueChange={setRating}>
                    <SelectTrigger className="h-11">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {RATINGS.map((o) => (
                        <SelectItem key={o} value={o}>
                          {o}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create & open the bible'}
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
