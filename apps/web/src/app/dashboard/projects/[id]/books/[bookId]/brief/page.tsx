'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { api } from '@/lib/api';

type FieldDef = {
  key: string;
  label: string;
  type: 'short' | 'text' | 'list' | 'rows' | 'checks';
  prompt: string;
  ai?: boolean;
  columns?: { key: string; label: string }[];
  items?: string[];
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

type Brief = {
  chapter_id: string;
  book_id: string;
  sections: Record<string, Record<string, unknown>>;
  section_status: Record<string, string>;
  version: number;
  completeness: Completeness;
};

type BriefRow = {
  chapter_id: string;
  title: string;
  sort_order: number;
  act_title: string | null;
  word_count: number | null;
  pct: number;
  filled: number;
  total: number;
};

type SaveState = 'idle' | 'saving' | 'saved' | 'error';

const STATUS_OPTIONS = [
  { value: 'working', label: 'Working' },
  { value: 'locked', label: 'Locked' },
  { value: 'undecided', label: 'Undecided' },
];

export default function ChapterBriefPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const search = useSearchParams();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = `/api/v1/projects/${projectId}/books/${bookId}/chapter-briefs`;

  const [schema, setSchema] = useState<SectionDef[]>([]);
  const [briefs, setBriefs] = useState<BriefRow[]>([]);
  const [activeChapter, setActiveChapter] = useState<string>('');
  const [brief, setBrief] = useState<Brief | null>(null);
  const [active, setActive] = useState<string>('purpose');
  const [saveState, setSaveState] = useState<SaveState>('idle');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [drafting, setDrafting] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load the questionnaire and the chapter list.
  useEffect(() => {
    (async () => {
      try {
        const [s, list] = await Promise.all([
          api<{ sections: SectionDef[] }>('/api/v1/projects/chapter-brief/schema'),
          api<BriefRow[]>(base),
        ]);
        setSchema(s.sections);
        setBriefs(list);
        const wanted = search?.get('chapter');
        const first = wanted && list.some((c) => c.chapter_id === wanted) ? wanted : list[0]?.chapter_id;
        if (first) setActiveChapter(first);
        else setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Could not load the chapter briefs.');
        setLoading(false);
      }
    })();
  }, [base, search]);

  // Load the brief for the selected chapter.
  useEffect(() => {
    if (!activeChapter) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const b = await api<Brief>(`${base}/${activeChapter}`);
        if (!cancelled) {
          setBrief(b);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Could not load this brief.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [activeChapter, base]);

  const refreshList = useCallback(async () => {
    try {
      const list = await api<BriefRow[]>(base);
      setBriefs(list);
    } catch {
      /* the list is a convenience; a failure here must not break saving */
    }
  }, [base]);

  const save = useCallback(
    async (sections: Record<string, Record<string, unknown>>, status?: Record<string, string>) => {
      if (!activeChapter) return;
      setSaveState('saving');
      try {
        const updated = await api<Brief>(`${base}/${activeChapter}`, {
          method: 'PATCH',
          body: JSON.stringify({ sections, section_status: status }),
        });
        setBrief(updated);
        setSaveState('saved');
        setTimeout(() => setSaveState('idle'), 1800);
        void refreshList();
      } catch {
        setSaveState('error');
      }
    },
    [activeChapter, base, refreshList]
  );

  const queueSave = useCallback(
    (sections: Record<string, Record<string, unknown>>, status?: Record<string, string>) => {
      if (timer.current) clearTimeout(timer.current);
      timer.current = setTimeout(() => void save(sections, status), 1000);
    },
    [save]
  );

  function setValue(sectionKey: string, fieldKey: string, value: unknown) {
    setBrief((current) => {
      if (!current) return current;
      const sectionBody = { ...(current.sections[sectionKey] || {}), [fieldKey]: value };
      const sections = { ...current.sections, [sectionKey]: sectionBody };
      queueSave({ [sectionKey]: sectionBody });
      return { ...current, sections };
    });
  }

  function setSectionStatus(sectionKey: string, value: string) {
    setBrief((current) => {
      if (!current) return current;
      const section_status = { ...current.section_status, [sectionKey]: value };
      queueSave({}, section_status);
      return { ...current, section_status };
    });
  }

  async function prefill() {
    if (!activeChapter) return;
    setSaveState('saving');
    try {
      const updated = await api<Brief>(`${base}/${activeChapter}/prefill`, { method: 'POST' });
      setBrief(updated);
      setSaveState('saved');
      setTimeout(() => setSaveState('idle'), 1800);
      void refreshList();
    } catch {
      setSaveState('error');
    }
  }

  async function draftField(sectionKey: string, fieldKey: string) {
    if (!activeChapter) return;
    setDrafting(`${sectionKey}:${fieldKey}`);
    try {
      const res = await api<{ text: string }>(`${base}/${activeChapter}/draft-field`, {
        method: 'POST',
        body: JSON.stringify({ section: sectionKey, field: fieldKey }),
      });
      const text = (res.text || '').trim();
      if (!text) return;
      if (sectionKey && text) {
        const existing = brief?.sections[sectionKey]?.[fieldKey];
        const isList = Array.isArray(existing);
        if (isList) {
          const items = text
            .split('\n')
            .map((line) => line.replace(/^[-*•]\s*/, '').trim())
            .filter(Boolean);
          setValue(sectionKey, fieldKey, items);
        } else {
          setValue(sectionKey, fieldKey, text);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The AI could not draft that field.');
    } finally {
      setDrafting(null);
    }
  }

  const section = useMemo(() => schema.find((s) => s.key === active) ?? schema[0], [schema, active]);
  const chapter = briefs.find((c) => c.chapter_id === activeChapter);

  if (error && !brief) return <p className="text-sm text-destructive">{error}</p>;
  if (!schema.length) return <p className="text-sm text-muted-foreground">Loading the brief…</p>;
  if (!briefs.length)
    return (
      <p className="text-sm text-muted-foreground">
        This book has no chapters yet. Add one on the book page and the brief will appear here.
      </p>
    );

  const values = brief?.sections[section?.key] || {};
  const completion = brief?.completeness.sections[section?.key];
  const status = brief?.section_status[section?.key] || 'working';

  return (
    <div className="grid min-w-0 gap-8 lg:grid-cols-[250px_minmax(0,1fr)]">
      <aside className="lg:sticky lg:top-4 lg:self-start">
        <div className="mb-3 flex items-baseline justify-between">
          <h1 className="font-serif text-lg font-semibold text-foreground">Chapter briefs</h1>
          <span className="text-xs text-muted-foreground">{briefs.length} chapters</span>
        </div>
        <ol className="max-h-[70vh] space-y-1 overflow-y-auto pr-1">
          {briefs.map((c) => {
            const isActive = c.chapter_id === activeChapter;
            return (
              <li key={c.chapter_id}>
                <button
                  type="button"
                  onClick={() => setActiveChapter(c.chapter_id)}
                  className={`w-full rounded-lg px-3 py-2 text-left text-sm transition-colors ${
                    isActive
                      ? 'bg-primary/10 font-medium text-foreground'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`}
                >
                  <span className="flex items-center justify-between gap-2">
                    <span className="truncate">{c.title}</span>
                    <span
                      className={`text-[10px] tabular-nums ${
                        c.pct >= 80 ? 'text-emerald-500' : c.pct > 0 ? 'text-amber-500' : 'text-muted-foreground'
                      }`}
                    >
                      {c.pct}%
                    </span>
                  </span>
                  {c.act_title && (
                    <span className="mt-0.5 block text-[10px] uppercase tracking-wider text-muted-foreground">
                      {c.act_title}
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ol>
      </aside>

      <section className="min-w-0">
        <header className="mb-6">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground">Chapter brief</p>
              <h2 className="mt-1 font-serif text-2xl font-bold text-foreground">
                {chapter?.title || 'Chapter'}
              </h2>
              <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                The instruction package for writing one chapter. The bible says what is true; the
                brief says what this chapter must do with it.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => void prefill()}
                className="rounded-lg border border-border px-3 py-2 text-sm hover:bg-muted"
              >
                Pull from bible
              </button>
              <div className="text-right">
                <p className="font-serif text-3xl text-foreground">{brief?.completeness.pct ?? 0}%</p>
                <p className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  {brief?.completeness.filled ?? 0} of {brief?.completeness.total ?? 50}
                </p>
              </div>
            </div>
          </div>
          <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all"
              style={{ width: `${brief?.completeness.pct ?? 0}%` }}
            />
          </div>
        </header>

        <div className="mb-6 flex gap-1 overflow-x-auto border-b border-border pb-1">
          {schema.map((s) => {
            const c = brief?.completeness.sections[s.key];
            const isActive = s.key === section?.key;
            return (
              <button
                key={s.key}
                type="button"
                onClick={() => setActive(s.key)}
                className={`shrink-0 rounded-t-lg px-3 py-1.5 text-xs transition-colors ${
                  isActive
                    ? 'bg-primary/10 font-medium text-foreground'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }`}
              >
                {s.number > 0 && <span className="mr-1 opacity-60">{s.number}</span>}
                {s.title}
                <span className="ml-1.5 tabular-nums opacity-60">{c?.pct ?? 0}%</span>
              </button>
            );
          })}
        </div>

        {section && (
          <>
            <div className="flex flex-wrap items-start justify-between gap-3 border-b border-border pb-4">
              <div>
                <p className="text-xs uppercase tracking-wider text-muted-foreground">
                  {section.number > 0 ? `Section ${section.number} of 13` : 'Identity'}
                </p>
                <h3 className="mt-1 font-serif text-xl font-semibold text-foreground">{section.title}</h3>
                <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{section.intro}</p>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-xs uppercase tracking-wider text-muted-foreground" htmlFor="canon">
                  Status
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
                    {field.ai && (
                      <button
                        type="button"
                        onClick={() => void draftField(section.key, field.key)}
                        disabled={drafting === `${section.key}:${field.key}`}
                        className="rounded-full border border-border px-2.5 py-1 text-[11px] text-muted-foreground hover:bg-muted hover:text-foreground disabled:opacity-50"
                      >
                        {drafting === `${section.key}:${field.key}` ? 'Drafting…' : 'Draft with AI'}
                      </button>
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

                  {field.type === 'checks' && (
                    <ChecksEditor
                      items={field.items || []}
                      value={(values[field.key] as Record<string, string>) || {}}
                      onChange={(next) => setValue(section.key, field.key, next)}
                    />
                  )}
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap items-center gap-3 border-t border-border pt-4 text-xs text-muted-foreground">
              <SaveBadge state={saveState} />
              <span>Autosaves as you type.</span>
              <span className="ml-auto tabular-nums">
                {completion?.filled ?? 0}/{completion?.total ?? 0} in this section
              </span>
            </div>
          </>
        )}
      </section>
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
        <ul className="mt-2 space-y-1">
          {value.map((item, i) => (
            <li key={`${item}-${i}`} className="flex items-start gap-2 text-sm">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-muted-foreground" />
              <span className="flex-1">{item}</span>
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
              {row[columns[0]?.key] ? row[columns[0].key] : `Entry ${index + 1}`}
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
                <textarea
                  value={row[col.key] ?? ''}
                  onChange={(e) => update(index, col.key, e.target.value)}
                  rows={1}
                  className="w-full resize-y rounded-lg border border-border bg-background px-2 py-1.5 text-sm"
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

function ChecksEditor({
  items,
  value,
  onChange,
}: {
  items: string[];
  value: Record<string, string>;
  onChange: (next: Record<string, string>) => void;
}) {
  const options = [
    { value: 'yes', label: 'Yes' },
    { value: 'no', label: 'No' },
    { value: 'later', label: 'Not yet' },
  ];
  return (
    <ul className="divide-y divide-border rounded-xl border border-border">
      {items.map((item) => {
        const current = value[item] || 'unset';
        return (
          <li key={item} className="flex flex-wrap items-center justify-between gap-2 px-3 py-2">
            <span className="text-sm text-foreground">{item}</span>
            <div className="flex gap-1">
              {options.map((o) => (
                <button
                  key={o.value}
                  type="button"
                  onClick={() => onChange({ ...value, [item]: o.value })}
                  className={`rounded-full px-2.5 py-1 text-[11px] transition-colors ${
                    current === o.value
                      ? o.value === 'yes'
                        ? 'bg-emerald-500/15 text-emerald-600'
                        : o.value === 'no'
                          ? 'bg-destructive/10 text-destructive'
                          : 'bg-amber-500/15 text-amber-600'
                      : 'text-muted-foreground hover:bg-muted'
                  }`}
                >
                  {o.label}
                </button>
              ))}
            </div>
          </li>
        );
      })}
    </ul>
  );
}
