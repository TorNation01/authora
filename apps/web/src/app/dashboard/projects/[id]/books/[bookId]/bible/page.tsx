'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import {
  BibleSummary,
  BibleWorkspace,
  OVERVIEW_FIELDS,
  fictionBase,
} from '@/lib/bible';
import { Field, SaveStatus, SectionHeading } from '@/components/bible/Field';
import { AISuggest } from '@/components/bible/AISuggest';

type FormState = Record<string, string>;

function toForm(ws: BibleWorkspace): FormState {
  return {
    premise: ws.premise || '',
    logline: ws.logline || '',
    central_question: ws.central_question || '',
    genre: ws.genre || '',
    subgenre: ws.subgenre || '',
    audience: ws.audience || '',
    pov: ws.pov || '',
    tense: ws.tense || '',
    target_word_count: ws.target_word_count ? String(ws.target_word_count) : '',
    comparable_titles: (ws.comparable_titles || []).join(', '),
    tone: ws.tone || '',
  };
}

export default function BibleOverviewPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = fictionBase(projectId, bookId);

  const [summary, setSummary] = useState<BibleSummary | null>(null);
  const [form, setForm] = useState<FormState>({});
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api<BibleSummary>(`${base}/summary`);
      setSummary(data);
      setForm(toForm(data.workspace));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the bible.');
    } finally {
      setLoading(false);
    }
  }, [base]);

  useEffect(() => {
    if (projectId && bookId) void load();
  }, [load, projectId, bookId]);

  const filledCount = useMemo(
    () => Object.values(form).filter((value) => value && value.trim().length > 0).length,
    [form]
  );

  async function save() {
    setStatus('saving');
    try {
      const payload: Record<string, unknown> = {};
      for (const field of OVERVIEW_FIELDS) {
        const raw = form[field.key as string] ?? '';
        if (field.key === 'target_word_count') {
          payload[field.key] = raw.trim() ? Number(raw.replace(/[^0-9]/g, '')) : null;
        } else if (field.key === 'comparable_titles') {
          payload[field.key] = raw
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean);
        } else {
          payload[field.key] = raw.trim() ? raw : null;
        }
      }
      const updated = await api<BibleWorkspace>(`${base}/workspace`, {
        method: 'PATCH',
        body: JSON.stringify(payload),
      });
      setSummary((current) => (current ? { ...current, workspace: updated } : current));
      setStatus('saved');
      setTimeout(() => setStatus('idle'), 2500);
    } catch {
      setStatus('error');
    }
  }

  const shortFields = OVERVIEW_FIELDS.filter((f) => !f.multiline);

  if (loading) {
    return <p className="text-sm text-muted-foreground">Loading the bible…</p>;
  }

  if (error) {
    return <p className="text-sm text-destructive">{error}</p>;
  }

  return (
    <div className="min-w-0">
      <header className="mb-8">
        <h1 className="font-serif text-2xl font-bold text-foreground">Book Bible</h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          The questions below are the ones a finished book has already answered. Answer them
          roughly first — a wrong answer you can see is worth more than a blank you are still
          circling.
        </p>
      </header>

      <div className="mb-8 grid grid-cols-2 gap-4 border-y border-border py-4 sm:grid-cols-4">
        {[
          { label: 'Overview answered', value: `${filledCount} of ${OVERVIEW_FIELDS.length}` },
          { label: 'Characters', value: String(summary?.characters.length ?? 0) },
          { label: 'Relationships', value: String(summary?.relationships.length ?? 0) },
          { label: 'Arcs', value: String(summary?.plot_arcs.length ?? 0) },
        ].map((stat) => (
          <div key={stat.label} className="min-w-0">
            <p className="text-xs uppercase tracking-wider text-muted-foreground">{stat.label}</p>
            <p className="mt-1 font-serif text-lg text-foreground">{stat.value}</p>
          </div>
        ))}
      </div>

      <section className="mb-8">
        <SectionHeading
          title="The story in brief"
          description="If these three answers are wrong, every chapter written from them will be wrong too."
        />
        <div className="space-y-6">
          {OVERVIEW_FIELDS.filter((f) => f.multiline).map((field) => (
            <Field
              key={field.key as string}
              label={field.label}
              question={field.question}
              value={form[field.key as string] || ''}
              rows={field.rows}
              placeholder={field.placeholder}
              multiline
              onChange={(value) => setForm((current) => ({ ...current, [field.key]: value }))}
            />
          ))}
        </div>
      </section>

      <section className="mb-8 rounded-xl border border-border p-5">
        <SectionHeading
          title="How the book is built"
          description="The choices a reader never notices but a writer cannot change late without rewriting."
        />
        <div className="grid gap-5 sm:grid-cols-2">
          {shortFields.map((field) => (
            <Field
              key={field.key as string}
              label={field.label}
              question={field.question}
              value={form[field.key as string] || ''}
              placeholder={field.placeholder}
              type={field.key === 'target_word_count' ? 'text' : 'text'}
              onChange={(value) => setForm((current) => ({ ...current, [field.key]: value }))}
            />
          ))}
        </div>
      </section>

      <div className="mb-10 flex flex-wrap items-center gap-3 border-t border-border pt-5">
        <button
          type="button"
          onClick={save}
          disabled={status === 'saving'}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-60"
        >
          {status === 'saving' ? 'Saving…' : 'Save the bible'}
        </button>
        <SaveStatus state={status} />
        <span className="text-xs text-muted-foreground">
          Changing a field here does not rewrite any chapter.
        </span>
      </div>

      <section className="mb-4">
        <SectionHeading
          title="Before you write another chapter"
          description="A developmental question with the whole bible in front of it. The answer arrives as a draft you can edit."
        />
        <AISuggest
          path={`${base}/ai`}
          promptType="premise_scope"
          label="Is this premise a book or a short story?"
          context={`The writer wants ${form.target_word_count || 'an unstated number of'} words. Judge whether the premise carries that length.`}
        />
      </section>
    </div>
  );
}
