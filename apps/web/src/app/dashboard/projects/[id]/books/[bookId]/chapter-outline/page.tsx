'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';

type FieldDef = {
  key: string;
  label: string;
  type: 'short' | 'text' | 'list';
  prompt: string;
  ai?: boolean;
};

type SectionDef = {
  key: string;
  number: number;
  title: string;
  intro: string;
  fields: FieldDef[];
};

type OutlineSheet = {
  id: string;
  sections: Record<string, Record<string, string | string[]>>;
  filled: number;
  total: number;
  version: number;
  turning_point_id: string | null;
};

type ChapterRow = {
  chapter_id: string;
  title: string;
  number: number;
  sort_order: number;
  act_id: string | null;
  outline: OutlineSheet | null;
};

type OutlineResponse = {
  book_id: string;
  book_title: string;
  chapters: ChapterRow[];
  turning_points: { id: string; title: string; sort_order: number }[];
  progress: { filled: number; total: number; pct: number; chapters: number };
};

export default function ChapterOutlinePage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;

  const [sections, setSections] = useState<SectionDef[]>([]);
  const [chapters, setChapters] = useState<ChapterRow[]>([]);
  const [points, setPoints] = useState<{ id: string; title: string; sort_order: number }[]>([]);
  const [bookTitle, setBookTitle] = useState('');
  const [selected, setSelected] = useState<string | null>(null);
  const [draft, setDraft] = useState<Record<string, Record<string, string>>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const hydrateDraft = (row: ChapterRow | undefined, schema: SectionDef[]) => {
    if (!row) return;
    const body: Record<string, string> = {};
    for (const section of schema) {
      for (const field of section.fields) {
        const value = row.outline?.sections?.[section.key]?.[field.key];
        body[field.key] = Array.isArray(value) ? value.join('\n') : (value ?? '');
      }
    }
    setDraft((current) => ({ ...current, [row.chapter_id]: body }));
  };

  const load = useCallback(async () => {
    if (!projectId || !bookId) return;
    setLoading(true);
    try {
      const [schemaRes, outlineRes] = await Promise.all([
        api<{ sections: SectionDef[] }>('/api/v1/projects/chapter-outline/schema'),
        api<OutlineResponse>(`/api/v1/projects/${projectId}/books/${bookId}/chapter-outline`),
      ]);
      setSections(schemaRes.sections);
      setChapters(outlineRes.chapters);
      setPoints(outlineRes.turning_points);
      setBookTitle(outlineRes.book_title);
      for (const row of outlineRes.chapters) hydrateDraft(row, schemaRes.sections);
      setSelected((current) => current ?? outlineRes.chapters[0]?.chapter_id ?? null);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the chapter outline.');
    } finally {
      setLoading(false);
    }
  }, [bookId, projectId]);

  useEffect(() => {
    void load();
  }, [load]);

  const active = useMemo(
    () => chapters.find((row) => row.chapter_id === selected) ?? null,
    [chapters, selected]
  );

  const progress = useMemo(() => {
    let filled = 0;
    let total = 0;
    for (const row of chapters) {
      for (const section of sections) {
        for (const field of section.fields) {
          total += 1;
          if ((draft[row.chapter_id]?.[field.key] ?? '').trim()) filled += 1;
        }
      }
    }
    return { filled, total, pct: total ? Math.round((filled / total) * 100) : 0 };
  }, [chapters, draft, sections]);

  async function patch(chapterId: string, body: Record<string, unknown>) {
    if (!projectId || !bookId) return;
    try {
      const updated = await api<OutlineSheet>(
        `/api/v1/projects/${projectId}/books/${bookId}/chapter-outline/${chapterId}`,
        { method: 'PATCH', body: JSON.stringify(body) }
      );
      setChapters((current) =>
        current.map((row) =>
          row.chapter_id === chapterId ? { ...row, outline: updated } : row
        )
      );
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save that.');
      return null;
    }
  }

  async function saveField(chapterId: string, field: FieldDef) {
    const value = draft[chapterId]?.[field.key] ?? '';
    const payload =
      field.type === 'list'
        ? value
            .split('\n')
            .map((line) => line.replace(/^[-*]\s*/, '').trim())
            .filter(Boolean)
        : value;
    await patch(chapterId, { fields: { [field.key]: payload } });
  }

  async function draftField(chapterId: string, field: FieldDef) {
    if (!projectId || !bookId) return;
    setBusy(`${chapterId}.${field.key}`);
    try {
      const res = await api<{ text: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/chapter-outline/${chapterId}/draft-field`,
        { method: 'POST', body: JSON.stringify({ field: field.key }) }
      );
      setDraft((current) => ({
        ...current,
        [chapterId]: { ...current[chapterId], [field.key]: res.text },
      }));
      const payload =
        field.type === 'list'
          ? res.text
              .split('\n')
              .map((line) => line.replace(/^[-*]\s+/g, '').replace(/^[-*]\s*/, '').trim())
              .filter(Boolean)
          : res.text;
      await patch(chapterId, { fields: { [field.key]: payload } });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The draft did not come back.');
    } finally {
      setBusy(null);
    }
  }

  if (loading) {
    return <p className="py-10 text-sm text-muted-foreground">Reading the map…</p>;
  }

  if (chapters.length === 0) {
    return (
      <div className="mx-auto max-w-3xl py-10">
        <h1 className="text-2xl font-semibold">Chapter Outline</h1>
        <p className="mt-3 text-sm text-muted-foreground">
          This book has no chapters yet. Add chapters on the Plan page first — the outline maps
          chapters that exist, it does not invent them.
        </p>
        <Link
          href={`/dashboard/projects/${projectId}/books/${bookId}/plan`}
          className="mt-5 inline-block rounded-lg border border-border px-4 py-2 text-sm"
        >
          Go to Plan →
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Layer four</p>
          <h1 className="mt-1 text-2xl font-semibold">Chapter Outline</h1>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">
            {bookTitle ? `${bookTitle} — ` : ''}the chapter-by-chapter map. Detailed enough to show
            a pacing problem, loose enough that the prose can grow.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-24 overflow-hidden rounded-full bg-muted">
            <div className="h-1.5 bg-foreground transition-all" style={{ width: `${progress.pct}%` }} />
          </div>
          <span className="text-xs tabular-nums text-muted-foreground">
            {progress.pct}% · {chapters.length} chapters
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-[220px_1fr]">
        <aside className="space-y-1">
          {chapters.map((row) => {
            const filled = sections
              .flatMap((section) => section.fields)
              .filter((field) => (draft[row.chapter_id]?.[field.key] ?? '').trim()).length;
            const total = sections.reduce((sum, section) => sum + section.fields.length, 0);
            const isActive = row.chapter_id === selected;
            return (
              <button
                key={row.chapter_id}
                type="button"
                onClick={() => setSelected(row.chapter_id)}
                className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                  isActive
                    ? 'border-foreground/40 bg-muted font-medium'
                    : 'border-transparent hover:bg-muted/60'
                }`}
              >
                <span className="block truncate">{row.number}. {row.title}</span>
                <span className="mt-0.5 block text-[11px] tabular-nums text-muted-foreground">
                  {filled}/{total}
                </span>
              </button>
            );
          })}
        </aside>

        <div>
          {active && (
            <div className="space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border px-4 py-3">
                <div>
                  <p className="text-[11px] uppercase tracking-wider text-muted-foreground">
                    Chapter {active.number}
                  </p>
                  <h2 className="text-base font-medium">{active.title}</h2>
                </div>
                {points.length > 0 && (
                  <select
                    value={active.outline?.turning_point_id ?? ''}
                    onChange={(e) =>
                      void patch(active.chapter_id, {
                        turning_point_id: e.target.value || null,
                      } as Record<string, unknown>)
                    }
                    className="rounded-md border border-border bg-background px-2 py-1 text-xs"
                  >
                    <option value="">No turning point</option>
                    {points.map((point) => (
                      <option key={point.id} value={point.id}>
                        {point.sort_order + 1}. {point.title}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              {sections.map((section) => (
                <section key={section.key} className="rounded-xl border border-border">
                  <div className="border-b border-border px-4 py-3">
                    <h3 className="text-sm font-medium">
                      {section.number + 1}. {section.title}
                    </h3>
                    <p className="mt-0.5 text-xs text-muted-foreground">{section.intro}</p>
                  </div>
                  <div className="grid gap-4 px-4 py-4 md:grid-cols-2">
                    {section.fields.map((field) => {
                      const value = draft[active.chapter_id]?.[field.key] ?? '';
                      const isBusy = busy === `${active.chapter_id}.${field.key}`;
                      const wide = field.type !== 'short';
                      return (
                        <div key={field.key} className={wide ? 'md:col-span-2' : ''}>
                          <div className="mb-1 flex items-center justify-between gap-2">
                            <label className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                              {field.label}
                            </label>
                            {field.ai && (
                              <button
                                type="button"
                                onClick={() => void draftField(active.chapter_id, field)}
                                disabled={isBusy}
                                className="rounded-md border border-border px-2 py-0.5 text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground disabled:opacity-50"
                              >
                                {isBusy ? '…' : 'Draft'}
                              </button>
                            )}
                          </div>
                          <textarea
                            value={value}
                            rows={field.type === 'list' ? 3 : field.type === 'text' ? 2 : 1}
                            placeholder={field.prompt}
                            onChange={(e) =>
                              setDraft((current) => ({
                                ...current,
                                [active.chapter_id]: {
                                  ...current[active.chapter_id],
                                  [field.key]: e.target.value,
                                },
                              }))
                            }
                            onBlur={() => void saveField(active.chapter_id, field)}
                            className="w-full resize-y rounded-lg border border-border bg-background px-2.5 py-1.5 text-sm leading-relaxed outline-none focus:border-foreground/40"
                          />
                        </div>
                      );
                    })}
                  </div>
                </section>
              ))}

              <div className="flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4 text-xs">
                <p className="text-muted-foreground">Saves when you leave a field.</p>
                <Link
                  href={`/dashboard/projects/${projectId}/books/${bookId}/brief`}
                  className="rounded-lg border border-border px-3 py-1.5 hover:bg-muted"
                >
                  Next: the chapter brief →
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
