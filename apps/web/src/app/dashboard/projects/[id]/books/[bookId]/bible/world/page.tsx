'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import {
  BibleSummary,
  BibleTheme,
  BibleWorldElement,
  WORLD_GROUPS,
  fictionBase,
  vaultBase,
} from '@/lib/bible';

const inputClass =
  'w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring';

export default function WorldPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = fictionBase(projectId, bookId);
  const vault = vaultBase(projectId);

  const [world, setWorld] = useState<BibleWorldElement[]>([]);
  const [themes, setThemes] = useState<BibleTheme[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [summary, themeList] = await Promise.all([
        api<BibleSummary>(`${base}/summary`),
        api<BibleTheme[]>(`${vault}/themes?book_id=${bookId}`).catch(() => []),
      ]);
      setWorld(summary.world_elements);
      setThemes(Array.isArray(themeList) ? themeList : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the world notes.');
    } finally {
      setLoading(false);
    }
  }, [base, vault, bookId]);

  useEffect(() => {
    if (projectId && bookId) void load();
  }, [load, projectId, bookId]);

  if (loading) return <p className="text-sm text-muted-foreground">Loading world and themes…</p>;

  return (
    <div className="min-w-0">
      <header className="mb-8">
        <h1 className="font-serif text-2xl font-bold text-foreground">World &amp; Themes</h1>
        <p className="mt-1 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          A world is the set of constraints that make choices expensive. A theme is a claim the
          story tests — if you cannot name the scene that tests it, it is a mood, not a theme.
        </p>
      </header>

      {WORLD_GROUPS.map((group) => (
        <WorldGroup
          key={group.category}
          base={base}
          category={group.category}
          title={group.title}
          blurb={group.blurb}
          nameQuestion={group.nameQuestion}
          question={group.question}
          items={world.filter((element) => element.category === group.category)}
          onChanged={load}
        />
      ))}

      <section className="mb-10">
        <h2 className="font-serif text-lg font-semibold text-foreground">Themes</h2>
        <p className="mb-4 mt-1 text-sm leading-relaxed text-muted-foreground">
          State each theme as a claim, then name where the book dramatises it. A theme that is
          only named will read as a lecture.
        </p>

        <div className="space-y-4">
          {themes.map((theme) => (
            <ThemeRow key={theme.id} theme={theme} vault={vault} onChanged={load} />
          ))}
        </div>

        <ThemeCreate vault={vault} bookId={bookId} onCreated={load} />
      </section>

      {error ? <p className="text-sm text-destructive">{error}</p> : null}
    </div>
  );
}

function WorldGroup({
  base,
  category,
  title,
  blurb,
  nameQuestion,
  question,
  items,
  onChanged,
}: {
  base: string;
  category: string;
  title: string;
  blurb: string;
  nameQuestion: string;
  question: string;
  items: BibleWorldElement[];
  onChanged: () => Promise<void>;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [busy, setBusy] = useState(false);

  async function create() {
    if (!name.trim()) return;
    setBusy(true);
    try {
      await api(`${base}/world`, {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          category,
          description: description.trim() || null,
        }),
      });
      setName('');
      setDescription('');
      await onChanged();
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="mb-10">
      <h2 className="font-serif text-lg font-semibold text-foreground">{title}</h2>
      <p className="mb-4 mt-1 text-sm text-muted-foreground">{blurb}</p>

      <div className="space-y-4">
        {items.map((item) => (
          <WorldRow key={item.id} item={item} base={base} onChanged={onChanged} />
        ))}
      </div>

      <div className="mt-4 rounded-xl border border-border p-4">
        <p className="text-xs uppercase tracking-wider text-muted-foreground">Add</p>
        <div className="mt-3 grid gap-3">
          <div>
            <label className="block text-sm font-medium text-foreground">{nameQuestion}</label>
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              className={`mt-2 ${inputClass}`}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground">{question}</label>
            <textarea
              rows={2}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              className={`mt-2 resize-y leading-relaxed ${inputClass}`}
            />
          </div>
          <div>
            <button
              type="button"
              onClick={create}
              disabled={busy || !name.trim()}
              className="rounded-lg border border-border px-3 py-1.5 text-sm text-foreground transition-colors hover:bg-muted disabled:opacity-50"
            >
              {busy ? 'Adding…' : `Add ${category === 'rule' ? 'rule' : category}`}
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}

function WorldRow({
  item,
  base,
  onChanged,
}: {
  item: BibleWorldElement;
  base: string;
  onChanged: () => Promise<void>;
}) {
  const [name, setName] = useState(item.name);
  const [description, setDescription] = useState(item.description || '');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setName(item.name);
    setDescription(item.description || '');
  }, [item.name, item.description]);

  async function save() {
    setBusy(true);
    try {
      await api(`${base}/world/${item.id}`, {
        method: 'PATCH',
        body: JSON.stringify({ name: name.trim(), description: description.trim() || null }),
      });
      await onChanged();
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!window.confirm(`Remove ${item.name}?`)) return;
    setBusy(true);
    try {
      await api(`${base}/world/${item.id}`, { method: 'DELETE' });
      await onChanged();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-xl border border-border p-4">
      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        aria-label="Name"
        className="w-full border-0 bg-transparent p-0 font-serif text-base font-semibold text-foreground focus:outline-none"
      />
      <textarea
        rows={2}
        value={description}
        onChange={(event) => setDescription(event.target.value)}
        aria-label="Description"
        placeholder="What does it demand, forbid, or cost?"
        className={`mt-2 resize-y leading-relaxed ${inputClass}`}
      />
      <div className="mt-2 flex items-center gap-3">
        <button
          type="button"
          onClick={save}
          disabled={busy}
          className="rounded-lg border border-border px-3 py-1 text-xs text-foreground transition-colors hover:bg-muted disabled:opacity-50"
        >
          Save
        </button>
        <button
          type="button"
          onClick={remove}
          disabled={busy}
          className="text-xs text-muted-foreground hover:text-destructive"
        >
          Remove
        </button>
      </div>
    </div>
  );
}

function ThemeRow({
  theme,
  vault,
  onChanged,
}: {
  theme: BibleTheme;
  vault: string;
  onChanged: () => Promise<void>;
}) {
  const [name, setName] = useState(theme.name);
  const [description, setDescription] = useState(theme.description || '');
  const [notes, setNotes] = useState(theme.notes || '');
  const [busy, setBusy] = useState(false);

  async function save() {
    setBusy(true);
    try {
      await api(`${vault}/themes/${theme.id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim() || null,
          notes: notes.trim() || null,
        }),
      });
      await onChanged();
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!window.confirm(`Remove the theme “${theme.name}”?`)) return;
    setBusy(true);
    try {
      await api(`${vault}/themes/${theme.id}`, { method: 'DELETE' });
      await onChanged();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="rounded-xl border border-border p-4">
      <label className="block text-xs uppercase tracking-wider text-muted-foreground">
        The claim
      </label>
      <input
        value={name}
        onChange={(event) => setName(event.target.value)}
        className="mt-1 w-full border-0 bg-transparent p-0 font-serif text-base font-semibold text-foreground focus:outline-none"
      />
      <div className="mt-3 grid gap-3">
        <div>
          <label className="block text-xs text-muted-foreground">
            Where is it dramatised — which scene proves it?
          </label>
          <textarea
            rows={2}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            className={`mt-1 resize-y leading-relaxed ${inputClass}`}
          />
        </div>
        <div>
          <label className="block text-xs text-muted-foreground">
            Which character argues the opposite?
          </label>
          <input
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            className={`mt-1 ${inputClass}`}
          />
        </div>
      </div>
      <div className="mt-2 flex items-center gap-3">
        <button
          type="button"
          onClick={save}
          disabled={busy}
          className="rounded-lg border border-border px-3 py-1 text-xs text-foreground transition-colors hover:bg-muted disabled:opacity-50"
        >
          Save
        </button>
        <button
          type="button"
          onClick={remove}
          disabled={busy}
          className="text-xs text-muted-foreground hover:text-destructive"
        >
          Remove
        </button>
      </div>
    </div>
  );
}

function ThemeCreate({
  vault,
  bookId,
  onCreated,
}: {
  vault: string;
  bookId: string;
  onCreated: () => Promise<void>;
}) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [busy, setBusy] = useState(false);

  async function create() {
    if (!name.trim()) return;
    setBusy(true);
    try {
      await api(`${vault}/themes`, {
        method: 'POST',
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim() || null,
          book_id: bookId,
          theme_type: 'theme',
        }),
      });
      setName('');
      setDescription('');
      await onCreated();
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mt-4 rounded-xl border border-border p-4">
      <p className="text-xs uppercase tracking-wider text-muted-foreground">Add a theme</p>
      <div className="mt-3 grid gap-3">
        <div>
          <label className="block text-sm font-medium text-foreground">
            State the theme as a claim, not a topic.
          </label>
          <input
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="Mercy without memory is just forgetfulness."
            className={`mt-2 ${inputClass}`}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-foreground">
            Where in the story is it dramatised?
          </label>
          <textarea
            rows={2}
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            placeholder="Ch. 19 — she burns the ledger that would have cleared her."
            className={`mt-2 resize-y leading-relaxed ${inputClass}`}
          />
        </div>
        <div>
          <button
            type="button"
            onClick={create}
            disabled={busy || !name.trim()}
            className="rounded-lg border border-border px-3 py-1.5 text-sm text-foreground transition-colors hover:bg-muted disabled:opacity-50"
          >
            {busy ? 'Adding…' : 'Add theme'}
          </button>
        </div>
      </div>
    </div>
  );
}
