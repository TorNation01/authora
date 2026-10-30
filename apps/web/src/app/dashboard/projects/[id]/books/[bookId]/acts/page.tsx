'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { BookNav } from '@/components/bible/nav';

type ChapterRef = { id: string; title: string; number: number; word_count: number };
type Act = {
  id: string;
  title: string;
  summary: string | null;
  sort_order: number;
  color: string | null;
  target_words: number | null;
  chapters: ChapterRef[];
};

export default function ActsPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = `/api/v1/projects/${projectId}/books/${bookId}/acts`;

  const [acts, setActs] = useState<Act[]>([]);
  const [unassigned, setUnassigned] = useState<ChapterRef[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await api<{ acts: Act[]; unassigned: ChapterRef[] }>(base);
      setActs(data.acts);
      setUnassigned(data.unassigned);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the acts.');
    } finally {
      setLoading(false);
    }
  }, [base]);

  useEffect(() => {
    if (projectId && bookId) void load();
  }, [load, projectId, bookId]);

  async function addAct() {
    setBusy(true);
    try {
      await api(base, {
        method: 'POST',
        body: JSON.stringify({ title: `Act ${acts.length + 1}`, summary: '' }),
      });
      await load();
    } finally {
      setBusy(false);
    }
  }

  async function patchAct(act: Act, fields: Partial<Act>) {
    setActs((current) => current.map((a) => (a.id === act.id ? { ...a, ...fields } : a)));
    await api(`${base}/${act.id}`, { method: 'PATCH', body: JSON.stringify(fields) });
  }

  async function removeAct(act: Act) {
    if (!confirm(`Delete "${act.title}"? Its chapters return to the unassigned list; nothing is deleted.`)) return;
    await api(`${base}/${act.id}`, { method: 'DELETE' });
    await load();
  }

  async function move(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= acts.length) return;
    const next = [...acts];
    [next[index], next[target]] = [next[target], next[index]];
    setActs(next);
    await api(`${base}/reorder`, { method: 'POST', body: JSON.stringify({ order: next.map((a) => a.id) }) });
  }

  async function assign(chapterId: string, actId: string | null) {
    await api(
      `/api/v1/projects/${projectId}/books/${bookId}/chapters/${chapterId}/act${actId ? `?act_id=${actId}` : ''}`,
      { method: 'PATCH' }
    );
    await load();
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading acts…</p>;
  if (error) return <p className="text-sm text-destructive">{error}</p>;

  const totalWords = acts.reduce((sum, a) => sum + a.chapters.reduce((s, c) => s + (c.word_count || 0), 0), 0);
  const unassignedWords = unassigned.reduce((s, c) => s + (c.word_count || 0), 0);

  return (
    <div className="max-w-5xl p-6 lg:p-8">
      <BookNav projectId={projectId} bookId={bookId} className="mb-6" />
      <header className="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-serif text-2xl font-bold text-foreground">Acts</h1>
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
            The book&rsquo;s spine. As many acts as the story needs — three, five, or twenty. Drag
            chapters into the act they belong to, or rename an act to whatever you call it.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{totalWords.toLocaleString()} words placed</span>
          <button
            type="button"
            onClick={addAct}
            disabled={busy}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary-hover disabled:opacity-50"
          >
            + Add act
          </button>
        </div>
      </header>

      <div className="space-y-4">
        {acts.map((act, index) => {
          const words = act.chapters.reduce((s, c) => s + (c.word_count || 0), 0);
          return (
            <section key={act.id} className="rounded-xl border border-border">
              <div className="flex flex-wrap items-center gap-3 border-b border-border px-4 py-3">
                <span className="font-mono text-xs text-muted-foreground">{String(index + 1).padStart(2, '0')}</span>
                <input
                  value={act.title}
                  onChange={(e) => setActs((cur) => cur.map((a) => (a.id === act.id ? { ...a, title: e.target.value } : a)))}
                  onBlur={(e) => patchAct(act, { title: e.target.value })}
                  className="min-w-[160px] flex-1 rounded-md border border-transparent bg-transparent px-1 py-0.5 font-serif text-lg font-semibold hover:border-border focus:border-border focus:outline-none"
                />
                <span className="text-xs text-muted-foreground">
                  {act.chapters.length} chapter{act.chapters.length === 1 ? '' : 's'} · {words.toLocaleString()} words
                </span>
                <div className="flex items-center gap-1">
                  <button
                    type="button"
                    onClick={() => move(index, -1)}
                    disabled={index === 0}
                    className="rounded border border-border px-2 py-1 text-xs disabled:opacity-30"
                    aria-label="Move up"
                  >
                    ↑
                  </button>
                  <button
                    type="button"
                    onClick={() => move(index, 1)}
                    disabled={index === acts.length - 1}
                    className="rounded border border-border px-2 py-1 text-xs disabled:opacity-30"
                    aria-label="Move down"
                  >
                    ↓
                  </button>
                  <button
                    type="button"
                    onClick={() => removeAct(act)}
                    className="rounded border border-border px-2 py-1 text-xs text-muted-foreground hover:text-destructive"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="px-4 py-3">
                <textarea
                  value={act.summary || ''}
                  onChange={(e) => setActs((cur) => cur.map((a) => (a.id === act.id ? { ...a, summary: e.target.value } : a)))}
                  onBlur={(e) => patchAct(act, { summary: e.target.value })}
                  rows={2}
                  placeholder="What this act does — the promise it makes and the turn it takes."
                  className="mb-3 w-full resize-y rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                />
                <ul className="space-y-1">
                  {act.chapters.map((ch) => (
                    <li key={ch.id} className="flex items-center gap-3 rounded-lg bg-muted/40 px-3 py-1.5 text-sm">
                      <span className="font-mono text-xs text-muted-foreground">{ch.number}</span>
                      <span className="min-w-0 flex-1 truncate">{ch.title}</span>
                      <span className="text-xs text-muted-foreground">{(ch.word_count || 0).toLocaleString()}w</span>
                      <select
                        value={act.id}
                        onChange={(e) => assign(ch.id, e.target.value || null)}
                        className="rounded border border-border bg-background px-1 py-0.5 text-xs"
                      >
                        {acts.map((a) => (
                          <option key={a.id} value={a.id}>
                            {a.title}
                          </option>
                        ))}
                        <option value="">Unassigned</option>
                      </select>
                    </li>
                  ))}
                  {act.chapters.length === 0 && (
                    <li className="px-1 py-2 text-xs text-muted-foreground">No chapters in this act yet.</li>
                  )}
                </ul>
              </div>
            </section>
          );
        })}
      </div>

      {unassigned.length > 0 && (
        <section className="mt-8 rounded-xl border border-dashed border-border p-4">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="font-serif text-base font-semibold">Unassigned chapters</h2>
            <span className="text-xs text-muted-foreground">{unassignedWords.toLocaleString()} words</span>
          </div>
          <ul className="space-y-1">
            {unassigned.map((ch) => (
              <li key={ch.id} className="flex items-center gap-3 rounded-lg px-2 py-1.5 text-sm">
                <span className="font-mono text-xs text-muted-foreground">{ch.number}</span>
                <span className="min-w-0 flex-1 truncate">{ch.title}</span>
                <select
                  defaultValue=""
                  onChange={(e) => assign(ch.id, e.target.value || null)}
                  className="rounded border border-border bg-background px-1 py-0.5 text-xs"
                >
                  <option value="">Move to…</option>
                  {acts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.title}
                    </option>
                  ))}
                </select>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
