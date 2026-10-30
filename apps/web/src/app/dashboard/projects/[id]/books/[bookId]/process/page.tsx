'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';

type Step = {
  key: string;
  number: number;
  title: string;
  purpose: string;
  output: string;
  check: string;
  surface: string | null;
  state: 'done' | 'in_progress' | 'pending';
  detail: string;
  current: boolean;
};

type ProcessPayload = {
  book: { id: string; title: string };
  steps: Step[];
  current: string | null;
  totals: { chapters: number; drafted: number; words: number; characters: number; turning_points: number };
};

type ReviewAnswer = { verdict: string; note: string; evidence: string };
type ReviewQuestion = { key: string; label: string; look_for: string };
type ReviewPayload = {
  run: { id: string; created_at: string | null; score: number; words: number; chapters: number } | null;
  questions: ReviewQuestion[];
  answers: Record<string, ReviewAnswer>;
  summary: { counts: Record<string, number>; answered: number; total: number; pct: number };
  totals: { chapters?: number; drafted?: number; words?: number };
};

const STATE_LABEL: Record<Step['state'], string> = {
  done: 'Done',
  in_progress: 'In progress',
  pending: 'Not started',
};

export default function ProcessPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id;
  const bookId = params?.bookId;

  const [process, setProcess] = useState<ProcessPayload | null>(null);
  const [review, setReview] = useState<ReviewPayload | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!projectId || !bookId) return;
    try {
      const [proc, rev] = await Promise.all([
        api<ProcessPayload>(`/api/v1/projects/${projectId}/books/${bookId}/process`),
        api<ReviewPayload>(`/api/v1/projects/${projectId}/books/${bookId}/process/review`),
      ]);
      setProcess(proc);
      setReview(rev);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The process could not be loaded.');
    }
  }, [projectId, bookId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function runReview() {
    if (!projectId || !bookId) return;
    setBusy(true);
    setError(null);
    try {
      const res = await api<ReviewPayload>(`/api/v1/projects/${projectId}/books/${bookId}/process/review/run`, {
        method: 'POST',
      });
      setReview(res);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The review could not run.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="w-full max-w-4xl">
      <header className="mb-8">
        <h1 className="text-2xl font-semibold">The process</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Nine steps, in order, for every book. Each one shows what it produces, the question that says it is
          finished, and where this book actually stands.
        </p>
      </header>

      {error && (
        <div className="mb-6 rounded-lg border border-red-500/40 bg-red-500/5 px-4 py-3 text-sm text-red-500">
          {error}
        </div>
      )}

      {!process && !error && <p className="text-sm text-muted-foreground">Reading the book…</p>}

      {process && (
        <ol className="space-y-3">
          {process.steps.map((step) => {
            const href =
              step.surface === 'series'
                ? `/dashboard/projects/${projectId}/series`
                : `/dashboard/projects/${projectId}/books/${bookId}/${step.surface}`;
            const tone =
              step.state === 'done'
                ? 'text-emerald-500 border-emerald-500/40'
                : step.state === 'in_progress'
                  ? 'text-amber-500 border-amber-500/40'
                  : 'text-muted-foreground border-border';
            return (
              <li
                key={step.key}
                className={`rounded-xl border p-4 ${step.current ? 'border-foreground/30 bg-muted/30' : 'border-border'}`}
              >
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <div className="flex items-baseline gap-3">
                    <span className="text-xs tabular-nums text-muted-foreground">{step.number}</span>
                    <h2 className="text-sm font-medium">{step.title}</h2>
                    {step.current && (
                      <span className="rounded-full bg-foreground px-2 py-0.5 text-[10px] uppercase tracking-wider text-background">
                        you are here
                      </span>
                    )}
                  </div>
                  <span className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-wider ${tone}`}>
                    {STATE_LABEL[step.state]}
                  </span>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">{step.purpose}</p>
                <p className="mt-1 text-xs">
                  <span className="text-muted-foreground">Output:</span> {step.output}
                </p>
                <p className="mt-1 text-xs italic text-muted-foreground">{step.detail}</p>
                <p className="mt-2 text-[11px] text-muted-foreground/80">Check: {step.check}</p>
                {step.surface ? (
                  <Link href={href} className="mt-3 inline-block text-xs font-medium underline underline-offset-4">
                    Open {step.title.toLowerCase()}
                  </Link>
                ) : (
                  <p className="mt-3 text-[11px] text-muted-foreground/70">
                    {step.key === 'canon'
                      ? 'Open the series bible from the project page to record canon.'
                      : 'This review runs on this page.'}
                  </p>
                )}
              </li>
            );
          })}
        </ol>
      )}

      {review && (
        <section className="mt-10 rounded-xl border border-border p-4">
          <div className="mb-3 flex flex-wrap items-start justify-between gap-3">
            <div>
              <h2 className="text-sm font-medium">Manuscript review</h2>
              <p className="mt-1 text-xs text-muted-foreground">
                {review.run
                  ? `Last run ${new Date(review.run.created_at ?? '').toLocaleString()} — ${review.run.chapters} chapters, ${review.run.words.toLocaleString()} words · ${review.summary.counts.pass ?? 0} pass · ${review.summary.counts.partial ?? 0} partial · ${review.summary.counts.fail ?? 0} fail`
                  : 'Judge the book as a whole: promise, character, world, depth, scene life, repetition, earned reveals, series consistency.'}
              </p>
            </div>
            <button
              type="button"
              onClick={() => void runReview()}
              disabled={busy || (process?.totals.drafted ?? 0) === 0}
              title={(process?.totals.drafted ?? 0) === 0 ? 'Write a chapter first' : undefined}
              className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium hover:bg-muted disabled:opacity-40"
            >
              {busy ? 'Reviewing…' : review.run ? 'Review again' : 'Review the manuscript'}
            </button>
          </div>

          {review.run && (
            <div className="divide-y divide-border">
              {review.questions.map((question, index) => {
                const answer = review.answers[question.key];
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
                      <span className={`shrink-0 text-[11px] uppercase tracking-wider ${tone}`}>{verdict}</span>
                    </div>
                    {answer?.note && <p className="mt-1 text-xs text-muted-foreground">{answer.note}</p>}
                    {answer?.evidence && (
                      <p className="mt-1 text-[11px] italic text-muted-foreground/80">{answer.evidence}</p>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </section>
      )}
    </div>
  );
}
