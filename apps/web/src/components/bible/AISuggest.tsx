'use client';

import { useState } from 'react';
import { apiStream } from '@/lib/api';

interface AISuggestProps {
  /** Path to the fiction AI endpoint, including /api/v1. */
  path: string;
  promptType: string;
  label: string;
  /** Extra context appended to the stored story context. */
  context?: string;
  onInsert?: (text: string) => void;
  insertLabel?: string;
}

/**
 * A craft question the model answers into an editable draft.
 * It never writes to a field on its own: the writer reads, edits, then chooses
 * whether to insert it. Discarding leaves the record untouched.
 */
export function AISuggest({
  path,
  promptType,
  label,
  context,
  onInsert,
  insertLabel = 'Insert into this sheet',
}: AISuggestProps) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState('');
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setOpen(true);
    setRunning(true);
    setError(null);
    setDraft('');
    try {
      await apiStream(
        path,
        (chunk) => setDraft((current) => current + chunk),
        {
          method: 'POST',
          body: JSON.stringify({ prompt_type: promptType, context: context || undefined }),
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The assistant did not answer.');
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="min-w-0">
      <button
        type="button"
        onClick={run}
        disabled={running}
        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-left text-sm text-foreground transition-colors hover:bg-muted disabled:opacity-60 sm:w-auto"
      >
        {running ? 'Thinking…' : label}
      </button>

      {open ? (
        <div className="mt-3 rounded-lg border border-border bg-muted/30 p-3">
          <div className="mb-2 flex items-center justify-between gap-3">
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Draft</p>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                setDraft('');
                setError(null);
              }}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              Close
            </button>
          </div>

          {error ? (
            <p className="text-sm text-destructive">{error}</p>
          ) : (
            <textarea
              value={draft}
              rows={10}
              onChange={(e) => setDraft(e.target.value)}
              placeholder={running ? 'Reading the bible…' : ''}
              className="w-full resize-y rounded-lg border border-input bg-background px-3 py-2 font-serif text-sm leading-relaxed text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          )}

          <div className="mt-2 flex flex-wrap items-center gap-2">
            {onInsert ? (
              <button
                type="button"
                disabled={!draft.trim()}
                onClick={() => {
                  onInsert(draft.trim());
                  setOpen(false);
                  setDraft('');
                }}
                className="rounded-lg bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50"
              >
                {insertLabel}
              </button>
            ) : null}
            <button
              type="button"
              onClick={run}
              disabled={running}
              className="rounded-lg border border-border px-3 py-1.5 text-xs text-foreground transition-colors hover:bg-muted disabled:opacity-50"
            >
              Ask again
            </button>
            <span className="text-xs text-muted-foreground">
              Edit the draft before inserting. Nothing is saved until you save the sheet.
            </span>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export function CompletenessMeter({
  filled,
  total,
  label = 'Core fields',
}: {
  filled: number;
  total: number;
  label?: string;
}) {
  const pct = Math.round((filled / Math.max(total, 1)) * 100);
  return (
    <div className="min-w-0">
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-xs uppercase tracking-wider text-muted-foreground">{label}</span>
        <span className="text-xs tabular-nums text-muted-foreground">
          {filled} of {total}
        </span>
      </div>
      <div
        className="mt-1.5 h-1 w-full overflow-hidden rounded-full bg-muted"
        role="progressbar"
        aria-valuenow={filled}
        aria-valuemin={0}
        aria-valuemax={total}
        aria-label={`${label}: ${filled} of ${total}`}
      >
        <div className="h-full bg-primary" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
