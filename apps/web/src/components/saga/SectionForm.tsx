'use client';

import { useMemo, useState } from 'react';
import type { FieldDef, SectionDef, SectionValues } from '@/lib/saga';

type Props = {
  schema: SectionDef[];
  values: SectionValues;
  onChange: (sectionKey: string, fieldKey: string, value: unknown) => void;
  statuses?: Record<string, string>;
  onStatus?: (sectionKey: string, status: string) => void;
  emptyNote?: string;
};

const STATUSES = [
  { value: 'working', label: 'Working' },
  { value: 'locked', label: 'Locked' },
  { value: 'undecided', label: 'Undecided' },
];

function isFilled(field: FieldDef, value: unknown): boolean {
  if (field.type === 'rows' || field.type === 'list') {
    return Array.isArray(value) && value.length > 0;
  }
  return Boolean(String(value ?? '').trim());
}

export function SectionForm({ schema, values, onChange, statuses, onStatus, emptyNote }: Props) {
  const [activeKey, setActiveKey] = useState(schema[0]?.key ?? '');
  const active = useMemo(
    () => schema.find((s) => s.key === activeKey) ?? schema[0],
    [schema, activeKey]
  );

  const progress = useMemo(() => {
    const out: Record<string, { filled: number; total: number; pct: number }> = {};
    for (const section of schema) {
      const body = values[section.key] || {};
      const filled = section.fields.filter((f) => isFilled(f, body[f.key])).length;
      out[section.key] = {
        filled,
        total: section.fields.length,
        pct: section.fields.length ? Math.round((100 * filled) / section.fields.length) : 0,
      };
    }
    return out;
  }, [schema, values]);

  const overall = useMemo(() => {
    const totals = Object.values(progress);
    const filled = totals.reduce((n, s) => n + s.filled, 0);
    const total = totals.reduce((n, s) => n + s.total, 0);
    return { filled, total, pct: total ? Math.round((100 * filled) / total) : 0 };
  }, [progress]);

  if (!schema.length) {
    return <p className="text-sm text-muted-foreground">{emptyNote || 'Nothing to fill in yet.'}</p>;
  }

  const body = values[active.key] || {};

  return (
    <div className="grid gap-6 lg:grid-cols-[240px,1fr]">
      <div className="space-y-3">
        <div className="rounded-lg border border-border/60 bg-card/60 p-3">
          <div className="flex items-baseline justify-between text-xs text-muted-foreground">
            <span>Overall</span>
            <span className="font-mono text-foreground">{overall.pct}%</span>
          </div>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-muted">
            <div className="h-full bg-primary" style={{ width: `${overall.pct}%` }} />
          </div>
          <p className="mt-1.5 text-[11px] text-muted-foreground">
            {overall.filled} of {overall.total} fields
          </p>
        </div>
        <nav className="max-h-[70vh] space-y-0.5 overflow-auto pr-1">
          {schema.map((section) => {
            const p = progress[section.key];
            const isActive = section.key === active?.key;
            return (
              <button
                key={section.key}
                onClick={() => setActiveKey(section.key)}
                className={`flex w-full items-start gap-2 rounded-md px-2.5 py-2 text-left text-sm transition ${
                  isActive ? 'bg-primary/10 text-foreground' : 'text-muted-foreground hover:bg-muted/60'
                }`}
              >
                <span className="mt-0.5 w-4 shrink-0 font-mono text-[11px] opacity-60">{section.number}</span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate">{section.title}</span>
                  <span className="mt-1 block h-0.5 w-full overflow-hidden rounded bg-muted">
                    <span
                      className={`block h-full ${p.pct === 100 ? 'bg-emerald-500' : 'bg-primary/70'}`}
                      style={{ width: `${p.pct}%` }}
                    />
                  </span>
                </span>
              </button>
            );
          })}
        </nav>
      </div>

      {active ? (
        <div className="min-w-0 space-y-5">
          <header className="flex flex-wrap items-start justify-between gap-3 border-b border-border/60 pb-3">
            <div>
              <h2 className="font-serif text-xl text-foreground">{active.title}</h2>
              <p className="mt-1 text-sm text-muted-foreground">{active.intro}</p>
            </div>
            {onStatus ? (
              <select
                value={statuses?.[active.key] || 'working'}
                onChange={(e) => onStatus(active.key, e.target.value)}
                className="rounded-md border border-border bg-background px-2 py-1 text-xs"
              >
                {STATUSES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </select>
            ) : null}
          </header>

          <div className="space-y-5">
            {active.fields.map((field) => {
              const value = body[field.key];
              return (
                <div key={field.key}>
                  <label className="block text-sm font-medium text-foreground">{field.label}</label>
                  <p className="mb-1.5 text-xs text-muted-foreground">{field.prompt}</p>
                  {field.type === 'short' ? (
                    <input
                      value={String(value ?? '')}
                      onChange={(e) => onChange(active.key, field.key, e.target.value)}
                      className="w-full rounded-md border border-border bg-background px-3 py-2 text-sm"
                    />
                  ) : field.type === 'text' ? (
                    <textarea
                      value={String(value ?? '')}
                      onChange={(e) => onChange(active.key, field.key, e.target.value)}
                      rows={4}
                      className="w-full resize-y rounded-md border border-border bg-background px-3 py-2 text-sm"
                    />
                  ) : field.type === 'list' ? (
                    <textarea
                      value={Array.isArray(value) ? (value as string[]).join('\n') : String(value ?? '')}
                      onChange={(e) =>
                        onChange(
                          active.key,
                          field.key,
                          e.target.value.split('\n').map((line) => line.trim()).filter(Boolean)
                        )
                      }
                      rows={4}
                      placeholder="One per line"
                      className="w-full resize-y rounded-md border border-border bg-background px-3 py-2 text-sm"
                    />
                  ) : field.type === 'rows' ? (
                    <RowsEditor
                      value={Array.isArray(value) ? (value as Record<string, string>[]) : []}
                      columns={field.columns || []}
                      onChange={(rows) => onChange(active.key, field.key, rows)}
                    />
                  ) : null}
                </div>
              );
            })}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function RowsEditor({
  value,
  columns,
  onChange,
}: {
  value: Record<string, string>[];
  columns: { key: string; label: string }[];
  onChange: (rows: Record<string, string>[]) => void;
}) {
  const update = (index: number, key: string, cell: string) => {
    const next = value.map((row, i) => (i === index ? { ...row, [key]: cell } : row));
    onChange(next);
  };
  return (
    <div className="space-y-2">
      <div className="overflow-x-auto rounded-md border border-border/60">
        <table className="w-full min-w-[640px] text-sm">
          <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
            <tr>
              {columns.map((c) => (
                <th key={c.key} className="px-2 py-1.5 font-medium">
                  {c.label}
                </th>
              ))}
              <th className="w-8" />
            </tr>
          </thead>
          <tbody>
            {value.length === 0 ? (
              <tr>
                <td colSpan={columns.length + 1} className="px-2 py-3 text-xs text-muted-foreground">
                  No rows yet.
                </td>
              </tr>
            ) : null}
            {value.map((row, index) => (
              <tr key={index} className="border-t border-border/40">
                {columns.map((c) => (
                  <td key={c.key} className="p-1">
                    <input
                      value={row[c.key] ?? ''}
                      onChange={(e) => update(index, c.key, e.target.value)}
                      className="w-full rounded border border-transparent bg-transparent px-1.5 py-1 text-sm focus:border-border focus:bg-background"
                    />
                  </td>
                ))}
                <td className="p-1 text-right">
                  <button
                    onClick={() => onChange(value.filter((_, i) => i !== index))}
                    className="px-1 text-xs text-muted-foreground hover:text-destructive"
                    aria-label="Remove row"
                  >
                    x
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        onClick={() => onChange([...value, Object.fromEntries(columns.map((c) => [c.key, '']))])}
        className="rounded-md border border-border px-3 py-1.5 text-xs hover:bg-muted"
      >
        Add row
      </button>
    </div>
  );
}
