'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import {
  BibleCharacter,
  BibleSummary,
  CHARACTER_FIELDS,
  ROLE_LABELS,
  STATUS_LABELS,
  characterCompleteness,
  fictionBase,
} from '@/lib/bible';
import { Field, SaveStatus } from '@/components/bible/Field';
import { AISuggest, CompletenessMeter } from '@/components/bible/AISuggest';

const EMPTY_CHARACTER = {
  name: '',
  role: 'supporting',
  description: '',
  age: '',
  appearance: '',
  voice: '',
  backstory: '',
  goals: '',
  need: '',
  wound: '',
  flaws: '',
  secret: '',
  arc_summary: '',
  first_appearance: '',
  status: 'active',
};

type Draft = typeof EMPTY_CHARACTER;

function toDraft(character: BibleCharacter): Draft {
  const draft = { ...EMPTY_CHARACTER } as Record<string, string>;
  for (const key of Object.keys(EMPTY_CHARACTER)) {
    const value = (character as unknown as Record<string, unknown>)[key];
    draft[key] = typeof value === 'string' ? value : '';
  }
  draft.role = character.role || 'supporting';
  draft.status = character.status || 'active';
  return draft as Draft;
}

export default function CharactersPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = fictionBase(projectId, bookId);

  const [characters, setCharacters] = useState<BibleCharacter[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_CHARACTER);
  const [dirty, setDirty] = useState(false);
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Empty-state interview
  const [newName, setNewName] = useState('');
  const [newWant, setNewWant] = useState('');
  const [newRole, setNewRole] = useState('protagonist');
  const [creating, setCreating] = useState(false);

  const load = useCallback(
    async (selectFirst = true) => {
      try {
        const data = await api<BibleSummary>(`${base}/summary`);
        setCharacters(data.characters);
        setSelectedId((current) => {
          if (current && data.characters.some((c) => c.id === current)) return current;
          return selectFirst && data.characters.length > 0 ? data.characters[0].id : null;
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not load characters.');
      } finally {
        setLoading(false);
      }
    },
    [base]
  );

  useEffect(() => {
    if (projectId && bookId) void load();
  }, [load, projectId, bookId]);

  const selected = useMemo(
    () => characters.find((character) => character.id === selectedId) || null,
    [characters, selectedId]
  );

  useEffect(() => {
    if (selected) {
      setDraft(toDraft(selected));
      setDirty(false);
      setStatus('idle');
    }
  }, [selectedId]); // eslint-disable-line react-hooks/exhaustive-deps

  function update(key: keyof Draft, value: string) {
    setDraft((current) => ({ ...current, [key]: value }));
    setDirty(true);
    setStatus('idle');
  }

  async function createCharacter(body: Record<string, unknown>) {
    setCreating(true);
    setError(null);
    try {
      const created = await api<BibleCharacter>(`${base}/characters`, {
        method: 'POST',
        body: JSON.stringify(body),
      });
      await load(false);
      setSelectedId(created.id);
      setNewName('');
      setNewWant('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the character.');
    } finally {
      setCreating(false);
    }
  }

  async function save() {
    if (!selected) return;
    setStatus('saving');
    try {
      const payload: Record<string, unknown> = { name: draft.name };
      for (const field of CHARACTER_FIELDS) {
        if (field.key === 'name') continue;
        const value = draft[field.key as keyof Draft];
        payload[field.key] = value && value.trim() ? value : null;
      }
      payload.role = draft.role;
      payload.status = draft.status;

      const updated = await api<BibleCharacter>(`${base}/characters/${selected.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
      setCharacters((current) =>
        current.map((character) => (character.id === updated.id ? updated : character))
      );
      setDirty(false);
      setStatus('saved');
      setTimeout(() => setStatus('idle'), 2500);
    } catch {
      setStatus('error');
    }
  }

  async function remove() {
    if (!selected) return;
    if (!window.confirm(`Delete ${selected.name || 'this character'}? This cannot be undone.`)) {
      return;
    }
    try {
      await api(`${base}/characters/${selected.id}`, { method: 'DELETE' });
      const remaining = characters.filter((character) => character.id !== selected.id);
      setCharacters(remaining);
      setSelectedId(remaining[0]?.id ?? null);
      if (remaining.length === 0) setDraft(EMPTY_CHARACTER);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete the character.');
    }
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading characters…</p>;

  // ----- Empty state: the first question the book needs answered -----
  if (characters.length === 0) {
    return (
      <div className="min-w-0">
        <header className="mb-8">
          <h1 className="font-serif text-2xl font-bold text-foreground">Characters</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            A book is not a plot with people in it. Start with the person whose life the book
            ruins or saves.
          </p>
        </header>

        <div className="max-w-xl rounded-xl border border-border p-6">
          <p className="text-xs uppercase tracking-wider text-muted-foreground">Start here</p>
          <h2 className="mt-2 font-serif text-xl leading-snug text-foreground">
            Who is this book about, and what do they want more than anything?
          </h2>

          <div className="mt-6 space-y-5">
            <div>
              <label htmlFor="first-name" className="block text-sm font-medium text-foreground">
                Their name
              </label>
              <p className="mb-2 mt-1 text-xs leading-relaxed text-muted-foreground">
                What do people call them — and what does only one person call them?
              </p>
              <input
                id="first-name"
                value={newName}
                onChange={(event) => setNewName(event.target.value)}
                placeholder="Mira Vane"
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            <div>
              <label htmlFor="first-want" className="block text-sm font-medium text-foreground">
                What they want
              </label>
              <p className="mb-2 mt-1 text-xs leading-relaxed text-muted-foreground">
                The external goal that gets them out of bed and into trouble.
              </p>
              <textarea
                id="first-want"
                rows={3}
                value={newWant}
                onChange={(event) => setNewWant(event.target.value)}
                placeholder="To reach the capital before the thaw and bury the order that killed her father."
                className="w-full resize-y rounded-lg border border-input bg-background px-3 py-2 text-sm leading-relaxed text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            <div>
              <label htmlFor="first-role" className="block text-sm font-medium text-foreground">
                What job do they do in the story?
              </label>
              <select
                id="first-role"
                value={newRole}
                onChange={(event) => setNewRole(event.target.value)}
                className="mt-2 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              >
                {Object.entries(ROLE_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              disabled={creating || !newName.trim() || !newWant.trim()}
              onClick={() =>
                createCharacter({
                  name: newName.trim(),
                  role: newRole,
                  goals: newWant.trim(),
                  description: newWant.trim().slice(0, 140),
                })
              }
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50"
            >
              {creating ? 'Creating…' : 'Create the character and open the sheet'}
            </button>
            {error ? <p className="text-sm text-destructive">{error}</p> : null}
          </div>
        </div>
      </div>
    );
  }

  const completeness = selected
    ? characterCompleteness({ ...selected, ...(draft as unknown as BibleCharacter) })
    : null;

  return (
    <div className="min-w-0">
      <header className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <h1 className="font-serif text-2xl font-bold text-foreground">Characters</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            A sheet is finished when the want, the need and the wound disagree with each other.
          </p>
        </div>
        <button
          type="button"
          onClick={() =>
            createCharacter({ name: 'Untitled character', role: 'supporting', status: 'active' })
          }
          className="shrink-0 rounded-lg border border-border px-3 py-2 text-sm text-foreground transition-colors hover:bg-muted"
        >
          New character
        </button>
      </header>

      <div className="grid gap-6 md:grid-cols-[220px_minmax(0,1fr)]">
        {/* List */}
        <aside className="min-w-0">
          <ul className="divide-y divide-border border-y border-border">
            {characters.map((character) => {
              const meter = characterCompleteness(character);
              const active = character.id === selectedId;
              return (
                <li key={character.id}>
                  <button
                    type="button"
                    onClick={() => setSelectedId(character.id)}
                    className={`w-full px-2 py-3 text-left transition-colors ${
                      active ? 'bg-muted/60' : 'hover:bg-muted/30'
                    }`}
                  >
                    <span className="block truncate text-sm font-medium text-foreground">
                      {character.name}
                    </span>
                    <span className="mt-0.5 block text-xs text-muted-foreground">
                      {ROLE_LABELS[character.role] || character.role}
                    </span>
                    <span className="mt-1.5 flex items-center gap-2">
                      <span className="h-0.5 flex-1 bg-muted">
                        <span
                          className="block h-full bg-primary"
                          style={{ width: `${meter.pct}%` }}
                        />
                      </span>
                      <span className="text-[10px] tabular-nums text-muted-foreground">
                        {meter.filled}/{meter.total}
                      </span>
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </aside>

        {/* Sheet */}
        <div className="min-w-0">
          {selected ? (
            <>
              <div className="mb-5 border-b border-border pb-4">
                <input
                  value={draft.name}
                  onChange={(event) => update('name', event.target.value)}
                  aria-label="Character name"
                  className="w-full border-0 bg-transparent p-0 font-serif text-2xl font-bold text-foreground focus:outline-none focus:ring-0"
                />
                {completeness ? (
                  <div className="mt-3 max-w-xs">
                    <CompletenessMeter
                      filled={completeness.filled}
                      total={completeness.total}
                      label="Sheet completeness"
                    />
                  </div>
                ) : null}
              </div>

              <div className="mb-5 grid gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="role" className="block text-sm font-medium text-foreground">
                    Role
                  </label>
                  <p className="mb-2 mt-1 text-xs text-muted-foreground">
                    What job do they do in the story?
                  </p>
                  <select
                    id="role"
                    value={draft.role}
                    onChange={(event) => update('role', event.target.value)}
                    className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    {Object.entries(ROLE_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label htmlFor="status" className="block text-sm font-medium text-foreground">
                    Status
                  </label>
                  <p className="mb-2 mt-1 text-xs text-muted-foreground">
                    Are they in the book, in the background, or cut?
                  </p>
                  <select
                    id="status"
                    value={draft.status}
                    onChange={(event) => update('status', event.target.value)}
                    className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    {Object.entries(STATUS_LABELS).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid gap-5 sm:grid-cols-2">
                {CHARACTER_FIELDS.filter((field) => field.key !== 'name').map((field) => (
                  <div
                    key={field.key as string}
                    className={field.multiline && (field.rows || 0) >= 3 ? 'sm:col-span-2' : ''}
                  >
                    <Field
                      label={field.label}
                      question={field.question}
                      value={draft[field.key as keyof Draft] || ''}
                      rows={field.rows}
                      placeholder={field.placeholder}
                      multiline={field.multiline}
                      onChange={(value) => update(field.key as keyof Draft, value)}
                    />
                  </div>
                ))}
              </div>

              <div className="mt-6 flex flex-wrap items-center gap-3 border-t border-border pt-4">
                <button
                  type="button"
                  onClick={save}
                  disabled={status === 'saving'}
                  className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-60"
                >
                  {status === 'saving' ? 'Saving…' : 'Save character'}
                </button>
                <SaveStatus state={status} />
                {dirty ? <span className="text-xs text-muted-foreground">Unsaved changes</span> : null}
                <button
                  type="button"
                  onClick={remove}
                  className="ml-auto text-xs text-muted-foreground underline-offset-4 hover:text-destructive hover:underline"
                >
                  Delete character
                </button>
              </div>

              <section className="mt-10 border-t border-border pt-6">
                <h2 className="font-serif text-lg font-semibold text-foreground">
                  Interrogate this character
                </h2>
                <p className="mb-4 mt-1 text-sm leading-relaxed text-muted-foreground">
                  Each question reads the sheet above. The answer arrives as a draft — edit it,
                  then choose whether it belongs in the sheet.
                </p>
                <div className="grid gap-3 sm:grid-cols-3">
                  <AISuggest
                    path={`${base}/ai`}
                    promptType="character_interrogate"
                    label="Interrogate this character"
                    insertLabel="Insert into backstory"
                    context={`The character under examination is ${draft.name || selected.name}. Answer only about them.`}
                    onInsert={(text) => update('backstory', text)}
                  />
                  <AISuggest
                    path={`${base}/ai`}
                    promptType="character_contradiction"
                    label="Find the contradiction"
                    insertLabel="Insert into flaw"
                    context={`The character under examination is ${draft.name || selected.name}. Answer only about them.`}
                    onInsert={(text) => update('flaws', text)}
                  />
                  <AISuggest
                    path={`${base}/ai`}
                    promptType="character_lie"
                    label="What are they lying about?"
                    insertLabel="Insert into secret"
                    context={`The character under examination is ${draft.name || selected.name}. Answer only about them.`}
                    onInsert={(text) => update('secret', text)}
                  />
                </div>
              </section>
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Select a character to edit their sheet.</p>
          )}
        </div>
      </div>

      {error ? <p className="mt-4 text-sm text-destructive">{error}</p> : null}
    </div>
  );
}
