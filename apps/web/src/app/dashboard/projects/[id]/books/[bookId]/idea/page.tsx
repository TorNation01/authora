'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';

type Column = { key: string; label: string };

type FieldDef = {
  key: string;
  label: string;
  type: 'short' | 'text' | 'list' | 'rows';
  prompt: string;
  columns?: Column[];
  ai?: boolean;
};

type SectionDef = {
  key: string;
  number: number;
  title: string;
  intro: string;
  fields: FieldDef[];
};

type Completeness = {
  pct: number;
  filled: number;
  total: number;
  sections: Record<string, { title: string; filled: number; total: number; pct: number }>;
};

type Idea = {
  book_id: string;
  sections: Record<string, Record<string, string | string[]>>;
  version: number;
  completeness: Completeness;
};

type SaveState = 'idle' | 'saving' | 'saved' | 'error';

export default function BookIdeaPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;

  const [schema, setSchema] = useState<SectionDef[]>([]);
  const [idea, setIdea] = useState<Idea | null>(null);
  const [draft, setDraft] = useState<Record<string, Record<string, string>>>({});
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [error, setError] = useState<string | null>(null);
  const [busyField, setBusyField] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const dirty = useRef<Set<string>>(new Set());
  const draftRef = useRef<Record<string, Record<string, string>>>({});

  const load = useCallback(async () => {
    if (!projectId || !bookId) return;
    setLoading(true);
    try {
      const [schemaRes, ideaRes] = await Promise.all([
        api<{ sections: SectionDef[] }>('/api/v1/projects/book-idea/schema'),
        api<Idea>(`/api/v1/projects/${projectId}/books/${bookId}/book-idea`),
      ]);
      setSchema(schemaRes.sections);
      setIdea(ideaRes);
      const flat: Record<string, Record<string, string>> = {};
      for (const section of schemaRes.sections) {
        flat[section.key] = {};
        for (const field of section.fields) {
          const value = ideaRes.sections?.[section.key]?.[field.key];
          flat[section.key][field.key] =
            field.type === 'rows'
              ? JSON.stringify(Array.isArray(value) ? value : [])
              : Array.isArray(value)
                ? value.join('\n')
                : (value ?? '');
        }
      }
      setDraft(flat);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load this book idea.');
    } finally {
      setLoading(false);
    }
  }, [bookId, projectId]);

  useEffect(() => {
    void load();
  }, [load]);

  const completeness = useMemo(() => {
    let filled = 0;
    let total = 0;
    const perSection: Completeness['sections'] = {};
    for (const section of schema) {
      let sectionFilled = 0;
      for (const field of section.fields) {
        const raw = draft[section.key]?.[field.key] ?? '';
        if (field.type === 'rows') {
          try {
            const rows = JSON.parse(raw || '[]');
            if (Array.isArray(rows) && rows.some((row) => Object.values(row).some((v) => String(v ?? '').trim())))
              sectionFilled += 1;
          } catch {
            /* unparseable, count as empty */
          }
        } else if (raw.trim()) {
          sectionFilled += 1;
        }
      }
      filled += sectionFilled;
      total += section.fields.length;
      perSection[section.key] = {
        title: section.title,
        filled: sectionFilled,
        total: section.fields.length,
        pct: section.fields.length ? Math.round((sectionFilled / section.fields.length) * 100) : 0,
      };
    }
    return { pct: total ? Math.round((filled / total) * 100) : 0, filled, total, sections: perSection };
  }, [draft, schema]);

  async function saveSection(sectionKey: string) {
    if (!projectId || !bookId) return;
    const section = schema.find((s) => s.key === sectionKey);
    if (!section) return;

    const payload: Record<string, unknown> = {};
    for (const field of section.fields) {
      const value = draftRef.current[sectionKey]?.[field.key] ?? draft[sectionKey]?.[field.key] ?? '';
      payload[field.key] =
        field.type === 'rows'
          ? (() => {
              try {
                const parsed = JSON.parse(value || '[]');
                return Array.isArray(parsed)
                  ? parsed.filter((row) => Object.values(row).some((v) => String(v ?? '').trim()))
                  : [];
              } catch {
                return [];
              }
            })()
          : field.type === 'list'
          ? value
              .split('\n')
              .map((line) => line.replace(/^[-*]\s*/, '').trim())
              .filter(Boolean)
          : value;
    }

    setSaveState('saving');
    try {
      const updated = await api<Idea>(`/api/v1/projects/${projectId}/books/${bookId}/book-idea`, {
        method: 'PATCH',
        body: JSON.stringify({ sections: { [sectionKey]: payload } }),
      });
      setIdea(updated);
      setSaveState('saved');
    } catch (err) {
      setSaveState('error');
      setError(err instanceof Error ? err.message : 'Could not save that section.');
    }
  }

  async function draftWithAi(sectionKey: string, field: FieldDef) {
    if (!projectId || !bookId) return;
    setBusyField(`${sectionKey}.${field.key}`);
    try {
      const res = await api<{ text: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/book-idea/draft-field`,
        { method: 'POST', body: JSON.stringify({ section: sectionKey, field: field.key }) }
      );
      setDraft((current) => ({
        ...current,
        [sectionKey]: { ...current[sectionKey], [field.key]: res.text },
      }));
      dirty.current.add(`${sectionKey}.${field.key}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The draft did not come back.');
    } finally {
      setBusyField(null);
    }
  }

  if (loading) {
    return (
      <div className="mx-auto max-w-4xl px-6 py-10">
        <p className="text-sm text-muted-foreground">Loading the book idea…</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Layer one</p>
          <h1 className="mt-1 text-2xl font-semibold">Overall Book Idea</h1>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">
            The pitch, the spine and the promise — settled before the bible, the outline or a
            single sentence of prose.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`text-xs ${
              saveState === 'error' ? 'text-destructive' : 'text-muted-foreground'
            }`}
          >
            {saveState === 'saving'
              ? 'Saving…'
              : saveState === 'error'
                ? 'Not saved'
                : saveState === 'saved'
                  ? 'Saved'
                  : 'Saves when you leave a field'}
          </span>
          <div className="w-24 overflow-hidden rounded-full bg-muted">
            <div className="h-1.5 bg-foreground transition-all" style={{ width: `${completeness.pct}%` }} />
          </div>
          <span className="text-xs tabular-nums text-muted-foreground">
            {completeness.filled}/{completeness.total}
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <div className="space-y-5">
        {schema.map((section) => (
          <section key={section.key} className="rounded-xl border border-border p-5">
            <div className="mb-3 flex items-baseline justify-between gap-3">
              <div>
                <h2 className="text-sm font-semibold">
                  {section.number > 0 && (
                    <span className="mr-2 text-muted-foreground">{String(section.number).padStart(2, '0')}</span>
                  )}
                  {section.title}
                </h2>
                <p className="mt-0.5 text-xs text-muted-foreground">{section.intro}</p>
              </div>
              <span className="shrink-0 text-[11px] tabular-nums text-muted-foreground">
                {completeness.sections[section.key]?.filled ?? 0}/{section.fields.length}
              </span>
            </div>

            <div className="space-y-3">
              {section.fields.map((field) => {
                const value = draft[section.key]?.[field.key] ?? '';
                const busy = busyField === `${section.key}.${field.key}`;
                return (
                  <div key={field.key}>
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <label className="text-xs font-medium" htmlFor={`${section.key}-${field.key}`}>
                        {field.label}
                      </label>
                      {field.ai && (
                        <button
                          type="button"
                          onClick={() => void draftWithAi(section.key, field)}
                          disabled={busy}
                          className="shrink-0 rounded-md border border-border px-2 py-0.5 text-[10px] uppercase tracking-wider text-muted-foreground transition-colors hover:text-foreground disabled:opacity-50"
                        >
                          {busy ? 'Drafting…' : 'Draft with AI'}
                        </button>
                      )}
                    </div>
                    {field.type === 'rows' ? (
                      <RowsEditor
                        columns={field.columns || []}
                        rows={(() => {
                          try {
                            const parsed = JSON.parse(value || '[]');
                            return Array.isArray(parsed) ? parsed : [];
                          } catch {
                            return [];
                          }
                        })()}
                        onChange={(next) => {
                          const serialised = JSON.stringify(next);
                          draftRef.current = {
                            ...draftRef.current,
                            [section.key]: { ...draftRef.current[section.key], [field.key]: serialised },
                          };
                          setDraft((current) => ({
                            ...current,
                            [section.key]: { ...current[section.key], [field.key]: serialised },
                          }));
                        }}
                        onCommit={() => void saveSection(section.key)}
                      />
                    ) : field.type === 'short' ? (
                      <input
                        id={`${section.key}-${field.key}`}
                        value={value}
                        placeholder={field.prompt}
                        onChange={(e) =>
                          setDraft((current) => ({
                            ...current,
                            [section.key]: { ...current[section.key], [field.key]: e.target.value },
                          }))
                        }
                        onBlur={() => void saveSection(section.key)}
                        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-foreground/40"
                      />
                    ) : (
                      <textarea
                        id={`${section.key}-${field.key}`}
                        value={value}
                        rows={field.type === 'list' ? 3 : 4}
                        placeholder={field.prompt}
                        onChange={(e) =>
                          setDraft((current) => ({
                            ...current,
                            [section.key]: { ...current[section.key], [field.key]: e.target.value },
                          }))
                        }
                        onBlur={() => void saveSection(section.key)}
                        className="w-full resize-y rounded-lg border border-border bg-background px-3 py-2 text-sm leading-relaxed outline-none focus:border-foreground/40"
                      />
                    )}
                    <p className="mt-1 text-[11px] leading-snug text-muted-foreground">{field.prompt}</p>
                  </div>
                );
              })}
            </div>
          </section>
        ))}
      </div>

      <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4">
        <p className="text-xs text-muted-foreground">
          {idea ? `Version ${idea.version} · saved to this book` : 'Not saved yet'}
        </p>
        <div className="flex gap-3 text-xs">
          <Link
            href={`/dashboard/projects/${projectId}/books/${bookId}/bible`}
            className="rounded-lg border border-border px-3 py-1.5 hover:bg-muted"
          >
            Next: the Book Bible →
          </Link>
        </div>
      </div>
    </div>
  );
}

function RowsEditor({
  columns,
  rows,
  onChange,
  onCommit,
}: {
  columns: Column[];
  rows: Record<string, string>[];
  onChange: (next: Record<string, string>[]) => void;
  onCommit: () => void;
}) {
  function update(index: number, key: string, value: string) {
    onChange(rows.map((row, i) => (i === index ? { ...row, [key]: value } : row)));
  }
  return (
    <div className="space-y-3">
      {rows.map((row, index) => (
        <div key={index} className="rounded-xl border border-border p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-[11px] uppercase tracking-wider text-muted-foreground">
              Theme {index + 1}
            </span>
            <button
              type="button"
              onClick={() => {
                onChange(rows.filter((_, i) => i !== index));
                onCommit();
              }}
              className="text-[11px] text-muted-foreground hover:text-destructive"
            >
              Remove
            </button>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            {columns.map((col) => (
              <label key={col.key} className="block">
                <span className="mb-1 block text-[11px] uppercase tracking-wider text-muted-foreground">
                  {col.label}
                </span>
                <input
                  value={row[col.key] ?? ''}
                  onChange={(e) => update(index, col.key, e.target.value)}
                  onBlur={onCommit}
                  className="w-full rounded-lg border border-border bg-background px-2 py-1.5 text-sm outline-none focus:border-foreground/40"
                />
              </label>
            ))}
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={() =>
          onChange([...rows, Object.fromEntries(columns.map((c) => [c.key, '']))])
        }
        className="rounded-lg border border-dashed border-border px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
      >
        + Add theme
      </button>
    </div>
  );
}
