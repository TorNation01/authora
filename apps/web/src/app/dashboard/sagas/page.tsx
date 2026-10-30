'use client';

import { useCallback, useEffect, useState } from 'react';
import Link from 'next/link';
import { createSaga, listSagas, type Saga } from '@/lib/saga';

export default function SagasPage() {
  const [sagas, setSagas] = useState<Saga[]>([]);
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await listSagas();
      setSagas(data.sagas);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load sagas.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      const created = await createSaga(name.trim());
      setName('');
      window.location.href = `/dashboard/sagas/${created.saga.id}`;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not create the saga.');
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-5xl px-5 py-8">
      <header className="mb-6">
        <h1 className="font-serif text-3xl text-foreground">Sagas</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          The tier above a series. One saga holds its own truths, its constituent series, and the promises it
          still owes the reader.
        </p>
      </header>

      <form onSubmit={onCreate} className="mb-8 flex flex-wrap gap-2 rounded-lg border border-border/60 bg-card/60 p-4">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Name the saga — working titles are fine"
          className="min-w-[260px] flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={busy || !name.trim()}
          className="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground disabled:opacity-50"
        >
          {busy ? 'Creating…' : 'Create saga'}
        </button>
      </form>

      {error ? <p className="mb-4 text-sm text-destructive">{error}</p> : null}
      {loading ? <p className="text-sm text-muted-foreground">Loading…</p> : null}

      {!loading && sagas.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border/70 p-8 text-center">
          <p className="text-sm text-muted-foreground">
            No sagas yet. Create one, then attach the series that make it up.
          </p>
        </div>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        {sagas.map((saga) => {
          const threads = Object.values(saga.threads || {}).reduce((n, v) => n + v, 0);
          const truths = Object.values(saga.truths || {}).reduce((n, v) => n + v, 0);
          const projects = saga.projects?.length ?? 0;
          return (
            <Link
              key={saga.id}
              href={`/dashboard/sagas/${saga.id}`}
              className="group rounded-lg border border-border/60 bg-card/60 p-4 transition hover:border-primary/50"
            >
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-serif text-lg text-foreground group-hover:text-primary">{saga.name}</h2>
                <span className="font-mono text-xs text-muted-foreground">
                  {saga.completeness.pct}%
                </span>
              </div>
              <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted">
                <div className="h-full bg-primary" style={{ width: `${saga.completeness.pct}%` }} />
              </div>
              <p className="mt-3 text-xs text-muted-foreground">
                {projects} {projects === 1 ? 'series' : 'series'} · {threads} threads · {truths} truths
              </p>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
