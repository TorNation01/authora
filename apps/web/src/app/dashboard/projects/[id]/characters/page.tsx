'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { api, apiUpload } from '@/lib/api';

type Character = {
  id: string;
  project_id: string;
  origin_book_id: string | null;
  continuation_of: string | null;
  name: string;
  aliases: string[];
  role: string;
  archetype: string | null;
  one_line: string | null;
  age: string | null;
  pronouns: string | null;
  gender: string | null;
  profession: string | null;
  appearance: string | null;
  voice: string | null;
  personality: string | null;
  goals: string | null;
  fears: string | null;
  motivations: string | null;
  internal_conflict: string | null;
  external_conflict: string | null;
  backstory: string | null;
  wound: string | null;
  secret: string | null;
  arc_summary: string | null;
  quirks: string | null;
  need: string | null;
  flaws: string | null;
  skills_limitations: string | null;
  values_boundaries: string | null;
  distinctive_behaviour: string | null;
  portrait_url: string | null;
  portrait_source: string | null;
  dialogue_patterns: string | null;
  relationships_notes: string | null;
  private_notes: string | null;
  canon_status: string;
  status: string;
  books: { id: string; title: string }[];
};

type Bond = {
  id: string;
  from_character_id: string;
  to_character_id: string;
  to_name: string | null;
  description: string | null;
  from_chapter_id: string | null;
};

type BookLite = { id: string; title: string };

const ROLES = [
  'protagonist',
  'antagonist',
  'love interest',
  'mentor',
  'supporting',
  'comic relief',
  'other',
];

const GROUPS: { title: string; hint: string; fields: { key: string; label: string; rows?: number; prompt: string }[] }[] = [
  {
    title: 'Identity',
    hint: 'Who they are before the story touches them.',
    fields: [
      { key: 'name', label: 'Name', prompt: 'The name on the page. Check it against the used-names list first.' },
      { key: 'one_line', label: 'One line', prompt: 'Describe them in a single sentence a reader would remember.', rows: 2 },
      { key: 'archetype', label: 'Archetype', prompt: 'The shape they take — reluctant hero, trickster, tyrant, confidant.' },
      { key: 'age', label: 'Age', prompt: 'Age or age range at the start of this book.' },
      { key: 'pronouns', label: 'Pronouns', prompt: 'How the prose refers to them.' },
    ],
  },
  {
    title: 'Body and voice',
    hint: 'What the reader sees and hears.',
    fields: [
      { key: 'gender', label: 'Gender', prompt: 'How they would describe themselves. Leave blank if it never matters on the page.', rows: 1 },
      { key: 'profession', label: 'Profession', prompt: 'What they do for a living, and what it has made of them.', rows: 2 },
      { key: 'appearance', label: 'Appearance', prompt: 'Three details that stick — not a police description. What do people notice first?', rows: 3 },
      { key: 'voice', label: 'Voice and speech', prompt: 'Rhythm, vocabulary, accent, verbal tics. How would you recognise them with your eyes closed?', rows: 3 },
      { key: 'dialogue_patterns', label: 'Dialogue patterns', prompt: 'Do they deflect with jokes, over-explain, go quiet? What do they never say?', rows: 2 },
      { key: 'personality', label: 'Personality', prompt: 'How they behave under pressure, and what they show the world versus what they hide.', rows: 3 },
      { key: 'quirks', label: 'Quirks and habits', prompt: 'Small physical habits that make them real on the page.', rows: 2 },
      { key: 'distinctive_behaviour', label: 'Distinctive behaviour', prompt: 'Habits, mannerisms and small details that make them recognisable on the page.', rows: 2 },
      { key: 'flaws', label: 'Flaws and contradictions', prompt: 'Where their beliefs and actions conflict. What they would never admit.', rows: 2 },
    ],
  },
  {
    title: 'Drive',
    hint: 'The engine. A character without these is furniture.',
    fields: [
      { key: 'goals', label: 'What they want', prompt: 'The concrete external goal that drives their choices in this book.', rows: 2 },
      { key: 'motivations', label: 'Why they want it', prompt: 'The need underneath the want. What are they actually trying to feel or avoid?', rows: 2 },
      { key: 'need', label: 'What they actually need', prompt: 'Not the goal — the thing they must learn or confront, which they would refuse if offered.', rows: 2 },
      { key: 'fears', label: 'What they fear', prompt: 'The thing they will lie, betray or break themselves to avoid.', rows: 2 },
      { key: 'internal_conflict', label: 'Internal conflict', prompt: 'The two things inside them that cannot both be true.', rows: 2 },
      { key: 'external_conflict', label: 'External conflict', prompt: 'The person or force standing in their way, and why it will not move.', rows: 2 },
    ],
  },
  {
    title: 'History',
    hint: 'What happened before page one.',
    fields: [
      { key: 'skills_limitations', label: 'Skills and limitations', prompt: 'What they can do well, and where they are out of their depth.', rows: 2 },
      { key: 'values_boundaries', label: 'Values and boundaries', prompt: 'What they believe, and what they would refuse to do even under pressure.', rows: 2 },
      { key: 'backstory', label: 'Backstory', prompt: 'Only what the plot leans on. The rest is iceberg.', rows: 4 },
      { key: 'wound', label: 'The wound', prompt: 'The moment that taught them the lie they believe about themselves.', rows: 2 },
      { key: 'secret', label: 'Secret', prompt: 'What they are hiding, who could expose it, and what it costs if they do.', rows: 2 },
      { key: 'arc_summary', label: 'Arc', prompt: 'Where they start, what breaks them open, where they end. The change in one paragraph.', rows: 3 },
    ],
  },
  {
    title: 'Relationships',
    hint: 'Who they are to everyone else.',
    fields: [
      { key: 'relationships_notes', label: 'Relationships', prompt: 'Each key relationship: what they owe, what they resent, what is unsaid.', rows: 4 },
    ],
  },
  {
    title: 'Working notes',
    hint: 'For you, not the reader.',
    fields: [
      { key: 'private_notes', label: 'Private notes', prompt: 'Open questions, research, anything still moving.', rows: 3 },
    ],
  },
];

const BLANK: Omit<Character, 'id' | 'project_id' | 'books'> = {
  origin_book_id: null,
  continuation_of: null,
  name: '',
  aliases: [],
  role: 'supporting',
  archetype: '',
  one_line: '',
  age: '',
  pronouns: '',
  gender: '',
  profession: '',
  appearance: '',
  voice: '',
  personality: '',
  goals: '',
  fears: '',
  motivations: '',
  internal_conflict: '',
  external_conflict: '',
  backstory: '',
  wound: '',
  secret: '',
  arc_summary: '',
  quirks: '',
  need: '',
  flaws: '',
  skills_limitations: '',
  values_boundaries: '',
  distinctive_behaviour: '',
  portrait_url: null,
  portrait_source: null,
  dialogue_patterns: '',
  relationships_notes: '',
  private_notes: '',
  canon_status: 'working',
  status: 'active',
};

export default function CharacterLibraryPage() {
  const params = useParams<{ id: string }>();
  const projectId = params?.id as string;

  const [characters, setCharacters] = useState<Character[]>([]);
  const [books, setBooks] = useState<BookLite[]>([]);
  const [query, setQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [editing, setEditing] = useState<Character | null>(null);
  const [draft, setDraft] = useState<typeof BLANK>(BLANK);
  const [nameWarning, setNameWarning] = useState<{ id: string; name: string; continuation_of: string | null } | null>(null);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<'library' | 'names'>('library');
  const [bonds, setBonds] = useState<Bond[]>([]);
  const [bondBook, setBondBook] = useState<string>('');
  const [bondChapters, setBondChapters] = useState<{ chapter_id: string; title: string }[]>([]);
  const [portraitBusy, setPortraitBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [c, b] = await Promise.all([
        api<{ characters: Character[] }>(`/api/v1/projects/${projectId}/characters?include_retired=true`),
        api<BookLite[] | { books: BookLite[] }>(`/api/v1/projects/${projectId}/books`),
      ]);
      setCharacters(c.characters);
      setBooks(Array.isArray(b) ? b : b.books || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the character library.');
    } finally {
      setLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    if (projectId) void load();
  }, [load, projectId]);

  useEffect(() => {
    if (!bondBook && books.length) setBondBook(books[0].id);
  }, [books, bondBook]);

  useEffect(() => {
    if (!editing || !bondBook) {
      setBonds([]);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const [rels, chapters] = await Promise.all([
          api<Bond[]>(`/api/v1/projects/${projectId}/books/${bondBook}/character-relationships`),
          api<{ chapter_id: string; title: string }[]>(
            `/api/v1/projects/${projectId}/books/${bondBook}/chapter-briefs`
          ),
        ]);
        if (!cancelled) {
          setBonds(rels.filter((r) => r.from_character_id === editing.id));
          setBondChapters(chapters.map((c) => ({ chapter_id: c.chapter_id, title: c.title })));
        }
      } catch {
        if (!cancelled) setBonds([]);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [bondBook, editing, projectId]);

  async function addBond(toId: string) {
    if (!editing || !bondBook || !toId) return;
    try {
      const rel = await api<Bond>(`/api/v1/projects/${projectId}/books/${bondBook}/character-relationships`, {
        method: 'POST',
        body: JSON.stringify({
          from_character_id: editing.id,
          to_character_id: toId,
          description: '',
        }),
      });
      setBonds((current) => [...current, rel]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add that relationship.');
    }
  }

  async function patchBond(id: string, patch: Partial<Pick<Bond, 'description' | 'from_chapter_id'>>) {
    if (!bondBook) return;
    setBonds((current) => current.map((b) => (b.id === id ? { ...b, ...patch } : b)));
    try {
      await api(`/api/v1/projects/${projectId}/books/${bondBook}/character-relationships/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          description: patch.description,
          from_chapter_id: patch.from_chapter_id ?? null,
        }),
      });
    } catch {
      setSaveState('error');
    }
  }

  async function removeBond(id: string) {
    if (!bondBook) return;
    setBonds((current) => current.filter((b) => b.id !== id));
    await api(`/api/v1/projects/${projectId}/books/${bondBook}/character-relationships/${id}`, {
      method: 'DELETE',
    });
  }

  async function uploadPortrait(file: File) {
    if (!editing) return;
    setPortraitBusy(true);
    try {
      const updated = await apiUpload<Character>(
        `/api/v1/projects/${projectId}/characters/${editing.id}/portrait`,
        file
      );
      setEditing(updated);
      setDraft((d) => ({ ...d, portrait_url: updated.portrait_url, portrait_source: updated.portrait_source }));
      setCharacters((current) => current.map((c) => (c.id === updated.id ? updated : c)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not upload that image.');
    } finally {
      setPortraitBusy(false);
    }
  }

  async function clearPortrait() {
    if (!editing) return;
    setPortraitBusy(true);
    try {
      const updated = await api<Character>(`/api/v1/projects/${projectId}/characters/${editing.id}/portrait`, {
        method: 'DELETE',
      });
      setEditing(updated);
      setDraft((d) => ({ ...d, portrait_url: null, portrait_source: null }));
      setCharacters((current) => current.map((c) => (c.id === updated.id ? updated : c)));
    } finally {
      setPortraitBusy(false);
    }
  }

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return characters.filter((c) => {
      if (roleFilter && c.role !== roleFilter) return false;
      if (!q) return true;
      return (
        c.name.toLowerCase().includes(q) ||
        (c.one_line || '').toLowerCase().includes(q) ||
        (c.archetype || '').toLowerCase().includes(q) ||
        c.aliases.some((a) => a.toLowerCase().includes(q))
      );
    });
  }, [characters, query, roleFilter]);

  const usedNames = useMemo(
    () => [...characters].sort((a, b) => a.name.localeCompare(b.name)),
    [characters]
  );

  function openNew() {
    setEditing(null);
    setDraft({ ...BLANK });
    setNameWarning(null);
  }

  function openEdit(c: Character) {
    setEditing(c);
    setDraft({ ...BLANK, ...c });
    setNameWarning(null);
  }

  async function checkName(name: string) {
    if (!name.trim()) return;
    try {
      const r = await api<{ used: boolean; matches: { id: string; name: string; continuation_of: string | null }[] }>(
        `/api/v1/projects/${projectId}/characters/name-check?name=${encodeURIComponent(name)}${editing ? `&exclude_id=${editing.id}` : ''}`
      );
      setNameWarning(r.used && r.matches.length ? r.matches[0] : null);
    } catch {
      setNameWarning(null);
    }
  }

  async function save() {
    if (!draft.name.trim()) return;
    setSaveState('saving');
    try {
      const payload = { ...draft, aliases: draft.aliases.filter(Boolean) };
      let saved: Character;
      if (editing) {
        saved = await api<Character>(`/api/v1/projects/${projectId}/characters/${editing.id}`, {
          method: 'PATCH',
          body: JSON.stringify({ fields: payload }),
        });
      } else {
        saved = await api<Character>(`/api/v1/projects/${projectId}/characters`, {
          method: 'POST',
          body: JSON.stringify(payload),
        });
      }
      setCharacters((current) => {
        const rest = current.filter((c) => c.id !== saved.id);
        return [...rest, saved].sort((a, b) => a.name.localeCompare(b.name));
      });
      setSaveState('saved');
      setTimeout(() => setSaveState('idle'), 2000);
      setEditing(saved);
    } catch {
      setSaveState('error');
    }
  }

  async function remove(c: Character) {
    if (!confirm(`Remove ${c.name} from the library? Chapters already written are untouched.`)) return;
    await api(`/api/v1/projects/${projectId}/characters/${c.id}`, { method: 'DELETE' });
    setCharacters((current) => current.filter((x) => x.id !== c.id));
    if (editing?.id === c.id) setEditing(null);
  }

  async function toggleBook(c: Character, book: BookLite, attached: boolean) {
    const path = `/api/v1/projects/${projectId}/books/${book.id}/characters/${c.id}`;
    await api(path, { method: attached ? 'DELETE' : 'POST' });
    setCharacters((current) =>
      current.map((x) =>
        x.id === c.id
          ? { ...x, books: attached ? x.books.filter((b) => b.id !== book.id) : [...x.books, book] }
          : x
      )
    );
    if (editing?.id === c.id) {
      setDraft((d) => ({ ...d, origin_book_id: attached ? null : book.id }));
    }
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading the character library…</p>;
  if (error) return <p className="text-sm text-destructive">{error}</p>;

  return (
    <div className="min-w-0">
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl font-bold text-foreground">Characters</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            One library for the whole series. Build a character once, bring them into any book,
            and keep every appearance consistent.
          </p>
        </div>
        <button
          type="button"
          onClick={openNew}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary-hover"
        >
          + New character
        </button>
      </header>

      <div className="mb-5 flex flex-wrap items-center gap-3 border-b border-border pb-3">
        <div className="flex gap-1">
          {(['library', 'names'] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`rounded-lg px-3 py-1.5 text-sm ${
                tab === t ? 'bg-primary/10 font-medium text-foreground' : 'text-muted-foreground hover:bg-muted'
              }`}
            >
              {t === 'library' ? `Library (${characters.length})` : `Used names (${characters.length})`}
            </button>
          ))}
        </div>
        {tab === 'library' && (
          <>
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search name, alias, archetype…"
              className="min-w-[200px] flex-1 rounded-lg border border-border bg-background px-3 py-1.5 text-sm"
            />
            <select
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
              className="rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
            >
              <option value="">All roles</option>
              {ROLES.map((r) => (
                <option key={r} value={r}>
                  {r}
                </option>
              ))}
            </select>
          </>
        )}
      </div>

      {tab === 'names' ? (
        <div className="max-w-2xl">
          <p className="mb-4 text-sm text-muted-foreground">
            Every name already spoken for across this series. A new character may not reuse one
            unless you deliberately mark them as a continuation.
          </p>
          <ul className="divide-y divide-border rounded-xl border border-border">
            {usedNames.map((c) => (
              <li key={c.id} className="flex flex-wrap items-center justify-between gap-2 px-4 py-2.5">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-foreground">
                    {c.name}
                    {c.aliases.length > 0 && (
                      <span className="ml-2 text-xs text-muted-foreground">({c.aliases.join(', ')})</span>
                    )}
                  </p>
                  <p className="truncate text-xs text-muted-foreground">
                    {c.books.length ? c.books.map((b) => b.title).join(' · ') : 'Not attached to a book yet'}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => {
                    setTab('library');
                    openEdit(c);
                  }}
                  className="text-xs text-primary hover:underline"
                >
                  Open
                </button>
              </li>
            ))}
            {usedNames.length === 0 && (
              <li className="px-4 py-6 text-center text-sm text-muted-foreground">No names yet.</li>
            )}
          </ul>
        </div>
      ) : (
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1fr)_420px]">
          <div>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {filtered.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => openEdit(c)}
                  className={`rounded-xl border p-4 text-left transition-colors hover:border-primary/50 ${
                    editing?.id === c.id ? 'border-primary' : 'border-border'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-serif text-base font-semibold text-foreground">{c.name}</p>
                    {c.canon_status === 'locked' && (
                      <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] uppercase tracking-wider text-emerald-600">
                        locked
                      </span>
                    )}
                  </div>
                  <p className="mt-0.5 text-xs uppercase tracking-wider text-muted-foreground">{c.role}</p>
                  <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">
                    {c.one_line || 'No one-line description yet.'}
                  </p>
                  <p className="mt-3 truncate text-[11px] text-muted-foreground">
                    {c.books.length ? c.books.map((b) => b.title).join(' · ') : 'Not in a book yet'}
                  </p>
                </button>
              ))}
              {filtered.length === 0 && (
                <div className="rounded-xl border border-dashed border-border p-8 text-center sm:col-span-2 xl:col-span-3">
                  <p className="text-sm text-muted-foreground">
                    No characters match. Create the first one — the library travels with the series.
                  </p>
                </div>
              )}
            </div>
          </div>

          <aside className="min-w-0 rounded-xl border border-border p-4">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-serif text-lg font-semibold">
                {editing ? 'Edit character' : 'New character'}
              </h2>
              {editing && (
                <button
                  type="button"
                  onClick={() => remove(editing)}
                  className="text-xs text-muted-foreground hover:text-destructive"
                >
                  Remove
                </button>
              )}
            </div>

            <div className="mb-4 flex items-start gap-3">
              <div className="h-24 w-20 shrink-0 overflow-hidden rounded-lg border border-border bg-muted">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                {draft.portrait_url ? (
                  <img src={draft.portrait_url} alt={draft.name || 'Character'} className="h-full w-full object-cover" />
                ) : (
                  <span className="flex h-full items-center justify-center text-[10px] text-muted-foreground">No portrait</span>
                )}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium">Portrait</p>
                <p className="mb-2 text-[11px] leading-snug text-muted-foreground">
                  Upload an image, or leave it and let the one-line carry them.
                </p>
                <div className="flex flex-wrap items-center gap-2">
                  <label className={`cursor-pointer rounded-lg border border-border px-2.5 py-1.5 text-xs hover:bg-muted ${!editing || portraitBusy ? 'pointer-events-none opacity-50' : ''}`}>
                    {portraitBusy ? 'Working…' : draft.portrait_url ? 'Replace image' : 'Upload image'}
                    <input
                      type="file"
                      accept="image/png,image/jpeg,image/webp,image/gif"
                      className="hidden"
                      disabled={!editing || portraitBusy}
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) void uploadPortrait(file);
                      }}
                    />
                  </label>
                  {draft.portrait_url && (
                    <button
                      type="button"
                      onClick={() => void clearPortrait()}
                      className="text-xs text-muted-foreground hover:text-destructive"
                    >
                      Remove
                    </button>
                  )}
                  {!editing && <span className="text-[11px] text-muted-foreground">Save first.</span>}
                </div>
              </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-2">
              <label className="sm:col-span-2">
                <span className="mb-1 block text-xs font-medium">Name</span>
                <input
                  value={draft.name}
                  onChange={(e) => setDraft({ ...draft, name: e.target.value })}
                  onBlur={(e) => checkName(e.target.value)}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                />
                {nameWarning && (
                  <span className="mt-1 block rounded-lg bg-amber-500/10 px-2 py-1.5 text-[11px] text-amber-700">
                    &ldquo;{nameWarning.name}&rdquo; is already in the library.{' '}
                    {editing && (
                      <button
                        type="button"
                        className="underline"
                        onClick={() => {
                          setDraft({ ...draft, continuation_of: nameWarning.id });
                          setNameWarning(null);
                        }}
                      >
                        Mark this as a continuation of that character
                      </button>
                    )}
                  </span>
                )}
              </label>
              <label>
                <span className="mb-1 block text-xs font-medium">Role</span>
                <select
                  value={draft.role}
                  onChange={(e) => setDraft({ ...draft, role: e.target.value })}
                  className="w-full rounded-lg border border-border bg-background px-2 py-2 text-sm"
                >
                  {ROLES.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                <span className="mb-1 block text-xs font-medium">Canon</span>
                <select
                  value={draft.canon_status}
                  onChange={(e) => setDraft({ ...draft, canon_status: e.target.value })}
                  className="w-full rounded-lg border border-border bg-background px-2 py-2 text-sm"
                >
                  <option value="working">Working</option>
                  <option value="locked">Locked</option>
                  <option value="undecided">Undecided</option>
                </select>
              </label>
              <label className="sm:col-span-2">
                <span className="mb-1 block text-xs font-medium">Aliases (comma separated)</span>
                <input
                  value={draft.aliases.join(', ')}
                  onChange={(e) => setDraft({ ...draft, aliases: e.target.value.split(',').map((a) => a.trim()) })}
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                />
              </label>
            </div>

            <div className="mt-5 max-h-[46vh] space-y-5 overflow-y-auto pr-1">
              {GROUPS.map((group) => (
                <div key={group.title}>
                  <p className="text-xs font-semibold uppercase tracking-wider text-foreground">{group.title}</p>
                  <p className="mb-2 text-[11px] text-muted-foreground">{group.hint}</p>
                  <div className="space-y-3">
                    {group.fields.map((field) => (
                      <label key={field.key as string} className="block">
                        <span className="mb-0.5 block text-xs font-medium">{field.label}</span>
                        <span className="mb-1 block text-[11px] leading-snug text-muted-foreground">{field.prompt}</span>
                        <textarea
                          rows={field.rows || 2}
                          value={String((draft as Record<string, unknown>)[field.key] ?? '')}
                          onChange={(e) => setDraft({ ...draft, [field.key]: e.target.value } as typeof BLANK)}
                          className="w-full resize-y rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                        />
                      </label>
                    ))}
                  </div>
                </div>
              ))}

              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-foreground">Appears in</p>
                <p className="mb-2 text-[11px] text-muted-foreground">
                  Tick each book in the series this character appears in.
                </p>
                <div className="space-y-1">
                  {books.map((b) => {
                    const attached = editing?.books.some((x) => x.id === b.id) ?? false;
                    return (
                      <label key={b.id} className="flex items-center gap-2 text-sm">
                        <input
                          type="checkbox"
                          checked={attached}
                          disabled={!editing}
                          onChange={() => editing && toggleBook(editing, b, attached)}
                        />
                        <span className="truncate">{b.title}</span>
                      </label>
                    );
                  })}
                  {books.length === 0 && <p className="text-xs text-muted-foreground">No books yet.</p>}
                </div>
              </div>

              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-foreground">
                  In this book, person by person
                </p>
                <p className="mb-2 text-[11px] leading-snug text-muted-foreground">
                  How this character sees each other character. One-way on purpose — they may see a
                  rival where the other barely notices them. Optional, and only true for the book
                  you pick.
                </p>
                <select
                  value={bondBook}
                  onChange={(e) => setBondBook(e.target.value)}
                  className="mb-2 w-full rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                  disabled={!editing || books.length === 0}
                >
                  {books.map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.title}
                    </option>
                  ))}
                </select>

                {editing ? (
                  <div className="space-y-2">
                    {bonds.map((bond) => (
                      <div key={bond.id} className="rounded-lg border border-border p-2">
                        <div className="mb-1 flex items-center justify-between gap-2">
                          <span className="text-xs font-medium">{bond.to_name}</span>
                          <button
                            type="button"
                            onClick={() => void removeBond(bond.id)}
                            className="text-[11px] text-muted-foreground hover:text-destructive"
                          >
                            Remove
                          </button>
                        </div>
                        <textarea
                          rows={2}
                          value={bond.description ?? ''}
                          placeholder="How they see this person, and what is unsaid."
                          onChange={(e) =>
                            setBonds((current) =>
                              current.map((x) => (x.id === bond.id ? { ...x, description: e.target.value } : x))
                            )
                          }
                          onBlur={(e) => void patchBond(bond.id, { description: e.target.value })}
                          className="w-full resize-y rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                        />
                        <label className="mt-1 block">
                          <span className="mb-0.5 block text-[10px] uppercase tracking-wider text-muted-foreground">
                            From chapter
                          </span>
                          <select
                            value={bond.from_chapter_id ?? ''}
                            onChange={(e) => void patchBond(bond.id, { from_chapter_id: e.target.value || null })}
                            className="w-full rounded-lg border border-border bg-background px-2 py-1 text-xs"
                          >
                            <option value="">From the start</option>
                            {bondChapters.map((c) => (
                              <option key={c.chapter_id} value={c.chapter_id}>
                                {c.title}
                              </option>
                            ))}
                          </select>
                        </label>
                      </div>
                    ))}
                    <select
                      value=""
                      onChange={(e) => void addBond(e.target.value)}
                      className="w-full rounded-lg border border-dashed border-border bg-background px-2 py-1.5 text-xs text-muted-foreground"
                    >
                      <option value="">+ Add a character they have a view on…</option>
                      {characters
                        .filter((c) => c.id !== editing.id)
                        .map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.name}
                          </option>
                        ))}
                    </select>
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">Save the character first.</p>
                )}
              </div>
            </div>

            <div className="mt-4 flex items-center gap-3 border-t border-border pt-3">
              <button
                type="button"
                onClick={save}
                disabled={saveState === 'saving' || !draft.name.trim()}
                className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary-hover disabled:opacity-50"
              >
                {saveState === 'saving' ? 'Saving…' : editing ? 'Save changes' : 'Add to library'}
              </button>
              {saveState === 'saved' && <span className="text-xs text-emerald-600">Saved</span>}
              {saveState === 'error' && <span className="text-xs text-destructive">Could not save</span>}
            </div>
          </aside>
        </div>
      )}
    </div>
  );
}
