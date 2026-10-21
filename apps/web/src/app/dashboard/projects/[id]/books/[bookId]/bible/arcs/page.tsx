'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import {
  ArcBeat,
  BibleArc,
  BibleChapter,
  BibleCharacter,
  BibleSummary,
  fetchChapters,
  fictionBase,
} from '@/lib/bible';
import { AISuggest } from '@/components/bible/AISuggest';

const inputClass =
  'w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring';

/** Turn the editor's BEAT/WHAT CHANGES/CHAPTER/EMOTIONAL TURN answer into beats. */
function parseBeats(text: string): ArcBeat[] {
  const blocks = text.split(/\n(?=BEAT:)/i).filter((block) => /BEAT:/i.test(block));
  if (blocks.length === 0) {
    return [{ label: 'Suggested beat', change: text.trim(), chapter: '', emotional_turn: '' }];
  }
  return blocks.slice(0, 3).map((block) => ({
    label: (block.match(/BEAT:\s*(.+)/i)?.[1] || 'Beat').trim(),
    change: (
      block.match(/WHAT CHANGES:\s*([\s\S]*?)(?=\n(?:CHAPTER|EMOTIONAL TURN|BEAT):|$)/i)?.[1] || ''
    ).trim(),
    chapter: (block.match(/CHAPTER:\s*(.+)/i)?.[1] || '').trim(),
    emotional_turn: (
      block.match(/EMOTIONAL TURN:\s*([\s\S]*?)(?=\n(?:BEAT|WHAT CHANGES|CHAPTER):|$)/i)?.[1] || ''
    ).trim(),
  }));
}

export default function ArcsPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = fictionBase(projectId, bookId);

  const [characters, setCharacters] = useState<BibleCharacter[]>([]);
  const [arcs, setArcs] = useState<BibleArc[]>([]);
  const [chapters, setChapters] = useState<BibleChapter[]>([]);
  const [characterId, setCharacterId] = useState<string>('');
  const [beats, setBeats] = useState<ArcBeat[]>([]);
  const [arcId, setArcId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [summary, chapterList] = await Promise.all([
        api<BibleSummary>(`${base}/summary`),
        fetchChapters(projectId, bookId),
      ]);
      setCharacters(summary.characters);
      setArcs(summary.plot_arcs);
      setChapters(Array.isArray(chapterList) ? chapterList : []);
      setCharacterId((current) => current || summary.characters[0]?.id || '');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load arcs.');
    } finally {
      setLoading(false);
    }
  }, [base, projectId, bookId]);

  useEffect(() => {
    if (projectId && bookId) void load();
  }, [load, projectId, bookId]);

  const character = useMemo(
    () => characters.find((item) => item.id === characterId) || null,
    [characters, characterId]
  );

  const arc = useMemo(
    () => arcs.find((item) => item.character_id === characterId) || null,
    [arcs, characterId]
  );

  useEffect(() => {
    setArcId(arc?.id ?? null);
    setBeats(Array.isArray(arc?.beats) ? (arc?.beats as ArcBeat[]) : []);
    setStatus(null);
  }, [arc]);

  async function ensureArc(): Promise<string | null> {
    if (arcId) return arcId;
    if (!character) return null;
    const created = await api<BibleArc>(`${base}/arcs`, {
      method: 'POST',
      body: JSON.stringify({
        name: `${character.name}'s arc`,
        structure: 'three_act',
        character_id: character.id,
        beats: [],
      }),
    });
    setArcs((current) => [...current, created]);
    setArcId(created.id);
    return created.id;
  }

  async function save() {
    setSaving(true);
    setError(null);
    try {
      const id = await ensureArc();
      if (!id) return;
      const updated = await api<BibleArc>(`${base}/arcs/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({ beats }),
      });
      setArcs((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setStatus('Saved');
      setTimeout(() => setStatus(null), 2500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save the arc.');
      setStatus(null);
    } finally {
      setSaving(false);
    }
  }

  function updateBeat(index: number, key: keyof ArcBeat, value: string) {
    setBeats((current) =>
      current.map((beat, i) => (i === index ? { ...beat, [key]: value } : beat))
    );
    setStatus(null);
  }

  function move(index: number, direction: -1 | 1) {
    const target = index + direction;
    if (target < 0 || target >= beats.length) return;
    setBeats((current) => {
      const next = [...current];
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
    setStatus(null);
  }

  function removeBeat(index: number) {
    setBeats((current) => current.filter((_, i) => i !== index));
    setStatus(null);
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading arcs…</p>;

  if (characters.length === 0) {
    return (
      <div className="min-w-0">
        <h1 className="font-serif text-2xl font-bold text-foreground">Arcs</h1>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
          An arc belongs to a character. Create one on the Characters screen first, then come
          back and break it.
        </p>
      </div>
    );
  }

  return (
    <div className="min-w-0">
      <header className="mb-6">
        <h1 className="font-serif text-2xl font-bold text-foreground">Arcs</h1>
        <p className="mt-1 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          Beats are ordered by what changes, not by what happens. If a beat could be moved
          without the arc noticing, it is a scene, not a beat.
        </p>
      </header>

      <div className="mb-6 max-w-sm">
        <label htmlFor="arc-character" className="block text-sm font-medium text-foreground">
          Whose arc
        </label>
        <select
          id="arc-character"
          value={characterId}
          onChange={(event) => setCharacterId(event.target.value)}
          className={`mt-2 ${inputClass}`}
        >
          {characters.map((item) => (
            <option key={item.id} value={item.id}>
              {item.name}
            </option>
          ))}
        </select>
      </div>

      <datalist id="chapter-anchors">
        {chapters.map((chapter) => (
          <option key={chapter.id} value={`Ch. ${chapter.sort_order + 1} — ${chapter.title}`} />
        ))}
      </datalist>

      <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="font-serif text-lg font-semibold text-foreground">
          {beats.length} {beats.length === 1 ? 'beat' : 'beats'}
        </h2>
        <div className="flex items-center gap-3">
          {status ? <span className="text-xs text-muted-foreground">{status}</span> : null}
          <button
            type="button"
            onClick={() => {
              setBeats((current) => [
                ...current,
                { label: '', change: '', chapter: '', emotional_turn: '' },
              ]);
              setStatus(null);
            }}
            className="rounded-lg border border-border px-3 py-1.5 text-sm text-foreground transition-colors hover:bg-muted"
          >
            Add beat
          </button>
        </div>
      </div>

      {beats.length === 0 ? (
        <div className="rounded-xl border border-dashed border-border p-6">
          <p className="font-serif text-lg text-foreground">
            Who is {character?.name || 'this character'} at the start — and what do they believe
            that the book will take away from them?
          </p>
          <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
            Add a first beat, or ask for three that break the arc. Beats save with the arc, so
            nothing is written until you press Save.
          </p>
        </div>
      ) : (
        <ol className="space-y-4">
          {beats.map((beat, index) => (
            <li key={index} className="rounded-xl border border-border p-4">
              <div className="mb-3 flex items-center justify-between gap-2">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">
                  Beat {index + 1}
                </span>
                <div className="flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => move(index, -1)}
                    disabled={index === 0}
                    aria-label={`Move beat ${index + 1} up`}
                    className="text-xs text-muted-foreground hover:text-foreground disabled:opacity-30"
                  >
                    Up
                  </button>
                  <button
                    type="button"
                    onClick={() => move(index, 1)}
                    disabled={index === beats.length - 1}
                    aria-label={`Move beat ${index + 1} down`}
                    className="text-xs text-muted-foreground hover:text-foreground disabled:opacity-30"
                  >
                    Down
                  </button>
                  <button
                    type="button"
                    onClick={() => removeBeat(index)}
                    className="text-xs text-muted-foreground hover:text-destructive"
                  >
                    Remove
                  </button>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="min-w-0">
                  <label className="block text-sm font-medium text-foreground">
                    Beat label
                  </label>
                  <p className="mb-2 mt-1 text-xs text-muted-foreground">
                    Name the beat in three words.
                  </p>
                  <input
                    value={beat.label || beat.name || ''}
                    onChange={(event) => updateBeat(index, 'label', event.target.value)}
                    placeholder="The refusal"
                    className={inputClass}
                  />
                </div>
                <div className="min-w-0">
                  <label className="block text-sm font-medium text-foreground">
                    Chapter anchor
                  </label>
                  <p className="mb-2 mt-1 text-xs text-muted-foreground">
                    Which chapter carries it?
                  </p>
                  <input
                    value={beat.chapter || ''}
                    onChange={(event) => updateBeat(index, 'chapter', event.target.value)}
                    list="chapter-anchors"
                    placeholder="Ch. 12"
                    className={inputClass}
                  />
                </div>
                <div className="min-w-0 sm:col-span-2">
                  <label className="block text-sm font-medium text-foreground">
                    What changes
                  </label>
                  <p className="mb-2 mt-1 text-xs text-muted-foreground">
                    A change in belief or allegiance — not an event.
                  </p>
                  <textarea
                    rows={2}
                    value={beat.change || beat.description || ''}
                    onChange={(event) => updateBeat(index, 'change', event.target.value)}
                    className={`${inputClass} resize-y leading-relaxed`}
                  />
                </div>
                <div className="min-w-0 sm:col-span-2">
                  <label className="block text-sm font-medium text-foreground">
                    Emotional turn
                  </label>
                  <p className="mb-2 mt-1 text-xs text-muted-foreground">
                    What feeling do they move from, and to?
                  </p>
                  <input
                    value={beat.emotional_turn || ''}
                    onChange={(event) => updateBeat(index, 'emotional_turn', event.target.value)}
                    placeholder="From certainty to shame"
                    className={inputClass}
                  />
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3 border-t border-border pt-4">
        <button
          type="button"
          onClick={save}
          disabled={saving}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-60"
        >
          {saving ? 'Saving…' : 'Save arc'}
        </button>
        {error ? <span className="text-sm text-destructive">{error}</span> : null}
      </div>

      <section className="mt-10 border-t border-border pt-6">
        <h2 className="font-serif text-lg font-semibold text-foreground">Break this arc</h2>
        <p className="mb-4 mt-1 text-sm leading-relaxed text-muted-foreground">
          Three beats that complicate the arc rather than complete it. They arrive as a draft;
          add them only if they cost the character something.
        </p>
        <AISuggest
          path={`${base}/ai`}
          promptType="arc_beats"
          label="Suggest three beats that break this arc"
          insertLabel="Add these beats to the arc"
          context={`The arc belongs to ${character?.name || 'the protagonist'}. Existing beats are in the context.`}
          onInsert={(text) => {
            const parsed = parseBeats(text);
            setBeats((current) => [...current, ...parsed]);
            setStatus(null);
          }}
        />
      </section>
    </div>
  );
}
