'use client';

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { SectionForm } from '@/components/saga/SectionForm';
import {
  createSeries,
  createThread,
  createTruth,
  deleteSeries,
  deleteThread,
  deleteTruth,
  getSaga,
  getSagaSchema,
  linkProject,
  listProjectsLite,
  listSeries,
  listThreads,
  listTruths,
  unlinkProject,
  updateSaga,
  updateSagaOutline,
  updateSeries,
  updateThread,
  updateTruth,
  type Saga,
  type SagaProject,
  type SagaSchema,
  type SectionValues,
  type SeriesPlan,
  type Thread,
  type Truth,
} from '@/lib/saga';

type Tab = 'bible' | 'outline' | 'series' | 'threads' | 'truths' | 'books';

const TABS: { key: Tab; label: string }[] = [
  { key: 'bible', label: 'Saga bible' },
  { key: 'outline', label: 'Saga outline' },
  { key: 'series', label: 'Series' },
  { key: 'threads', label: 'Threads' },
  { key: 'truths', label: 'Truths' },
  { key: 'books', label: 'Books' },
];

export default function SagaWorkspacePage() {
  const params = useParams<{ id: string }>();
  const sagaId = params?.id as string;

  const [schema, setSchema] = useState<SagaSchema | null>(null);
  const [saga, setSaga] = useState<Saga | null>(null);
  const [sections, setSections] = useState<SectionValues>({});
  const [statuses, setStatuses] = useState<Record<string, string>>({});
  const [outline, setOutline] = useState<SectionValues>({});
  const [series, setSeries] = useState<SeriesPlan[]>([]);
  const [activePlanId, setActivePlanId] = useState<string | null>(null);
  const [threads, setThreads] = useState<Thread[]>([]);
  const [truths, setTruths] = useState<Truth[]>([]);
  const [projects, setProjects] = useState<SagaProject[]>([]);
  const [allProjects, setAllProjects] = useState<{ id: string; name: string }[]>([]);
  const [tab, setTab] = useState<Tab>('bible');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');

  const saveTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  const load = useCallback(async () => {
    try {
      const [s, detail, plans, threadList, truthList] = await Promise.all([
        getSagaSchema(),
        getSaga(sagaId),
        listSeries(sagaId),
        listThreads(sagaId),
        listTruths(sagaId),
      ]);
      setSchema(s);
      setSaga(detail.saga);
      setSections(detail.sections || {});
      setStatuses(detail.section_status || {});
      setOutline(detail.outline.sections || {});
      setProjects(detail.projects || []);
      setSeries(plans.series);
      if (plans.series.length > 0) setActivePlanId((current) => current ?? plans.series[0].id);
      setThreads(threadList.threads);
      setTruths(truthList.truths);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the saga.');
    } finally {
      setLoading(false);
    }
  }, [sagaId]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const timers = saveTimers.current;
    return () => {
      Object.values(timers).forEach(clearTimeout);
    };
  }, []);

  const activePlan = useMemo(
    () => series.find((plan) => plan.id === activePlanId) ?? null,
    [series, activePlanId]
  );

  function scheduleSave(key: string, action: () => Promise<unknown>) {
    if (saveTimers.current[key]) clearTimeout(saveTimers.current[key]);
    setSaveState('saving');
    saveTimers.current[key] = setTimeout(async () => {
      try {
        await action();
        setSaveState('saved');
      } catch (err) {
        setSaveState('error');
        setError(err instanceof Error ? err.message : 'Could not save.');
      }
    }, 700);
  }

  function changeSection(sectionKey: string, fieldKey: string, value: unknown) {
    const next = {
      ...sections,
      [sectionKey]: { ...(sections[sectionKey] || {}), [fieldKey]: value },
    };
    setSections(next);
    scheduleSave('saga', async () => {
      const res = await updateSaga(sagaId, { sections: { [sectionKey]: next[sectionKey] } });
      if (res?.saga) setSaga(res.saga);
    });
  }

  function changeOutline(sectionKey: string, fieldKey: string, value: unknown) {
    const next = {
      ...outline,
      [sectionKey]: { ...(outline[sectionKey] || {}), [fieldKey]: value },
    };
    setOutline(next);
    scheduleSave('outline', () => updateSagaOutline(sagaId, { [sectionKey]: next[sectionKey] }));
  }

  function changePlanSection(sectionKey: string, fieldKey: string, value: unknown) {
    if (!activePlan) return;
    const nextSections = {
      ...(activePlan.sections || {}),
      [sectionKey]: { ...((activePlan.sections || {})[sectionKey] || {}), [fieldKey]: value },
    };
    setSeries((current) =>
      current.map((plan) => (plan.id === activePlan.id ? { ...plan, sections: nextSections } : plan))
    );
    scheduleSave(`plan-${activePlan.id}`, () =>
      updateSeries(sagaId, activePlan.id, { sections: { [sectionKey]: nextSections[sectionKey] } })
    );
  }

  async function addSeries() {
    const name = window.prompt('Name this series or phase');
    if (!name?.trim()) return;
    try {
      const created = await createSeries(sagaId, name.trim());
      const plans = await listSeries(sagaId);
      setSeries(plans.series);
      setActivePlanId(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the series.');
    }
  }

  async function removeSeries(plan: SeriesPlan) {
    if (!window.confirm(`Delete "${plan.name}"? Its questionnaire is lost; books stay where they are.`)) return;
    try {
      await deleteSeries(sagaId, plan.id);
      const plans = await listSeries(sagaId);
      setSeries(plans.series);
      setActivePlanId(plans.series[0]?.id ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete the series.');
    }
  }

  async function refreshThreads() {
    const data = await listThreads(sagaId);
    setThreads(data.threads);
  }

  async function refreshTruths() {
    const data = await listTruths(sagaId);
    setTruths(data.truths);
  }

  async function addThread(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    const name = String(data.get('name') || '').trim();
    if (!name) return;
    try {
      await createThread(sagaId, {
        name,
        detail: String(data.get('detail') || '') || null,
        opened_in: String(data.get('opened_in') || '') || null,
      });
      form.reset();
      await refreshThreads();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add the thread.');
    }
  }

  async function addTruth(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    const statement = String(data.get('statement') || '').trim();
    if (!statement) return;
    try {
      await createTruth(sagaId, {
        statement,
        reveal_point: String(data.get('reveal_point') || '') || null,
        knows: String(data.get('knows') || '')
          .split(',')
          .map((s) => s.trim())
          .filter(Boolean),
      });
      form.reset();
      await refreshTruths();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add the truth.');
    }
  }

  async function attachProject(projectId: string) {
    if (!projectId) return;
    try {
      await linkProject(sagaId, projectId);
      const detail = await getSaga(sagaId);
      setProjects(detail.projects);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not attach the project.');
    }
  }

  async function detachProject(projectId: string) {
    try {
      await unlinkProject(sagaId, projectId);
      setProjects((current) => current.filter((p) => p.id !== projectId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not detach the project.');
    }
  }

  useEffect(() => {
    if (tab !== 'books' || allProjects.length > 0) return;
    listProjectsLite()
      .then(setAllProjects)
      .catch(() => undefined);
  }, [tab, allProjects.length]);

  if (loading) return <div className="p-8 text-sm text-muted-foreground">Loading the saga…</div>;
  if (!saga || !schema) return <div className="p-8 text-sm text-destructive">{error || 'Saga not found.'}</div>;

  const linkedIds = new Set(projects.map((p) => p.id));
  const available = allProjects.filter((p) => !linkedIds.has(p.id));

  return (
    <div className="mx-auto max-w-6xl px-5 py-8">
      <header className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/dashboard/sagas" className="text-xs text-muted-foreground hover:text-foreground">
            ← All sagas
          </Link>
          <h1 className="mt-1 font-serif text-3xl text-foreground">{saga.name}</h1>
          <p className="mt-1 text-xs text-muted-foreground">
            {projects.length} {projects.length === 1 ? 'series attached' : 'series attached'} ·{' '}
            {saga.completeness.pct}% bible
          </p>
        </div>
        <span
          className={`rounded-full px-2.5 py-1 text-[11px] ${
            saveState === 'error'
              ? 'bg-destructive/10 text-destructive'
              : saveState === 'saving'
                ? 'bg-muted text-muted-foreground'
                : 'bg-emerald-500/10 text-emerald-600'
          }`}
        >
          {saveState === 'saving' ? 'Saving…' : saveState === 'error' ? 'Save failed' : 'Saved'}
        </span>
      </header>

      <nav className="mb-6 flex flex-wrap gap-1 border-b border-border/60">
        {TABS.map((item) => (
          <button
            key={item.key}
            onClick={() => setTab(item.key)}
            className={`-mb-px border-b-2 px-3 py-2 text-sm transition ${
              tab === item.key
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {error ? <p className="mb-4 text-sm text-destructive">{error}</p> : null}

      {tab === 'bible' ? (
        <SectionForm
          schema={schema.sections}
          values={sections}
          statuses={statuses}
          onChange={changeSection}
          onStatus={(key, status) => {
            const next = { ...statuses, [key]: status };
            setStatuses(next);
            scheduleSave('status', async () => {
              const res = await updateSaga(sagaId, { section_status: { [key]: status } });
              if (res?.saga) setSaga(res.saga);
            });
          }}
        />
      ) : null}

      {tab === 'outline' ? (
        <SectionForm
          schema={schema.outline_sections}
          values={outline}
          onChange={changeOutline}
          emptyNote="The outline appears once the saga exists."
        />
      ) : null}

      {tab === 'series' ? (
        <div className="grid gap-6 lg:grid-cols-[240px,1fr]">
          <div className="space-y-2">
            {series.map((plan) => (
              <button
                key={plan.id}
                onClick={() => setActivePlanId(plan.id)}
                className={`flex w-full items-center justify-between gap-2 rounded-md px-2.5 py-2 text-left text-sm ${
                  plan.id === activePlanId
                    ? 'bg-primary/10 text-foreground'
                    : 'text-muted-foreground hover:bg-muted/60'
                }`}
              >
                <span className="min-w-0 truncate">
                  <span className="mr-1 font-mono text-[11px] opacity-60">{plan.position}</span>
                  {plan.name}
                </span>
                <span className="font-mono text-[11px]">{plan.completeness.pct}%</span>
              </button>
            ))}
            <button
              onClick={addSeries}
              className="w-full rounded-md border border-dashed border-border px-3 py-2 text-xs text-muted-foreground hover:text-foreground"
            >
              + Add series or phase
            </button>
          </div>
          <div className="min-w-0">
            {activePlan ? (
              <>
                <div className="mb-4 flex items-center justify-between gap-3">
                  <h2 className="font-serif text-xl text-foreground">{activePlan.name}</h2>
                  <button
                    onClick={() => removeSeries(activePlan)}
                    className="text-xs text-muted-foreground hover:text-destructive"
                  >
                    Delete series
                  </button>
                </div>
                <SectionForm
                  schema={schema.series_sections}
                  values={activePlan.sections || {}}
                  onChange={changePlanSection}
                />
              </>
            ) : (
              <div className="rounded-lg border border-dashed border-border/70 p-8 text-center text-sm text-muted-foreground">
                No series yet. A saga is made of one or more series or major phases.
              </div>
            )}
          </div>
        </div>
      ) : null}

      {tab === 'threads' ? (
        <div className="space-y-4">
          <form onSubmit={addThread} className="grid gap-2 rounded-lg border border-border/60 bg-card/60 p-4 sm:grid-cols-[2fr,2fr,1fr,auto]">
            <input name="name" placeholder="Promise or thread" className="rounded-md border border-border bg-background px-3 py-2 text-sm" />
            <input name="detail" placeholder="What was promised" className="rounded-md border border-border bg-background px-3 py-2 text-sm" />
            <input name="opened_in" placeholder="Opened in" className="rounded-md border border-border bg-background px-3 py-2 text-sm" />
            <button type="submit" className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
              Add thread
            </button>
          </form>

          <div className="overflow-x-auto rounded-lg border border-border/60">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-3 py-2">Promise</th>
                  <th className="px-3 py-2">Opened</th>
                  <th className="px-3 py-2">Paid in</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2" />
                </tr>
              </thead>
              <tbody>
                {threads.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-3 py-6 text-center text-muted-foreground">
                      No threads tracked. Every promise the saga makes belongs here.
                    </td>
                  </tr>
                ) : null}
                {threads.map((thread) => (
                  <tr key={thread.id} className="border-t border-border/40">
                    <td className="px-3 py-2">
                      <input
                        defaultValue={thread.name}
                        onBlur={(e) => {
                          if (e.target.value !== thread.name) {
                            void updateThread(sagaId, thread.id, { name: e.target.value }).then(refreshThreads);
                          }
                        }}
                        className="w-full bg-transparent"
                      />
                      {thread.detail ? <p className="text-xs text-muted-foreground">{thread.detail}</p> : null}
                    </td>
                    <td className="px-3 py-2">
                      <input
                        defaultValue={thread.opened_in ?? ''}
                        onBlur={(e) => {
                          if (e.target.value !== (thread.opened_in ?? '')) {
                            void updateThread(sagaId, thread.id, { opened_in: e.target.value }).then(refreshThreads);
                          }
                        }}
                        className="w-full bg-transparent"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        defaultValue={thread.paid_in ?? ''}
                        onBlur={(e) => {
                          if (e.target.value !== (thread.paid_in ?? '')) {
                            void updateThread(sagaId, thread.id, { paid_in: e.target.value }).then(refreshThreads);
                          }
                        }}
                        className="w-full bg-transparent"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <select
                        value={thread.status}
                        onChange={(e) =>
                          void updateThread(sagaId, thread.id, { status: e.target.value }).then(refreshThreads)
                        }
                        className="rounded border border-border bg-background px-2 py-1 text-xs"
                      >
                        {schema.thread_statuses.map((status) => (
                          <option key={status} value={status}>
                            {status}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-3 py-2 text-right">
                      <button
                        onClick={() => void deleteThread(sagaId, thread.id).then(refreshThreads)}
                        className="text-xs text-muted-foreground hover:text-destructive"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {tab === 'truths' ? (
        <div className="space-y-4">
          <form onSubmit={addTruth} className="grid gap-2 rounded-lg border border-border/60 bg-card/60 p-4 sm:grid-cols-[3fr,1fr,1fr,auto]">
            <input name="statement" placeholder="What is actually true" className="rounded-md border border-border bg-background px-3 py-2 text-sm" />
            <input name="reveal_point" placeholder="Revealed in" className="rounded-md border border-border bg-background px-3 py-2 text-sm" />
            <input name="knows" placeholder="Who knows (comma separated)" className="rounded-md border border-border bg-background px-3 py-2 text-sm" />
            <button type="submit" className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground">
              Add truth
            </button>
          </form>

          <div className="overflow-x-auto rounded-lg border border-border/60">
            <table className="w-full min-w-[720px] text-sm">
              <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-3 py-2">Truth</th>
                  <th className="px-3 py-2">Reveal</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2" />
                </tr>
              </thead>
              <tbody>
                {truths.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-6 text-center text-muted-foreground">
                      No truths tracked yet. If a reveal is not written down, a later book will contradict it.
                    </td>
                  </tr>
                ) : null}
                {truths.map((truth) => (
                  <tr key={truth.id} className="border-t border-border/40">
                    <td className="px-3 py-2">
                      <input
                        defaultValue={truth.statement}
                        onBlur={(e) => {
                          if (e.target.value !== truth.statement) {
                            void updateTruth(sagaId, truth.id, { statement: e.target.value }).then(refreshTruths);
                          }
                        }}
                        className="w-full bg-transparent"
                      />
                      {truth.knows.length ? (
                        <p className="text-xs text-muted-foreground">Knows: {truth.knows.join(', ')}</p>
                      ) : null}
                    </td>
                    <td className="px-3 py-2">
                      <input
                        defaultValue={truth.reveal_point ?? ''}
                        onBlur={(e) => {
                          if (e.target.value !== (truth.reveal_point ?? '')) {
                            void updateTruth(sagaId, truth.id, { reveal_point: e.target.value }).then(refreshTruths);
                          }
                        }}
                        className="w-full bg-transparent"
                      />
                    </td>
                    <td className="px-3 py-2">
                      <select
                        value={truth.status}
                        onChange={(e) =>
                          void updateTruth(sagaId, truth.id, { status: e.target.value }).then(refreshTruths)
                        }
                        className="rounded border border-border bg-background px-2 py-1 text-xs"
                      >
                        {schema.truth_statuses.map((status) => (
                          <option key={status} value={status}>
                            {status}
                          </option>
                        ))}
                      </select>
                    </td>
                    <td className="px-3 py-2 text-right">
                      <button
                        onClick={() => void deleteTruth(sagaId, truth.id).then(refreshTruths)}
                        className="text-xs text-muted-foreground hover:text-destructive"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}

      {tab === 'books' ? (
        <div className="space-y-5">
          <div className="flex flex-wrap items-end gap-2 rounded-lg border border-border/60 bg-card/60 p-4">
            <label className="text-sm">
              <span className="mb-1 block text-xs text-muted-foreground">Attach an existing project</span>
              <select
                defaultValue=""
                onChange={(e) => {
                  void attachProject(e.target.value);
                  e.target.value = '';
                }}
                className="min-w-[280px] rounded-md border border-border bg-background px-3 py-2 text-sm"
              >
                <option value="">Choose a project…</option>
                {available.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            </label>
            <p className="text-xs text-muted-foreground">
              Attaching a standalone project turns it into a series member.
            </p>
          </div>

          <div className="overflow-hidden rounded-lg border border-border/60">
            <table className="w-full text-sm">
              <thead className="bg-muted/50 text-left text-xs uppercase tracking-wide text-muted-foreground">
                <tr>
                  <th className="px-3 py-2">Series</th>
                  <th className="px-3 py-2">Scope</th>
                  <th className="px-3 py-2">Books</th>
                  <th className="px-3 py-2" />
                </tr>
              </thead>
              <tbody>
                {projects.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-3 py-6 text-center text-muted-foreground">
                      Nothing attached yet.
                    </td>
                  </tr>
                ) : null}
                {projects.map((project) => (
                  <tr key={project.id} className="border-t border-border/40">
                    <td className="px-3 py-2">
                      <Link href={`/dashboard/projects/${project.id}`} className="hover:text-primary">
                        {project.name}
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-muted-foreground">{project.scope}</td>
                    <td className="px-3 py-2 font-mono text-xs">{project.book_count}</td>
                    <td className="px-3 py-2 text-right">
                      <button
                        onClick={() => void detachProject(project.id)}
                        className="text-xs text-muted-foreground hover:text-destructive"
                      >
                        Detach
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  );
}
