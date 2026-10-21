'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import {
  BibleChapter,
  BibleCharacter,
  BibleSummary,
  BibleTimelineEvent,
  fetchChapters as loadChapters,
  fictionBase,
  vaultBase,
} from '@/lib/bible';

const inputClass =
  'w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring';

interface Draft {
  title: string;
  date_label: string;
  chapter_id: string;
  character_ids: string[];
  description: string;
}

const EMPTY: Draft = {
  title: '',
  date_label: '',
  chapter_id: '',
  character_ids: [],
  description: '',
};

export default function TimelinePage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = fictionBase(projectId, bookId);
  const vault = vaultBase(projectId);

  const [events, setEvents] = useState<BibleTimelineEvent[]>([]);
  const [characters, setCharacters] = useState<BibleCharacter[]>([]);
  const [chapters, setChapters] = useState<BibleChapter[]>([]);
  const [draft, setDraft] = useState<Draft>(EMPTY);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [summary, chapterList, timeline] = await Promise.all([
        api<BibleSummary>(`${base}/summary`),
        loadChapters(projectId, bookId),
        api<BibleTimelineEvent[]>(`${vault}/timeline?book_id=${bookId}`),
      ]);
      setCharacters(summary.characters);
      setChapters(Array.isArray(chapterList) ? chapterList : []);
      setEvents(Array.isArray(timeline) ? timeline : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the timeline.');
    } finally {
      setLoading(false);
    }
  }, [base, vault, projectId, bookId]);

  useEffect(() => {
    if (projectId && bookId) void load();
  }, [load, projectId, bookId]);

  async function create() {
    if (!draft.title.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await api(`${vault}/timeline`, {
        method: 'POST',
        body: JSON.stringify({
          title: draft.title.trim(),
          date_label: draft.date_label.trim() || null,
          chapter_id: draft.chapter_id || null,
          character_ids: draft.character_ids,
          description: draft.description.trim() || null,
          book_id: bookId,
          sequence_order:
            events.length > 0 ? Math.max(...events.map((event) => event.sequence_order || 0)) + 1 : 0,
        }),
      });
      setDraft(EMPTY);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not add the event.');
    } finally {
      setBusy(false);
    }
  }

  async function remove(event: BibleTimelineEvent) {
    if (!window.confirm(`Remove “${event.title}” from the timeline?`)) return;
    try {
      await api(`${vault}/timeline/${event.id}`, { method: 'DELETE' });
      setEvents((current) => current.filter((item) => item.id !== event.id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not remove the event.');
    }
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading the timeline…</p>;

  return (
    <div className="min-w-0">
      <header className="mb-8">
        <h1 className="font-serif text-2xl font-bold text-foreground">Timeline</h1>
        <p className="mt-1 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          Story time is not chapter order. Record what happened when, so a flashback cannot
          contradict a thing a character already knows.
        </p>
      </header>

      {events.length === 0 ? (
        <p className="mb-6 text-sm text-muted-foreground">
          No events yet. Start with the thing that happened before page one — the one everybody
          in the book is still reacting to.
        </p>
      ) : (
        <ol className="mb-10 border-l border-border">
          {events
            .slice()
            .sort((a, b) => (a.sequence_order || 0) - (b.sequence_order || 0))
            .map((event) => {
              const chapter = chapters.find((item) => item.id === event.chapter_id);
              const present = (event.character_ids || [])
                .map((id) => characters.find((character) => character.id === id)?.name)
                .filter(Boolean);
              return (
                <li key={event.id} className="relative pl-5 pb-6">
                  <span className="absolute -left-[3px] top-2 h-1.5 w-1.5 rounded-full bg-foreground" />
                  <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                    {event.date_label ? (
                      <span className="text-xs uppercase tracking-wider text-muted-foreground">
                        {event.date_label}
                      </span>
                    ) : null}
                    {chapter ? (
                      <span className="text-xs text-muted-foreground">
                        Ch. {chapter.sort_order + 1} — {chapter.title}
                      </span>
                    ) : null}
                    <button
                      type="button"
                      onClick={() => remove(event)}
                      className="ml-auto text-xs text-muted-foreground hover:text-destructive"
                    >
                      Remove
                    </button>
                  </div>
                  <p className="mt-1 font-serif text-base font-semibold text-foreground">
                    {event.title}
                  </p>
                  {event.description ? (
                    <p className="mt-1 break-words text-sm leading-relaxed text-muted-foreground">
                      {event.description}
                    </p>
                  ) : null}
                  {present.length > 0 ? (
                    <p className="mt-1 text-xs text-muted-foreground">
                      Present: {present.join(', ')}
                    </p>
                  ) : null}
                </li>
              );
            })}
        </ol>
      )}

      <section className="rounded-xl border border-border p-5">
        <h2 className="font-serif text-lg font-semibold text-foreground">Add an event</h2>
        <p className="mb-4 mt-1 text-sm leading-relaxed text-muted-foreground">
          One line is enough. The chapter anchor is where the reader learns it, which may be
          later than when it happened.
        </p>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="min-w-0 sm:col-span-2">
            <label htmlFor="event-title" className="block text-sm font-medium text-foreground">
              What happens
            </label>
            <input
              id="event-title"
              value={draft.title}
              onChange={(event) => setDraft({ ...draft, title: event.target.value })}
              placeholder="The customs house burns with her father's name still on the ledger."
              className={`mt-2 ${inputClass}`}
            />
          </div>

          <div className="min-w-0">
            <label htmlFor="event-when" className="block text-sm font-medium text-foreground">
              When, in story time
            </label>
            <p className="mb-2 mt-1 text-xs text-muted-foreground">
              A date, a season, or “eleven years before”.
            </p>
            <input
              id="event-when"
              value={draft.date_label}
              onChange={(event) => setDraft({ ...draft, date_label: event.target.value })}
              placeholder="Late winter, year 11 of the Compact"
              className={inputClass}
            />
          </div>

          <div className="min-w-0">
            <label htmlFor="event-chapter" className="block text-sm font-medium text-foreground">
              Where the reader learns it
            </label>
            <p className="mb-2 mt-1 text-xs text-muted-foreground">
              Which chapter carries this event?
            </p>
            <select
              id="event-chapter"
              value={draft.chapter_id}
              onChange={(event) => setDraft({ ...draft, chapter_id: event.target.value })}
              className={inputClass}
            >
              <option value="">Not placed yet</option>
              {chapters.map((chapter) => (
                <option key={chapter.id} value={chapter.id}>
                  Ch. {chapter.sort_order + 1} — {chapter.title}
                </option>
              ))}
            </select>
          </div>

          <div className="min-w-0 sm:col-span-2">
            <label className="block text-sm font-medium text-foreground">Who is present</label>
            <p className="mb-2 mt-1 text-xs text-muted-foreground">
              Everyone in the room, whether or not they speak.
            </p>
            {characters.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No characters yet — add them on the Characters screen.
              </p>
            ) : (
              <div className="flex flex-wrap gap-x-4 gap-y-2">
                {characters.map((character) => {
                  const checked = draft.character_ids.includes(character.id);
                  return (
                    <label key={character.id} className="flex items-center gap-2 text-sm text-foreground">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={(event) =>
                          setDraft({
                            ...draft,
                            character_ids: event.target.checked
                              ? [...draft.character_ids, character.id]
                              : draft.character_ids.filter((id) => id !== character.id),
                          })
                        }
                        className="h-4 w-4 rounded border-input"
                      />
                      {character.name}
                    </label>
                  );
                })}
              </div>
            )}
          </div>

          <div className="min-w-0 sm:col-span-2">
            <label htmlFor="event-description" className="block text-sm font-medium text-foreground">
              What changes because of it
            </label>
            <textarea
              id="event-description"
              rows={2}
              value={draft.description}
              onChange={(event) => setDraft({ ...draft, description: event.target.value })}
              className={`mt-2 resize-y leading-relaxed ${inputClass}`}
            />
          </div>
        </div>

        <div className="mt-4 flex items-center gap-3">
          <button
            type="button"
            onClick={create}
            disabled={busy || !draft.title.trim()}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-50"
          >
            {busy ? 'Adding…' : 'Add event'}
          </button>
          {error ? <span className="text-sm text-destructive">{error}</span> : null}
        </div>
      </section>
    </div>
  );
}
