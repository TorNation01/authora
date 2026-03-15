'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/layout/PageHeader';
import { Progress } from '@/components/ui/progress';
import { api } from '@/lib/api';
import { useToast } from '@/hooks/use-toast';
import {
  BookOpen,
  Users,
  GitBranch,
  Globe,
  Map,
  LayoutList,
  FileText,
  ListChecks,
  Plus,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';
import { FICTION_GENRES, FICTION_TONES, WORLD_CATEGORIES, RELATIONSHIP_TYPES } from '@authora/shared';

interface Book {
  id: string;
  title: string;
  type: string;
  genre?: string;
  planner_data?: Record<string, unknown>;
}

const TABS = [
  { id: 'premise', label: 'Premise & Genre', icon: BookOpen },
  { id: 'characters', label: 'Characters', icon: Users },
  { id: 'relationships', label: 'Relationships', icon: GitBranch },
  { id: 'world', label: 'Worldbuilding', icon: Globe },
  { id: 'plot', label: 'Plot Arcs', icon: Map },
  { id: 'scenes', label: 'Scene Cards', icon: LayoutList },
  { id: 'chapters', label: 'Chapter Planner', icon: FileText },
  { id: 'trackers', label: 'Trackers', icon: ListChecks },
];

export default function PlanRouterPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const bookId = params.bookId as string;
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Book>(`/api/v1/projects/${projectId}/books/${bookId}`)
      .then(setBook)
      .catch(() => router.push('/dashboard'))
      .finally(() => setLoading(false));
  }, [projectId, bookId, router]);

  if (loading || !book) return <div className="p-8">Loading...</div>;

  if (book.type === 'fiction') {
    return <FictionWorkspace projectId={projectId} bookId={bookId} book={book} />;
  }
  return <NonfictionWorkspace projectId={projectId} bookId={bookId} book={book} />;
}

function FictionWorkspace({
  projectId,
  bookId,
  book,
}: {
  projectId: string;
  bookId: string;
  book: Book;
}) {
  const [activeTab, setActiveTab] = useState('premise');
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    api<Record<string, unknown>>(`/api/v1/projects/${projectId}/books/${bookId}/fiction/summary`)
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, [projectId, bookId, activeTab]);

  const workspace = summary?.workspace as Record<string, unknown> | undefined;
  const characters = (summary?.characters as Record<string, unknown>[]) || [];
  const relationships = (summary?.relationships as Record<string, unknown>[]) || [];
  const worldElements = (summary?.world_elements as Record<string, unknown>[]) || [];
  const plotArcs = (summary?.plot_arcs as Record<string, unknown>[]) || [];
  const scenes = (summary?.scenes as Record<string, unknown>[]) || [];
  const trackers = (summary?.trackers as Record<string, unknown>[]) || [];
  const chapterPlans = (summary?.chapter_plans as Record<string, unknown>[]) || [];

  const totalItems =
    (characters?.length || 0) +
    (relationships?.length || 0) +
    (worldElements?.length || 0) +
    (plotArcs?.length || 0) +
    (scenes?.length || 0);
  const progress = Math.min(100, Math.round((totalItems / 20) * 100));

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      <PageHeader
        title="Fiction workspace"
        description={`Plan "${book.title}" — premise, characters, world, plot, and more`}
        backHref={`/dashboard/projects/${projectId}/books/${bookId}`}
        backLabel="Book"
      />

      <Progress value={progress} showLabel className="mb-6" />

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {activeTab === 'premise' && (
        <PremiseTab projectId={projectId} bookId={bookId} workspace={workspace} book={book} />
      )}
      {activeTab === 'characters' && (
        <CharactersTab projectId={projectId} bookId={bookId} characters={characters} workspace={workspace} />
      )}
      {activeTab === 'relationships' && (
        <RelationshipsTab projectId={projectId} bookId={bookId} relationships={relationships} characters={characters} />
      )}
      {activeTab === 'world' && (
        <WorldTab projectId={projectId} bookId={bookId} worldElements={worldElements} />
      )}
      {activeTab === 'plot' && (
        <PlotTab projectId={projectId} bookId={bookId} plotArcs={plotArcs} />
      )}
      {activeTab === 'scenes' && (
        <ScenesTab projectId={projectId} bookId={bookId} scenes={scenes} characters={characters} />
      )}
      {activeTab === 'chapters' && (
        <ChaptersTab projectId={projectId} bookId={bookId} chapterPlans={chapterPlans} />
      )}
      {activeTab === 'trackers' && (
        <TrackersTab projectId={projectId} bookId={bookId} trackers={trackers} />
      )}

      <div className="mt-8 flex gap-3">
        <Button variant="soft" asChild>
          <Link href={`/dashboard/projects/${projectId}/books/${bookId}`}>
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to writing
          </Link>
        </Button>
        <Button asChild>
          <Link href={`/dashboard/projects/${projectId}/books/${bookId}`}>
            Start writing
            <ChevronRight className="h-4 w-4 ml-2" />
          </Link>
        </Button>
      </div>
    </div>
  );
}

function PremiseTab({
  projectId,
  bookId,
  workspace,
  book,
}: {
  projectId: string;
  bookId: string;
  workspace?: Record<string, unknown>;
  book: Book;
}) {
  const [premise, setPremise] = useState((workspace?.premise as string) || (book.planner_data?.premise as string) || '');
  const [genre, setGenre] = useState((workspace?.genre as string) || book.genre || '');
  const [tone, setTone] = useState((workspace?.tone as string) || '');
  const [themes, setThemes] = useState((workspace?.themes as string[])?.join(', ') || '');
  const [pacingNotes, setPacingNotes] = useState((workspace?.pacing_notes as string) || '');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleSave() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/workspace`, {
        method: 'PATCH',
        body: JSON.stringify({
          premise,
          genre: genre || null,
          tone: tone || null,
          themes: themes ? themes.split(',').map((t) => t.trim()).filter(Boolean) : null,
          pacing_notes: pacingNotes || null,
        }),
      });
      toast({ title: 'Saved' });
    } catch {
      toast({ title: 'Failed to save', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Premise & genre</CardTitle>
        <CardDescription>Core story setup and tone.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label htmlFor="premise">Premise</Label>
          <textarea
            id="premise"
            value={premise}
            onChange={(e) => setPremise(e.target.value)}
            placeholder="e.g. A young detective must solve a murder in a town where everyone has something to hide..."
            className="min-h-[120px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm font-serif placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="genre">Genre</Label>
            <select
              id="genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Select genre</option>
              {FICTION_GENRES.map((g) => (
                <option key={g} value={g}>{g}</option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="tone">Tone</Label>
            <select
              id="tone"
              value={tone}
              onChange={(e) => setTone(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Select tone</option>
              {FICTION_TONES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="themes">Themes (comma-separated)</Label>
          <Input
            id="themes"
            value={themes}
            onChange={(e) => setThemes(e.target.value)}
            placeholder="e.g. identity, redemption, sacrifice"
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="pacing">Pacing notes</Label>
          <textarea
            id="pacing"
            value={pacingNotes}
            onChange={(e) => setPacingNotes(e.target.value)}
            placeholder="e.g. Slow start, build to mid-point climax, fast finale..."
            className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
          />
        </div>
        <Button onClick={handleSave} disabled={saving}>
          {saving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
          Save
        </Button>
      </CardContent>
    </Card>
  );
}

function CharactersTab({
  projectId,
  bookId,
  characters,
  workspace,
}: {
  projectId: string;
  bookId: string;
  characters: Record<string, unknown>[];
  workspace?: Record<string, unknown>;
}) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [role, setRole] = useState('supporting');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!name.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/characters`, {
        method: 'POST',
        body: JSON.stringify({ name: name.trim(), role, description: description || null }),
      });
      toast({ title: 'Character added' });
      setName('');
      setDescription('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed to add', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Character database</CardTitle>
        <CardDescription>Protagonist, antagonist, and supporting characters.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          {characters.map((c) => (
            <div key={String(c.id)} className="flex items-center justify-between rounded-lg border p-4">
              <div>
                <p className="font-medium">{String(c.name)}</p>
                <p className="text-sm text-muted-foreground capitalize">{String(c.role)}</p>
                {c.description && <p className="text-sm mt-1">{String(c.description).slice(0, 100)}...</p>}
              </div>
            </div>
          ))}
        </div>
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New character</Label>
            <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="protagonist">Protagonist</option>
              <option value="antagonist">Antagonist</option>
              <option value="supporting">Supporting</option>
            </select>
            <textarea
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add character
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function RelationshipsTab({
  projectId,
  bookId,
  relationships,
  characters,
}: {
  projectId: string;
  bookId: string;
  relationships: Record<string, unknown>[];
  characters: Record<string, unknown>[];
}) {
  const [showForm, setShowForm] = useState(false);
  const [charA, setCharA] = useState('');
  const [charB, setCharB] = useState('');
  const [relType, setRelType] = useState('Friend');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!charA || !charB) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/relationships`, {
        method: 'POST',
        body: JSON.stringify({
          character_a_id: charA,
          character_b_id: charB,
          relationship_type: relType,
          description: description || null,
        }),
      });
      toast({ title: 'Relationship added' });
      setCharA('');
      setCharB('');
      setDescription('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed to add', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  const getCharName = (id: string) => characters.find((c) => c.id === id)?.name ?? id;

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Relationship mapping</CardTitle>
        <CardDescription>How characters connect and conflict.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          {relationships.map((r) => (
            <div key={String(r.id)} className="rounded-lg border p-4">
              <p className="font-medium">
                {getCharName(String(r.character_a_id))} ↔ {getCharName(String(r.character_b_id))}
              </p>
              <p className="text-sm text-muted-foreground">{String(r.relationship_type)}</p>
              {r.description && <p className="text-sm mt-1">{String(r.description)}</p>}
            </div>
          ))}
        </div>
        {showForm && characters.length >= 2 ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New relationship</Label>
            <select
              value={charA}
              onChange={(e) => setCharA(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Select character</option>
              {characters.map((c) => (
                <option key={String(c.id)} value={String(c.id)}>{String(c.name)}</option>
              ))}
            </select>
            <select
              value={charB}
              onChange={(e) => setCharB(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Select character</option>
              {characters.map((c) => (
                <option key={String(c.id)} value={String(c.id)}>{String(c.name)}</option>
              ))}
            </select>
            <select
              value={relType}
              onChange={(e) => setRelType(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {RELATIONSHIP_TYPES.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
            <textarea
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[60px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)} disabled={characters.length < 2}>
            <Plus className="h-4 w-4 mr-2" />
            Add relationship
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function WorldTab({
  projectId,
  bookId,
  worldElements,
}: {
  projectId: string;
  bookId: string;
  worldElements: Record<string, unknown>[];
}) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [category, setCategory] = useState('Location');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!name.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/world`, {
        method: 'POST',
        body: JSON.stringify({ name: name.trim(), category, description: description || null }),
      });
      toast({ title: 'World element added' });
      setName('');
      setDescription('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed to add', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Worldbuilding</CardTitle>
        <CardDescription>Locations, cultures, magic, technology, etc.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          {worldElements.map((w) => (
            <div key={String(w.id)} className="rounded-lg border p-4">
              <p className="font-medium">{String(w.name)}</p>
              <p className="text-sm text-muted-foreground">{String(w.category)}</p>
              {w.description && <p className="text-sm mt-1">{String(w.description)}</p>}
            </div>
          ))}
        </div>
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New world element</Label>
            <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {WORLD_CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
            <textarea
              placeholder="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add world element
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function PlotTab({
  projectId,
  bookId,
  plotArcs,
}: {
  projectId: string;
  bookId: string;
  plotArcs: Record<string, unknown>[];
}) {
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [structure, setStructure] = useState('three_act');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!name.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/arcs`, {
        method: 'POST',
        body: JSON.stringify({ name: name.trim(), structure }),
      });
      toast({ title: 'Plot arc added' });
      setName('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed to add', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Plot arcs</CardTitle>
        <CardDescription>Story structure and beats.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          {plotArcs.map((a) => (
            <div key={String(a.id)} className="rounded-lg border p-4">
              <p className="font-medium">{String(a.name)}</p>
              <p className="text-sm text-muted-foreground">{String(a.structure)}</p>
            </div>
          ))}
        </div>
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New plot arc</Label>
            <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <select
              value={structure}
              onChange={(e) => setStructure(e.target.value)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="three_act">Three-act</option>
              <option value="hero_journey">Hero&apos;s journey</option>
              <option value="save_the_cat">Save the cat</option>
              <option value="seven_point">Seven-point</option>
              <option value="custom">Custom</option>
            </select>
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add plot arc
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function ScenesTab({
  projectId,
  bookId,
  scenes,
  characters,
}: {
  projectId: string;
  bookId: string;
  scenes: Record<string, unknown>[];
  characters: Record<string, unknown>[];
}) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [beat, setBeat] = useState('');
  const [conflictLevel, setConflictLevel] = useState<number | ''>('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/scenes`, {
        method: 'POST',
        body: JSON.stringify({
          title: title.trim(),
          summary: summary || null,
          beat: beat || null,
          conflict_level: conflictLevel ? Number(conflictLevel) : null,
        }),
      });
      toast({ title: 'Scene added' });
      setTitle('');
      setSummary('');
      setBeat('');
      setConflictLevel('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed to add', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Scene cards</CardTitle>
        <CardDescription>Plan scenes with summary, beat, and conflict level.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2">
          {scenes.map((s) => (
            <div key={String(s.id)} className="rounded-lg border p-4">
              <p className="font-medium">{String(s.title)}</p>
              {s.beat && <p className="text-xs text-muted-foreground">{String(s.beat)}</p>}
              {s.conflict_level && <p className="text-xs">Conflict: {String(s.conflict_level)}/5</p>}
              {s.summary && <p className="text-sm mt-1">{String(s.summary).slice(0, 80)}...</p>}
            </div>
          ))}
        </div>
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New scene</Label>
            <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <Input placeholder="Beat (e.g. inciting incident)" value={beat} onChange={(e) => setBeat(e.target.value)} />
            <select
              value={conflictLevel}
              onChange={(e) => setConflictLevel(e.target.value ? Number(e.target.value) : '')}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="">Conflict level</option>
              {[1, 2, 3, 4, 5].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
            <textarea
              placeholder="Summary"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add scene
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function ChaptersTab({
  projectId,
  bookId,
  chapterPlans,
}: {
  projectId: string;
  bookId: string;
  chapterPlans: Record<string, unknown>[];
}) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/chapter-plans`, {
        method: 'POST',
        body: JSON.stringify({ title: title.trim(), summary: summary || null }),
      });
      toast({ title: 'Chapter plan added' });
      setTitle('');
      setSummary('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed to add', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Chapter planner</CardTitle>
        <CardDescription>Plan chapters with summary and goals.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          {chapterPlans.map((p, i) => (
            <div key={String(p.id)} className="rounded-lg border p-4">
              <p className="font-medium">Ch. {i + 1}: {String(p.title)}</p>
              {p.summary && <p className="text-sm mt-1">{String(p.summary)}</p>}
            </div>
          ))}
        </div>
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New chapter plan</Label>
            <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea
              placeholder="Summary"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add chapter plan
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

function TrackersTab({
  projectId,
  bookId,
  trackers,
}: {
  projectId: string;
  bookId: string;
  trackers: Record<string, unknown>[];
}) {
  const [showForm, setShowForm] = useState(false);
  const [type, setType] = useState<'continuity' | 'foreshadowing' | 'unresolved'>('continuity');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/fiction/trackers`, {
        method: 'POST',
        body: JSON.stringify({ type, title: title.trim(), content: content || null }),
      });
      toast({ title: 'Tracker added' });
      setTitle('');
      setContent('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed to add', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  const byType = { continuity: [] as Record<string, unknown>[], foreshadowing: [] as Record<string, unknown>[], unresolved: [] as Record<string, unknown>[] };
  trackers.forEach((t) => {
    const ttype = t.type as keyof typeof byType;
    if (byType[ttype]) byType[ttype].push(t);
  });

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Trackers</CardTitle>
        <CardDescription>Continuity notes, foreshadowing, unresolved threads.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <h4 className="font-medium mb-2">Continuity</h4>
            {byType.continuity.map((t) => (
              <div key={String(t.id)} className="rounded border p-2 mb-2 text-sm">
                <p className="font-medium">{String(t.title)}</p>
                {t.content && <p className="text-muted-foreground">{String(t.content).slice(0, 60)}...</p>}
              </div>
            ))}
          </div>
          <div>
            <h4 className="font-medium mb-2">Foreshadowing</h4>
            {byType.foreshadowing.map((t) => (
              <div key={String(t.id)} className="rounded border p-2 mb-2 text-sm">
                <p className="font-medium">{String(t.title)}</p>
                {t.content && <p className="text-muted-foreground">{String(t.content).slice(0, 60)}...</p>}
              </div>
            ))}
          </div>
          <div>
            <h4 className="font-medium mb-2">Unresolved</h4>
            {byType.unresolved.map((t) => (
              <div key={String(t.id)} className="rounded border p-2 mb-2 text-sm">
                <p className="font-medium">{String(t.title)}</p>
                {t.content && <p className="text-muted-foreground">{String(t.content).slice(0, 60)}...</p>}
              </div>
            ))}
          </div>
        </div>
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New tracker</Label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as typeof type)}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              <option value="continuity">Continuity</option>
              <option value="foreshadowing">Foreshadowing</option>
              <option value="unresolved">Unresolved</option>
            </select>
            <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea
              placeholder="Content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm"
            />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add tracker
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

const NF_TABS = [
  { id: 'core', label: 'Core Message', icon: BookOpen },
  { id: 'audience', label: 'Target Audience', icon: Users },
  { id: 'transformation', label: 'Transformation', icon: Map },
  { id: 'chapters', label: 'Chapter Framework', icon: FileText },
  { id: 'arguments', label: 'Arguments', icon: GitBranch },
  { id: 'examples', label: 'Examples', icon: LayoutList },
  { id: 'case-studies', label: 'Case Studies', icon: ListChecks },
  { id: 'stories', label: 'Story Insertions', icon: BookOpen },
  { id: 'worksheets', label: 'Worksheets', icon: ListChecks },
  { id: 'research', label: 'Research Notes', icon: FileText },
  { id: 'citations', label: 'Citations', icon: FileText },
  { id: 'authority', label: 'Authority', icon: Users },
  { id: 'summary', label: 'Summary & Actions', icon: ListChecks },
];

function NonfictionWorkspace({
  projectId,
  bookId,
  book,
}: {
  projectId: string;
  bookId: string;
  book: Book;
}) {
  const [activeTab, setActiveTab] = useState('core');
  const [summary, setSummary] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    api<Record<string, unknown>>(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/summary`)
      .then(setSummary)
      .catch(() => setSummary(null))
      .finally(() => setLoading(false));
  }, [projectId, bookId, activeTab]);

  const workspace = summary?.workspace as Record<string, unknown> | undefined;
  const audiences = (summary?.audiences as Record<string, unknown>[]) || [];
  const transformations = (summary?.transformations as Record<string, unknown>[]) || [];
  const chapterPlans = (summary?.chapter_plans as Record<string, unknown>[]) || [];
  const arguments_ = (summary?.arguments as Record<string, unknown>[]) || [];
  const examples = (summary?.examples as Record<string, unknown>[]) || [];
  const caseStudies = (summary?.case_studies as Record<string, unknown>[]) || [];
  const storyInsertions = (summary?.story_insertions as Record<string, unknown>[]) || [];
  const worksheets = (summary?.worksheets as Record<string, unknown>[]) || [];
  const researchNotes = (summary?.research_notes as Record<string, unknown>[]) || [];
  const citations = (summary?.citations as Record<string, unknown>[]) || [];
  const authority = (summary?.authority as Record<string, unknown>[]) || [];
  const summaryActions = (summary?.summary_actions as Record<string, unknown>[]) || [];

  const totalItems =
    audiences.length + transformations.length + chapterPlans.length + arguments_.length +
    examples.length + caseStudies.length + storyInsertions.length + worksheets.length +
    researchNotes.length + citations.length + authority.length + summaryActions.length;
  const progress = Math.min(100, Math.round((totalItems / 15) * 100));

  return (
    <div className="p-6 lg:p-8 max-w-5xl">
      <PageHeader
        title="Non-fiction workspace"
        description={`Plan "${book.title}" — message, audience, structure, and more`}
        backHref={`/dashboard/projects/${projectId}/books/${bookId}`}
        backLabel="Book"
      />

      <Progress value={progress} showLabel className="mb-6" />

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {NF_TABS.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                activeTab === tab.id ? 'bg-primary text-primary-foreground' : 'bg-muted hover:bg-muted/80'
              }`}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {activeTab === 'core' && <NFCoreTab projectId={projectId} bookId={bookId} workspace={workspace} book={book} />}
      {activeTab === 'audience' && <NFAudienceTab projectId={projectId} bookId={bookId} audiences={audiences} />}
      {activeTab === 'transformation' && <NFTransformationTab projectId={projectId} bookId={bookId} transformations={transformations} />}
      {activeTab === 'chapters' && <NFChaptersTab projectId={projectId} bookId={bookId} chapterPlans={chapterPlans} />}
      {activeTab === 'arguments' && <NFArgumentsTab projectId={projectId} bookId={bookId} arguments={arguments_} />}
      {activeTab === 'examples' && <NFExamplesTab projectId={projectId} bookId={bookId} examples={examples} />}
      {activeTab === 'case-studies' && <NFCaseStudiesTab projectId={projectId} bookId={bookId} caseStudies={caseStudies} />}
      {activeTab === 'stories' && <NFStoriesTab projectId={projectId} bookId={bookId} storyInsertions={storyInsertions} />}
      {activeTab === 'worksheets' && <NFWorksheetsTab projectId={projectId} bookId={bookId} worksheets={worksheets} />}
      {activeTab === 'research' && <NFResearchTab projectId={projectId} bookId={bookId} researchNotes={researchNotes} />}
      {activeTab === 'citations' && <NFCitationsTab projectId={projectId} bookId={bookId} citations={citations} />}
      {activeTab === 'authority' && <NFAuthorityTab projectId={projectId} bookId={bookId} authority={authority} />}
      {activeTab === 'summary' && <NFSummaryTab projectId={projectId} bookId={bookId} summaryActions={summaryActions} />}

      <div className="mt-8 flex gap-3">
        <Button variant="soft" asChild>
          <Link href={`/dashboard/projects/${projectId}/books/${bookId}`}>
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back to writing
          </Link>
        </Button>
        <Button asChild>
          <Link href={`/dashboard/projects/${projectId}/books/${bookId}`}>
            Start writing
            <ChevronRight className="h-4 w-4 ml-2" />
          </Link>
        </Button>
      </div>
    </div>
  );
}

function NFCoreTab({ projectId, bookId, workspace, book }: { projectId: string; bookId: string; workspace?: Record<string, unknown>; book: Book }) {
  const [coreMessage, setCoreMessage] = useState((workspace?.core_message as string) || (book.planner_data?.core_message as string) || '');
  const [readerOutcome, setReaderOutcome] = useState((workspace?.reader_outcome as string) || '');
  const [readerPromise, setReaderPromise] = useState((workspace?.reader_promise as string) || '');
  const [topic, setTopic] = useState((workspace?.topic as string) || (book.planner_data?.topic as string) || '');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleSave() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/workspace`, {
        method: 'PATCH',
        body: JSON.stringify({ core_message: coreMessage, reader_outcome: readerOutcome, reader_promise: readerPromise, topic }),
      });
      toast({ title: 'Saved' });
    } catch {
      toast({ title: 'Failed to save', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Core message & reader promise</CardTitle>
        <CardDescription>Your central message and what readers will gain.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <Label>Core message</Label>
          <textarea value={coreMessage} onChange={(e) => setCoreMessage(e.target.value)} placeholder="The one thing you want readers to take away..." className="min-h-[100px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" />
        </div>
        <div className="space-y-2">
          <Label>Reader outcome</Label>
          <textarea value={readerOutcome} onChange={(e) => setReaderOutcome(e.target.value)} placeholder="What will readers be able to do or understand after reading?" className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" />
        </div>
        <div className="space-y-2">
          <Label>Reader promise</Label>
          <textarea value={readerPromise} onChange={(e) => setReaderPromise(e.target.value)} placeholder="The transformation you promise..." className="min-h-[80px] w-full rounded-lg border border-input bg-background px-3 py-2 text-sm" />
        </div>
        <div className="space-y-2">
          <Label>Topic</Label>
          <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="e.g. Productivity for creatives" />
        </div>
        <Button onClick={handleSave} disabled={saving}>Save</Button>
      </CardContent>
    </Card>
  );
}

function NFAudienceTab({ projectId, bookId, audiences }: { projectId: string; bookId: string; audiences: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [demographics, setDemographics] = useState('');
  const [painPoints, setPainPoints] = useState('');
  const [goals, setGoals] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/audiences`, {
        method: 'POST',
        body: JSON.stringify({ demographics: demographics || null, pain_points: painPoints || null, goals: goals || null }),
      });
      toast({ title: 'Added' });
      setDemographics('');
      setPainPoints('');
      setGoals('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Target audience</CardTitle>
        <CardDescription>Who you&apos;re writing for and their needs.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {audiences.map((a) => (
          <div key={String(a.id)} className="rounded-lg border p-4">
            {a.demographics && <p><strong>Demographics:</strong> {String(a.demographics).slice(0, 150)}...</p>}
            {a.pain_points && <p><strong>Pain points:</strong> {String(a.pain_points).slice(0, 150)}...</p>}
            {a.goals && <p><strong>Goals:</strong> {String(a.goals).slice(0, 150)}...</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New audience profile</Label>
            <textarea placeholder="Demographics" value={demographics} onChange={(e) => setDemographics(e.target.value)} className="min-h-[60px] w-full rounded-lg border px-3 py-2 text-sm" />
            <textarea placeholder="Pain points" value={painPoints} onChange={(e) => setPainPoints(e.target.value)} className="min-h-[60px] w-full rounded-lg border px-3 py-2 text-sm" />
            <textarea placeholder="Goals" value={goals} onChange={(e) => setGoals(e.target.value)} className="min-h-[60px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add audience profile</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFTransformationTab({ projectId, bookId, transformations }: { projectId: string; bookId: string; transformations: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [before, setBefore] = useState('');
  const [after, setAfter] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/transformations`, {
        method: 'POST',
        body: JSON.stringify({ before_state: before || null, after_state: after || null }),
      });
      toast({ title: 'Added' });
      setBefore('');
      setAfter('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Transformation framework</CardTitle>
        <CardDescription>Before and after state for your readers.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {transformations.map((t) => (
          <div key={String(t.id)} className="rounded-lg border p-4 grid sm:grid-cols-2 gap-4">
            <div><strong>Before:</strong> {String(t.before_state || '').slice(0, 100)}...</div>
            <div><strong>After:</strong> {String(t.after_state || '').slice(0, 100)}...</div>
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Label>New transformation</Label>
            <textarea placeholder="Before state" value={before} onChange={(e) => setBefore(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <textarea placeholder="After state" value={after} onChange={(e) => setAfter(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add transformation</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFChaptersTab({ projectId, bookId, chapterPlans }: { projectId: string; bookId: string; chapterPlans: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [summary, setSummary] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/chapter-plans`, {
        method: 'POST',
        body: JSON.stringify({ title: title.trim(), summary: summary || null }),
      });
      toast({ title: 'Added' });
      setTitle('');
      setSummary('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Chapter framework</CardTitle>
        <CardDescription>Plan each chapter with summary and key points.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {chapterPlans.map((p, i) => (
          <div key={String(p.id)} className="rounded-lg border p-4">
            <p className="font-medium">Ch. {i + 1}: {String(p.title)}</p>
            {p.summary && <p className="text-sm mt-1">{String(p.summary)}</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Input placeholder="Chapter title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea placeholder="Summary" value={summary} onChange={(e) => setSummary(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add chapter plan</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFArgumentsTab({ projectId, bookId, arguments: args }: { projectId: string; bookId: string; arguments: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [mainArg, setMainArg] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/arguments`, {
        method: 'POST',
        body: JSON.stringify({ main_argument: mainArg || null }),
      });
      toast({ title: 'Added' });
      setMainArg('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Argument structure</CardTitle>
        <CardDescription>Main arguments and supporting points.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {args.map((a) => (
          <div key={String(a.id)} className="rounded-lg border p-4">
            <p>{String(a.main_argument || '').slice(0, 200)}...</p>
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <textarea placeholder="Main argument" value={mainArg} onChange={(e) => setMainArg(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add argument</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFExamplesTab({ projectId, bookId, examples }: { projectId: string; bookId: string; examples: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/examples`, {
        method: 'POST',
        body: JSON.stringify({ title: title.trim(), description: description || null }),
      });
      toast({ title: 'Added' });
      setTitle('');
      setDescription('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Supporting examples</CardTitle>
        <CardDescription>Examples that illustrate your points.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {examples.map((e) => (
          <div key={String(e.id)} className="rounded-lg border p-4">
            <p className="font-medium">{String(e.title)}</p>
            {e.description && <p className="text-sm mt-1">{String(e.description).slice(0, 100)}...</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add example</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFCaseStudiesTab({ projectId, bookId, caseStudies }: { projectId: string; bookId: string; caseStudies: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [scenario, setScenario] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/case-studies`, {
        method: 'POST',
        body: JSON.stringify({ title: title.trim(), scenario: scenario || null }),
      });
      toast({ title: 'Added' });
      setTitle('');
      setScenario('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Case studies</CardTitle>
        <CardDescription>Real-world scenarios and outcomes.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {caseStudies.map((c) => (
          <div key={String(c.id)} className="rounded-lg border p-4">
            <p className="font-medium">{String(c.title)}</p>
            {c.scenario && <p className="text-sm mt-1">{String(c.scenario).slice(0, 100)}...</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <textarea placeholder="Scenario" value={scenario} onChange={(e) => setScenario(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add case study</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFStoriesTab({ projectId, bookId, storyInsertions }: { projectId: string; bookId: string; storyInsertions: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [content, setContent] = useState('');
  const [purpose, setPurpose] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/story-insertions`, {
        method: 'POST',
        body: JSON.stringify({ story_content: content || null, purpose: purpose || null }),
      });
      toast({ title: 'Added' });
      setContent('');
      setPurpose('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Story/example insertions</CardTitle>
        <CardDescription>Stories and examples to weave into chapters.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {storyInsertions.map((s) => (
          <div key={String(s.id)} className="rounded-lg border p-4">
            {s.purpose && <p className="font-medium">{String(s.purpose)}</p>}
            {s.story_content && <p className="text-sm mt-1">{String(s.story_content).slice(0, 100)}...</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Input placeholder="Purpose" value={purpose} onChange={(e) => setPurpose(e.target.value)} />
            <textarea placeholder="Story content" value={content} onChange={(e) => setContent(e.target.value)} className="min-h-[100px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add story</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFWorksheetsTab({ projectId, bookId, worksheets }: { projectId: string; bookId: string; worksheets: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/worksheets`, {
        method: 'POST',
        body: JSON.stringify({ title: title.trim(), items: [] }),
      });
      toast({ title: 'Added' });
      setTitle('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Worksheets & checklists</CardTitle>
        <CardDescription>Reader exercises and checklists.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {worksheets.map((w) => (
          <div key={String(w.id)} className="rounded-lg border p-4">
            <p className="font-medium">{String(w.title)}</p>
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add worksheet</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFResearchTab({ projectId, bookId, researchNotes }: { projectId: string; bookId: string; researchNotes: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [source, setSource] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!title.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/research-notes`, {
        method: 'POST',
        body: JSON.stringify({ title: title.trim(), content: content || null, source: source || null }),
      });
      toast({ title: 'Added' });
      setTitle('');
      setContent('');
      setSource('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Research notes</CardTitle>
        <CardDescription>Organize research and sources.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {researchNotes.map((r) => (
          <div key={String(r.id)} className="rounded-lg border p-4">
            <p className="font-medium">{String(r.title)}</p>
            {r.source && <p className="text-xs text-muted-foreground">{String(r.source)}</p>}
            {r.content && <p className="text-sm mt-1">{String(r.content).slice(0, 80)}...</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Input placeholder="Title" value={title} onChange={(e) => setTitle(e.target.value)} />
            <Input placeholder="Source" value={source} onChange={(e) => setSource(e.target.value)} />
            <textarea placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add research note</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFCitationsTab({ projectId, bookId, citations }: { projectId: string; bookId: string; citations: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [placeholderText, setPlaceholderText] = useState('');
  const [sourceHint, setSourceHint] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    if (!placeholderText.trim()) return;
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/citations`, {
        method: 'POST',
        body: JSON.stringify({ placeholder_text: placeholderText.trim(), source_hint: sourceHint || null }),
      });
      toast({ title: 'Added' });
      setPlaceholderText('');
      setSourceHint('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Citation placeholders</CardTitle>
        <CardDescription>Track citations to add later.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {citations.map((c) => (
          <div key={String(c.id)} className="rounded-lg border p-4">
            <p>{String(c.placeholder_text)}</p>
            {c.source_hint && <p className="text-xs text-muted-foreground">{String(c.source_hint)}</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <Input placeholder="Placeholder text" value={placeholderText} onChange={(e) => setPlaceholderText(e.target.value)} />
            <Input placeholder="Source hint" value={sourceHint} onChange={(e) => setSourceHint(e.target.value)} />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add citation</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFAuthorityTab({ projectId, bookId, authority: auth }: { projectId: string; bookId: string; authority: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [credentials, setCredentials] = useState('');
  const [experience, setExperience] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    setSaving(true);
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/authority`, {
        method: 'POST',
        body: JSON.stringify({ credentials: credentials || null, experience: experience || null }),
      });
      toast({ title: 'Added' });
      setCredentials('');
      setExperience('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Authority builder</CardTitle>
        <CardDescription>Credentials, experience, testimonials.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {auth.map((a) => (
          <div key={String(a.id)} className="rounded-lg border p-4">
            {a.credentials && <p>{String(a.credentials).slice(0, 150)}...</p>}
            {a.experience && <p className="text-sm mt-1">{String(a.experience).slice(0, 100)}...</p>}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <textarea placeholder="Credentials" value={credentials} onChange={(e) => setCredentials(e.target.value)} className="min-h-[60px] w-full rounded-lg border px-3 py-2 text-sm" />
            <textarea placeholder="Experience" value={experience} onChange={(e) => setExperience(e.target.value)} className="min-h-[60px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add authority</Button>
        )}
      </CardContent>
    </Card>
  );
}

function NFSummaryTab({ projectId, bookId, summaryActions }: { projectId: string; bookId: string; summaryActions: Record<string, unknown>[] }) {
  const [showForm, setShowForm] = useState(false);
  const [summary, setSummary] = useState('');
  const [actionSteps, setActionSteps] = useState('');
  const [saving, setSaving] = useState(false);
  const { toast } = useToast();

  async function handleCreate() {
    setSaving(true);
    try {
      const steps = actionSteps ? actionSteps.split('\n').map((s) => s.trim()).filter(Boolean) : [];
      await api(`/api/v1/projects/${projectId}/books/${bookId}/nonfiction/summary-actions`, {
        method: 'POST',
        body: JSON.stringify({ summary: summary || null, action_steps: steps }),
      });
      toast({ title: 'Added' });
      setSummary('');
      setActionSteps('');
      setShowForm(false);
      window.location.reload();
    } catch {
      toast({ title: 'Failed', variant: 'destructive' });
    } finally {
      setSaving(false);
    }
  }

  return (
    <Card variant="sanctuary">
      <CardHeader>
        <CardTitle className="font-serif">Summary & action steps</CardTitle>
        <CardDescription>Key takeaways and reader action steps.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {summaryActions.map((s) => (
          <div key={String(s.id)} className="rounded-lg border p-4">
            {s.summary && <p>{String(s.summary).slice(0, 150)}...</p>}
            {s.action_steps && Array.isArray(s.action_steps) && (
              <ul className="list-disc list-inside text-sm mt-2">
                {(s.action_steps as string[]).slice(0, 3).map((step, i) => (
                  <li key={i}>{step}</li>
                ))}
              </ul>
            )}
          </div>
        ))}
        {showForm ? (
          <div className="rounded-lg border p-4 space-y-4">
            <textarea placeholder="Summary" value={summary} onChange={(e) => setSummary(e.target.value)} className="min-h-[60px] w-full rounded-lg border px-3 py-2 text-sm" />
            <textarea placeholder="Action steps (one per line)" value={actionSteps} onChange={(e) => setActionSteps(e.target.value)} className="min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm" />
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving}>Add</Button>
              <Button variant="ghost" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </div>
        ) : (
          <Button variant="outline" onClick={() => setShowForm(true)}><Plus className="h-4 w-4 mr-2" />Add summary & actions</Button>
        )}
      </CardContent>
    </Card>
  );
}
