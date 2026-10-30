'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
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

type TurningPoint = {
  id: string;
  book_id: string;
  act_id: string | null;
  sort_order: number;
  title: string;
  fields: Record<string, string | string[]>;
  filled: number;
  total: number;
  version: number;
};

type ActRow = { id: string; title: string; sort_order: number };

type CheckAnswer = { verdict: string; note: string; evidence: string };
type CheckQuestion = { key: string; label: string; look_for: string };
type CheckPayload = {
  run: { id: string; created_at: string | null; score: number; model: string } | null;
  questions: CheckQuestion[];
  answers: Record<string, CheckAnswer>;
  summary: { counts: Record<string, number>; answered: number; total: number; pct: number };
};

type ActSheet = {
  key: string;
  number: number;
  title: string;
  intro: string;
  fields: FieldDef[];
  values: Record<string, string>;
  filled: number;
  total: number;
  version: number;
};

type OutlineResponse = {
  book_id: string;
  book_title: string;
  turning_points: TurningPoint[];
  acts: ActRow[];
  progress: { filled: number; total: number; pct: number; points: number };
};

export default function OutlinePage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;

  const [fields, setFields] = useState<FieldDef[]>([]);
  const [points, setPoints] = useState<TurningPoint[]>([]);
  const [acts, setActs] = useState<ActRow[]>([]);
  const [sheets, setSheets] = useState<ActSheet[]>([]);
  const [actDraft, setActDraft] = useState<Record<string, Record<string, string>>>({});
  const [actBusy, setActBusy] = useState<string | null>(null);
  const [check, setCheck] = useState<CheckPayload | null>(null);
  const [checkBusy, setCheckBusy] = useState(false);
  const [bookTitle, setBookTitle] = useState('');
  const [draft, setDraft] = useState<Record<string, Record<string, string>>>({});
  const [titles, setTitles] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const hydrate = useCallback((res: OutlineResponse, schema: FieldDef[]) => {
    setPoints(res.turning_points);
    setActs(res.acts);
    setBookTitle(res.book_title);
    const flat: Record<string, Record<string, string>> = {};
    const nameMap: Record<string, string> = {};
    for (const point of res.turning_points) {
      flat[point.id] = {};
      nameMap[point.id] = point.title;
      for (const field of schema) {
        const value = point.fields?.[field.key];
        flat[point.id][field.key] = Array.isArray(value) ? value.join('\n') : (value ?? '');
      }
    }
    setDraft(flat);
    setTitles(nameMap);
  }, []);

  const load = useCallback(async () => {
    if (!projectId || !bookId) return;
    setLoading(true);
    try {
      const [schemaRes, outlineRes] = await Promise.all([
        api<{ fields: FieldDef[] }>('/api/v1/projects/book-outline/schema'),
        api<OutlineResponse>(`/api/v1/projects/${projectId}/books/${bookId}/outline`),
      ]);
      setFields(schemaRes.fields);
      hydrate(outlineRes, schemaRes.fields);
      const actsRes = await api<{ sections: ActSheet[] }>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/acts`
      );
      setSheets(actsRes.sections);
      const flatActs: Record<string, Record<string, string>> = {};
      for (const sheet of actsRes.sections) {
        flatActs[sheet.key] = {};
        for (const field of sheet.fields) {
          flatActs[sheet.key][field.key] = String(sheet.values?.[field.key] ?? '');
        }
      }
      setActDraft(flatActs);
      const checkRes = await api<CheckPayload>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/check`
      );
      setCheck(checkRes);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the outline.');
    } finally {
      setLoading(false);
    }
  }, [bookId, hydrate, projectId]);

  useEffect(() => {
    void load();
  }, [load]);

  const completeness = useMemo(() => {
    let filled = 0;
    let total = 0;
    for (const point of points) {
      for (const field of fields) {
        total += 1;
        if ((draft[point.id]?.[field.key] ?? '').trim()) filled += 1;
      }
    }
    return { filled, total, pct: total ? Math.round((filled / total) * 100) : 0 };
  }, [draft, fields, points]);

  async function runCheck() {
    if (!projectId || !bookId) return;
    setCheckBusy(true);
    try {
      const res = await api<CheckPayload>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/check/run`,
        { method: 'POST' }
      );
      setCheck(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The check could not run.');
    } finally {
      setCheckBusy(false);
    }
  }

  async function saveActField(actKey: string, fieldKey: string) {
    if (!projectId || !bookId) return;
    const value = actDraft[actKey]?.[fieldKey] ?? '';
    try {
      const updated = await api<ActSheet>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/acts/${actKey}`,
        { method: 'PATCH', body: JSON.stringify({ values: { [fieldKey]: value } }) }
      );
      setSheets((current) => current.map((s) => (s.key === actKey ? updated : s)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save that section.');
    }
  }

  async function draftActField(sheet: ActSheet, field: FieldDef) {
    if (!projectId || !bookId) return;
    const busyKey = `${sheet.key}:${field.key}`;
    setActBusy(busyKey);
    try {
      const res = await api<{ text: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/acts/${sheet.key}/draft-field`,
        { method: 'POST', body: JSON.stringify({ field: field.key }) }
      );
      setActDraft((current) => ({
        ...current,
        [sheet.key]: { ...current[sheet.key], [field.key]: res.text },
      }));
      await api<ActSheet>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/acts/${sheet.key}`,
        { method: 'PATCH', body: JSON.stringify({ values: { [field.key]: res.text } }) }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The draft did not come back.');
    } finally {
      setActBusy(null);
    }
  }

  async function reloadActs() {
    if (!projectId || !bookId) return;
    const actsRes = await api<{ sections: ActSheet[] }>(
      `/api/v1/projects/${projectId}/books/${bookId}/outline/acts`
    );
    setSheets(actsRes.sections);
    setActDraft((current) => {
      const next = { ...current };
      for (const sheet of actsRes.sections) {
        if (!next[sheet.key]) {
          next[sheet.key] = Object.fromEntries(
            sheet.fields.map((field) => [field.key, String(sheet.values?.[field.key] ?? '')])
          );
        }
      }
      return next;
    });
  }

  async function addAct() {
    if (!projectId || !bookId) return;
    setActBusy('add');
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/outline/acts`, {
        method: 'POST',
        body: JSON.stringify({}),
      });
      await reloadActs();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add an act.');
    } finally {
      setActBusy(null);
    }
  }

  async function removeAct(actKey: string) {
    if (!projectId || !bookId) return;
    if (!window.confirm('Remove this act and everything written in it?')) return;
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/outline/acts/${actKey}`, {
        method: 'DELETE',
      });
      await reloadActs();
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not remove that act.');
    }
  }

  async function renameAct(actKey: string, title: string) {
    if (!projectId || !bookId || !title.trim()) return;
    try {
      const updated = await api<ActSheet>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/acts/${actKey}`,
        { method: 'PATCH', body: JSON.stringify({ title }) }
      );
      setSheets((current) => current.map((s) => (s.key === actKey ? updated : s)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not rename that act.');
    }
  }

  async function patchPoint(id: string, body: Record<string, unknown>) {
    if (!projectId || !bookId) return;
    try {
      const updated = await api<TurningPoint>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/${id}`,
        { method: 'PATCH', body: JSON.stringify(body) }
      );
      setPoints((current) => current.map((p) => (p.id === id ? { ...p, ...updated } : p)));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save that turning point.');
    }
  }

  async function saveField(pointId: string, fieldKey: string) {
    const value = draft[pointId]?.[fieldKey] ?? '';
    const field = fields.find((f) => f.key === fieldKey);
    const payload =
      field?.type === 'list'
        ? value
            .split('\n')
            .map((line) => line.replace(/^[-*]\s*/, '').trim())
            .filter(Boolean)
        : value;
    await patchPoint(pointId, { fields: { [fieldKey]: payload } });
  }

  async function addPoint() {
    if (!projectId || !bookId) return;
    try {
      const created = await api<TurningPoint>(`/api/v1/projects/${projectId}/books/${bookId}/outline`, {
        method: 'POST',
        body: JSON.stringify({ title: `Turning point ${points.length + 1}` }),
      });
      const res = await api<OutlineResponse>(`/api/v1/projects/${projectId}/books/${bookId}/outline`);
      hydrate(res, fields);
      setExpanded((current) => ({ ...current, [created.id]: true }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add a turning point.');
    }
  }

  async function removePoint(id: string) {
    if (!projectId || !bookId) return;
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/outline/${id}`, { method: 'DELETE' });
      const res = await api<OutlineResponse>(`/api/v1/projects/${projectId}/books/${bookId}/outline`);
      hydrate(res, fields);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not remove that turning point.');
    }
  }

  async function move(id: string, direction: 'up' | 'down') {
    if (!projectId || !bookId) return;
    try {
      await api(`/api/v1/projects/${projectId}/books/${bookId}/outline/${id}/move`, {
        method: 'POST',
        body: JSON.stringify({ direction }),
      });
      const res = await api<OutlineResponse>(`/api/v1/projects/${projectId}/books/${bookId}/outline`);
      hydrate(res, fields);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not move that turning point.');
    }
  }

  async function draftField(pointId: string, field: FieldDef) {
    if (!projectId || !bookId) return;
    setBusy(`${pointId}.${field.key}`);
    try {
      const res = await api<{ text: string }>(
        `/api/v1/projects/${projectId}/books/${bookId}/outline/${pointId}/draft-field`,
        { method: 'POST', body: JSON.stringify({ field: field.key }) }
      );
      setDraft((current) => ({
        ...current,
        [pointId]: { ...current[pointId], [field.key]: res.text },
      }));
      const payload =
        field.type === 'list'
          ? res.text
              .split('\n')
              .map((line) => line.replace(/^[-*]\s*/, '').trim())
              .filter(Boolean)
          : res.text;
      await patchPoint(pointId, { fields: { [field.key]: payload } });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The draft did not come back.');
    } finally {
      setBusy(null);
    }
  }

  if (loading) {
    return <p className="py-10 text-sm text-muted-foreground">Loading the outline…</p>;
  }

  return (
    <div className="mx-auto max-w-4xl">
      <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Layer three</p>
          <h1 className="mt-1 text-2xl font-semibold">Overall Outline</h1>
          <p className="mt-1 max-w-xl text-sm text-muted-foreground">
            {bookTitle ? `${bookTitle} — ` : ''}the spine, one turning point at a time. Every section
            answers the same eleven questions, so you can judge it before you write it.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="w-24 overflow-hidden rounded-full bg-muted">
            <div className="h-1.5 bg-foreground transition-all" style={{ width: `${completeness.pct}%` }} />
          </div>
          <span className="text-xs tabular-nums text-muted-foreground">
            {completeness.pct}% · {points.length} turning points
          </span>
        </div>
      </div>

      {error && (
        <div className="mb-4 rounded-lg border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      {sheets.length > 0 && (
        <div className="mb-8 space-y-4">
          <div className="flex items-baseline justify-between">
            <div>
              <h2 className="text-sm font-medium">What each act must establish</h2>
              <p className="mt-1 text-xs text-muted-foreground">
                Plot is the floor, not the ceiling. These answer for character, relationships, world,
                mysteries, subplots and cause. Add as many acts as the book needs.
              </p>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs tabular-nums text-muted-foreground">
                {sheets.reduce((n, s) => n + s.filled, 0)}/{sheets.reduce((n, s) => n + s.total, 0)}
              </span>
              <button
                type="button"
                onClick={() => void addAct()}
                disabled={actBusy === 'add'}
                className="rounded-lg border border-border px-3 py-1.5 text-xs hover:border-foreground/40 disabled:opacity-40"
              >
                {actBusy === 'add' ? 'Adding…' : '+ Add act'}
              </button>
            </div>
          </div>
          {sheets.map((sheet) => (
            <div key={sheet.key} className="rounded-xl border border-border p-4">
              <div className="mb-3 flex flex-wrap items-baseline justify-between gap-2">
                <div className="flex-1">
                  {['setup', 'confrontation', 'resolution'].includes(sheet.key) ? (
                    <h3 className="text-sm font-semibold">
                      {sheet.number}. {sheet.title}
                    </h3>
                  ) : (
                    <input
                      defaultValue={sheet.title}
                      onBlur={(e) => {
                        if (e.target.value.trim() && e.target.value !== sheet.title) {
                          void renameAct(sheet.key, e.target.value.trim());
                        }
                      }}
                      className="w-full max-w-sm rounded border border-transparent bg-transparent text-sm font-semibold outline-none hover:border-border focus:border-foreground/40"
                      aria-label="Act title"
                    />
                  )}
                  <p className="text-xs text-muted-foreground">{sheet.intro}</p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-[11px] tabular-nums text-muted-foreground">
                    {sheet.filled}/{sheet.total}
                  </span>
                  {!['setup', 'confrontation', 'resolution'].includes(sheet.key) && (
                    <button
                      type="button"
                      onClick={() => void removeAct(sheet.key)}
                      className="text-[11px] uppercase tracking-wider text-muted-foreground hover:text-destructive"
                    >
                      Remove
                    </button>
                  )}
                </div>
              </div>
              <div className="space-y-3">
                {sheet.fields.map((field) => (
                  <div key={field.key}>
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <label className="text-[11px] uppercase tracking-wider text-muted-foreground">
                        {field.label}
                      </label>
                      {field.ai !== false && (
                        <button
                          type="button"
                          onClick={() => void draftActField(sheet, field)}
                          disabled={actBusy === `${sheet.key}:${field.key}`}
                          className="text-[11px] uppercase tracking-wider text-muted-foreground hover:text-foreground disabled:opacity-40"
                        >
                          {actBusy === `${sheet.key}:${field.key}` ? 'Drafting…' : 'Draft with AI'}
                        </button>
                      )}
                    </div>
                    {field.type === 'short' ? (
                      <input
                        value={actDraft[sheet.key]?.[field.key] ?? ''}
                        onChange={(e) =>
                          setActDraft((current) => ({
                            ...current,
                            [sheet.key]: { ...current[sheet.key], [field.key]: e.target.value },
                          }))
                        }
                        onBlur={() => void saveActField(sheet.key, field.key)}
                        placeholder={field.prompt}
                        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-foreground/40"
                      />
                    ) : (
                      <textarea
                        value={actDraft[sheet.key]?.[field.key] ?? ''}
                        onChange={(e) =>
                          setActDraft((current) => ({
                            ...current,
                            [sheet.key]: { ...current[sheet.key], [field.key]: e.target.value },
                          }))
                        }
                        onBlur={() => void saveActField(sheet.key, field.key)}
                        placeholder={field.prompt}
                        rows={3}
                        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus:border-foreground/40"
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {check && (
        <div className="mb-8 rounded-xl border border-border p-4">
          <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-sm font-medium">The twelve-question check</h2>
              <p className="mt-1 text-xs text-muted-foreground">
                {check.run
                  ? `Last run ${new Date(check.run.created_at ?? '').toLocaleString()} — ${check.summary.counts.pass ?? 0} pass · ${check.summary.counts.partial ?? 0} partial · ${check.summary.counts.fail ?? 0} fail · ${check.summary.counts.unknown ?? 0} unknown`
                  : 'Cause, agency, stakes, relationships, world, consequence, mystery and delivery of the promise.'}
              </p>
            </div>
            <button
              type="button"
              onClick={() => void runCheck()}
              disabled={checkBusy || points.length === 0}
              title={points.length === 0 ? 'Add turning points first' : undefined}
              className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium hover:bg-muted disabled:opacity-40"
            >
              {checkBusy ? 'Checking…' : check.run ? 'Run again' : 'Run the check'}
            </button>
          </div>
          {check.run && (
            <div className="divide-y divide-border">
              {check.questions.map((question, index) => {
                const answer = check.answers[question.key];
                const verdict = answer?.verdict ?? 'unknown';
                const tone =
                  verdict === 'pass'
                    ? 'text-emerald-500'
                    : verdict === 'partial'
                      ? 'text-amber-500'
                      : verdict === 'fail'
                        ? 'text-red-500'
                        : 'text-muted-foreground';
                return (
                  <div key={question.key} className="py-3">
                    <div className="flex items-baseline justify-between gap-3">
                      <p className="text-sm">
                        <span className="mr-2 tabular-nums text-muted-foreground">{index + 1}.</span>
                        {question.label}
                      </p>
                      <span className={`shrink-0 text-[11px] uppercase tracking-wider ${tone}`}>
                        {verdict}
                      </span>
                    </div>
                    {answer?.note && (
                      <p className="mt-1 text-xs text-muted-foreground">{answer.note}</p>
                    )}
                    {answer?.evidence && (
                      <p className="mt-1 text-[11px] italic text-muted-foreground/80">
                        {answer.evidence}
                      </p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {points.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-8 text-center">
          <p className="text-sm text-muted-foreground">
            No turning points yet. Start with the one you can see clearest — usually the
            disruption that opens the story.
          </p>
          <button
            type="button"
            onClick={() => void addPoint()}
            className="mt-4 rounded-lg bg-foreground px-4 py-2 text-sm text-background"
          >
            Add the first turning point
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {points.map((point, index) => {
            const open = expanded[point.id] ?? index === 0;
            const filled = fields.filter((f) => (draft[point.id]?.[f.key] ?? '').trim()).length;
            return (
              <section key={point.id} className="rounded-xl border border-border">
                <div className="flex flex-wrap items-center gap-2 border-b border-border px-4 py-3">
                  <span className="w-6 text-xs tabular-nums text-muted-foreground">{index + 1}.</span>
                  <input
                    value={titles[point.id] ?? ''}
                    onChange={(e) => setTitles((c) => ({ ...c, [point.id]: e.target.value }))}
                    onBlur={() => void patchPoint(point.id, { title: titles[point.id] ?? '' })}
                    placeholder="Name this turning point"
                    className="min-w-0 flex-1 border-0 bg-transparent text-sm font-medium outline-none placeholder:text-muted-foreground"
                  />
                  <select
                    value={point.act_id ?? ''}
                    onChange={(e) =>
                      void patchPoint(
                        point.id,
                        e.target.value ? { act_id: e.target.value } : { clear_act: true }
                      )
                    }
                    className="rounded-md border border-border bg-background px-2 py-1 text-xs"
                  >
                    <option value="">No act</option>
                    {acts.map((act) => (
                      <option key={act.id} value={act.id}>
                        {act.title}
                      </option>
                    ))}
                  </select>
                  <span className="text-[11px] tabular-nums text-muted-foreground">
                    {filled}/{fields.length}
                  </span>
                  <div className="flex items-center gap-1">
                    <button
                      type="button"
                      onClick={() => void move(point.id, 'up')}
                      disabled={index === 0}
                      className="rounded-md border border-border px-2 py-0.5 text-xs disabled:opacity-30"
                      aria-label="Move up"
                    >
                      ↑
                    </button>
                    <button
                      type="button"
                      onClick={() => void move(point.id, 'down')}
                      disabled={index === points.length - 1}
                      className="rounded-md border border-border px-2 py-0.5 text-xs disabled:opacity-30"
                      aria-label="Move down"
                    >
                      ↓
                    </button>
                    <button
                      type="button"
                      onClick={() => setExpanded((c) => ({ ...c, [point.id]: !open }))}
                      className="rounded-md border border-border px-2 py-0.5 text-xs"
                    >
                      {open ? 'Collapse' : 'Open'}
                    </button>
                    <button
                      type="button"
                      onClick={() => void removePoint(point.id)}
                      className="rounded-md border border-border px-2 py-0.5 text-xs text-muted-foreground hover:text-destructive"
                    >
                      Remove
                    </button>
                  </div>
                </div>

                {open && (
                  <div className="grid gap-4 px-4 py-4 md:grid-cols-2">
                    {fields.map((field) => {
                      const value = draft[point.id]?.[field.key] ?? '';
                      const isBusy = busy === `${point.id}.${field.key}`;
                      const wide = field.type === 'text';
                      return (
                        <div key={field.key} className={wide ? 'md:col-span-2' : ''}>
                          <div className="mb-1 flex items-center justify-between gap-2">
                            <label className="text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
                              {field.label}
                            </label>
                            {field.ai && (
                              <button
                                type="button"
                                onClick={() => void draftField(point.id, field)}
                                disabled={isBusy}
                                className="rounded-md border border-border px-2 py-0.5 text-[10px] uppercase tracking-wider text-muted-foreground hover:text-foreground disabled:opacity-50"
                              >
                                {isBusy ? '…' : 'Draft'}
                              </button>
                            )}
                          </div>
                          <textarea
                            value={value}
                            rows={field.type === 'list' ? 3 : 2}
                            placeholder={field.prompt}
                            onChange={(e) =>
                              setDraft((current) => ({
                                ...current,
                                [point.id]: { ...current[point.id], [field.key]: e.target.value },
                              }))
                            }
                            onBlur={() => void saveField(point.id, field.key)}
                            className="w-full resize-y rounded-lg border border-border bg-background px-2.5 py-1.5 text-sm leading-relaxed outline-none focus:border-foreground/40"
                          />
                        </div>
                      );
                    })}
                  </div>
                )}
              </section>
            );
          })}

          <button
            type="button"
            onClick={() => void addPoint()}
            className="w-full rounded-xl border border-dashed border-border py-3 text-sm text-muted-foreground hover:border-foreground/30 hover:text-foreground"
          >
            Add another turning point
          </button>
        </div>
      )}

      <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-border pt-4 text-xs">
        <p className="text-muted-foreground">Saves when you leave a field.</p>
        <Link
          href={`/dashboard/projects/${projectId}/books/${bookId}/brief`}
          className="rounded-lg border border-border px-3 py-1.5 hover:bg-muted"
        >
          Next: chapter briefs →
        </Link>
      </div>
    </div>
  );
}
