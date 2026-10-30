'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';

type FieldDef = {
  key: string;
  label: string;
  type: 'short' | 'text' | 'list' | 'rows';
  prompt: string;
  columns?: { key: string; label: string }[];
};

type SectionDef = {
  key: string;
  number: number;
  title: string;
  intro: string;
  fields: FieldDef[];
};

type SeriesBible = {
  project_id: string;
  sections: Record<string, Record<string, unknown>>;
  section_status: Record<string, string>;
  version: number;
  completeness: {
    pct: number;
    filled: number;
    total: number;
    sections: Record<string, { title: string; filled: number; total: number; pct: number }>;
  };
};

type SaveState = 'idle' | 'saving' | 'saved' | 'error';

const STATUS_OPTIONS = [
  { value: 'working', label: 'Working' },
  { value: 'locked', label: 'Locked' },
  { value: 'undecided', label: 'Undecided' },
];

export default function SeriesBiblePage() {
  const params = useParams<{ id: string }>();
  const projectId = params?.id as string;
  const seriesPath = `/api/v1/projects/${projectId}/series`;

  const [schema, setSchema] = useState<SectionDef[]>([]);
  const [bible, setBible] = useState<SeriesBible | null>(null);
  const [active, setActive] = useState<string>('series_identity');
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [s, b] = await Promise.all([
          api<{ sections: SectionDef[] }>('/api/v1/projects/series/schema'),
          api<SeriesBible>(seriesPath),
        ]);
        setSchema(s.sections);
        setBible(b);
        const wanted = new URLSearchParams(window.location.search).get('section');
        if (wanted && s.sections.some((x) => x.key === wanted)) setActive(wanted);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not load the series bible.');
      } finally {
        setLoading(false);
      }
    })();
  }, [seriesPath]);

  const save = useCallback(
    async (sections: Record<string, Record<string, unknown>>, status?: Record<string, string>) => {
      setSaveState('saving');
      try {
        const updated = await api<SeriesBible>(seriesPath, {
          method: 'PATCH',
          body: JSON.stringify({ sections, section_status: status }),
        });
        setBible(updated);
        setSaveState('saved');
        setTimeout(() => setSaveState('idle'), 2000);
      } catch {
        setSaveState('error');
      }
    },
    [seriesPath]
  );

  const queueSave = useCallback(
    (sections: Record<string, Record<string, unknown>>, status?: Record<string, string>) => {
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(() => void save(sections, status), 1100);
    },
    [save]
  );

  function setValue(sectionKey: string, fieldKey: string, value: unknown) {
    setBible((current) => {
      if (!current) return current;
      const sections = {
        ...current.sections,
        [sectionKey]: { ...(current.sections[sectionKey] || {}), [fieldKey]: value },
      };
      queueSave({ [sectionKey]: sections[sectionKey] });
      return { ...current, sections };
    });
  }

  function setSectionStatus(sectionKey: string, value: string) {
    setBible((current) => {
      if (!current) return current;
      const section_status = { ...current.section_status, [sectionKey]: value };
      queueSave({}, section_status);
      return { ...current, section_status };
    });
  }

  const section = useMemo(() => schema.find((s) => s.key === active) ?? schema[0], [schema, active]);

  if (loading) return <p className="text-sm text-muted-foreground">Loading the series bible…</p>;
  if (error) return <p className="text-sm text-destructive">{error}</p>;
  if (!bible || !section) return null;

  const values = bible.sections[section.key] || {};
  const completion = bible.completeness.sections[section.key];
  const status = bible.section_status[section.key] || 'working';

  return (
    <div className="min-w-0">
      <header className="mb-6">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <h1 className="font-serif text-2xl font-bold text-foreground">Series Bible</h1>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              Canon that outranks any single book. Fill this once and every book in the series
              inherits it — the AI reads it first, and the process step{' '}
              <span className="text-foreground">Gather existing canon</span> is measured from here.
            </p>
          </div>
          <div className="text-right">
            <p className="font-serif text-3xl text-foreground">{bible.completeness.pct}%</p>
            <p className="text-xs uppercase tracking-wider text-muted-foreground">
              {bible.completeness.filled} of {bible.completeness.total} answered
            </p>
          </div>
        </div>
        <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-muted">
          <div
            className="h-full rounded-full bg-primary transition-all"
            style={{ width: `${bible.completeness.pct}%` }}
          />
        </div>
      </header>

      <div className="grid gap-8 lg:grid-cols-[240px_minmax(0,1fr)]">
        <nav className="lg:sticky lg:top-4 lg:self-start">
          <ol className="flex gap-1 overflow-x-auto pb-2 lg:flex-col lg:overflow-visible lg:pb-0">
            {schema.map((s) => {
              const c = bible.completeness.sections[s.key];
              const isActive = s.key === section.key;
              return (
                <li key={s.key} className="shrink-0 lg:shrink">
                  <button
                    type="button"
                    onClick={() => setActive(s.key)}
                    className={`flex w-full items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                      isActive
                        ? 'bg-primary/10 font-medium text-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`}
                  >
                    <span className="truncate">
                      <span className="mr-2 text-xs opacity-60">{s.number}</span>
                      {s.title}
                    </span>
                    <span
                      className={`text-[10px] tabular-nums ${
                        c?.pct === 100 ? 'text-emerald-500' : 'text-muted-foreground'
                      }`}
                    >
                      {c?.pct ?? 0}%
                    </span>
                  </button>
                </li>
              );
            })}
          </ol>
        </nav>

        <section className="min-w-0">
          <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border pb-4">
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground">
                Section {section.number} of {schema.length}
              </p>
              <h2 className="mt-1 font-serif text-xl font-semibold text-foreground">{section.title}</h2>
              <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{section.intro}</p>
            </div>
            <div className="flex items-center gap-2">
              <label className="text-xs uppercase tracking-wider text-muted-foreground" htmlFor="canon">
                Canon
              </label>
              <select
                id="canon"
                value={status}
                onChange={(e) => setSectionStatus(section.key, e.target.value)}
                className="rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
              >
                {STATUS_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mt-6 space-y-7">
            {section.fields.map((field) => (
              <div key={field.key}>
                <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
                  <label
                    className="text-sm font-medium text-foreground"
                    htmlFor={`${section.key}-${field.key}`}
                  >
                    {field.label}
                  </label>
                  {status === 'locked' && (
                    <span className="text-[10px] uppercase tracking-wider text-emerald-600">locked</span>
                  )}
                </div>
                <p className="mb-2 text-xs leading-relaxed text-muted-foreground">{field.prompt}</p>

                {field.type === 'short' && (
                  <input
                    id={`${section.key}-${field.key}`}
                    value={String(values[field.key] ?? '')}
                    onChange={(e) => setValue(section.key, field.key, e.target.value)}
                    className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
                  />
                )}

                {field.type === 'text' && (
                  <textarea
                    id={`${section.key}-${field.key}`}
                    value={String(values[field.key] ?? '')}
                    onChange={(e) => setValue(section.key, field.key, e.target.value)}
                    rows={4}
                    className="w-full resize-y rounded-lg border border-border bg-background px-3 py-2 text-sm leading-relaxed"
                  />
                )}

                {field.type === 'list' && (
                  <ListEditor
                    value={(values[field.key] as string[]) || []}
                    onChange={(next) => setValue(section.key, field.key, next)}
                  />
                )}

                {field.type === 'rows' && (
                  <RowsEditor
                    columns={field.columns || []}
                    rows={(values[field.key] as Record<string, string>[]) || []}
                    onChange={(next) => setValue(section.key, field.key, next)}
                  />
                )}
              </div>
            ))}
          </div>

          <div className="mt-8 flex flex-wrap items-center gap-3 border-t border-border pt-4 text-xs text-muted-foreground">
            <SaveBadge state={saveState} />
            <span>Autosaves as you type. Canon here never rewrites a chapter.</span>
            <span className="ml-auto tabular-nums">
              {completion?.filled}/{completion?.total} in this section
            </span>
          </div>

          <div className="mt-6 rounded-xl border border-border bg-muted/30 p-4 text-xs text-muted-foreground">
            The book-level detail lives in each book&apos;s own bible.{' '}
            <Link
              href={`/dashboard/projects/${projectId}`}
              className="font-medium text-foreground underline underline-offset-4"
            >
              Back to the project
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}

function SaveBadge({ state }: { state: SaveState }) {
  if (state === 'saving') return <span className="text-muted-foreground">Saving…</span>;
  if (state === 'saved') return <span className="text-emerald-600">Saved</span>;
  if (state === 'error') return <span className="text-destructive">Could not save — retry</span>;
  return <span className="text-muted-foreground">All changes saved</span>;
}

function ListEditor({ value, onChange }: { value: string[]; onChange: (next: string[]) => void }) {
  const [draft, setDraft] = useState('');
  function add() {
    const item = draft.trim();
    if (!item) return;
    onChange([...value, item]);
    setDraft('');
  }
  return (
    <div>
      <div className="flex gap-2">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              add();
            }
          }}
          placeholder="Type one and press Enter"
          className="flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm"
        />
        <button
          type="button"
          onClick={add}
          className="rounded-lg border border-border px-3 py-2 text-sm hover:bg-muted"
        >
          Add
        </button>
      </div>
      {value.length > 0 && (
        <ul className="mt-2 flex flex-wrap gap-2">
          {value.map((item, i) => (
            <li
              key={`${item}-${i}`}
              className="flex items-center gap-2 rounded-full border border-border bg-muted/50 px-3 py-1 text-xs"
            >
              <span>{item}</span>
              <button
                type="button"
                aria-label={`Remove ${item}`}
                onClick={() => onChange(value.filter((_, idx) => idx !== i))}
                className="text-muted-foreground hover:text-destructive"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function RowsEditor({
  columns,
  rows,
  onChange,
}: {
  columns: { key: string; label: string }[];
  rows: Record<string, string>[];
  onChange: (next: Record<string, string>[]) => void;
}) {
  function update(index: number, key: string, value: string) {
    onChange(rows.map((row, i) => (i === index ? { ...row, [key]: value } : row)));
  }
  return (
    <div className="space-y-3">
      {rows.map((row, index) => (
        <div key={index} className="rounded-xl border border-border p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs uppercase tracking-wider text-muted-foreground">
              Entry {index + 1}
            </span>
            <button
              type="button"
              onClick={() => onChange(rows.filter((_, i) => i !== index))}
              className="text-xs text-muted-foreground hover:text-destructive"
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
                  className="w-full rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
                />
              </label>
            ))}
          </div>
        </div>
      ))}
      <button
        type="button"
        onClick={() => onChange([...rows, Object.fromEntries(columns.map((c) => [c.key, '']))])}
        className="rounded-lg border border-dashed border-border px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground"
      >
        + Add entry
      </button>
    </div>
  );
}
