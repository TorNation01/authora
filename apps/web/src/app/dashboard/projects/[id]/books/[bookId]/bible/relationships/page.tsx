'use client';

import { useCallback, useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import {
  BibleCharacter,
  BibleRelationship,
  BibleSummary,
  RELATIONSHIP_TYPES,
  fictionBase,
} from '@/lib/bible';
import { RelationshipMap } from '@/components/bible/RelationshipMap';

interface Form {
  character_a_id: string;
  character_b_id: string;
  relationship_type: string;
  intensity: number;
  description: string;
}

const EMPTY_FORM: Form = {
  character_a_id: '',
  character_b_id: '',
  relationship_type: 'ally',
  intensity: 3,
  description: '',
};

export default function RelationshipsPage() {
  const params = useParams<{ id: string; bookId: string }>();
  const projectId = params?.id as string;
  const bookId = params?.bookId as string;
  const base = fictionBase(projectId, bookId);

  const [characters, setCharacters] = useState<BibleCharacter[]>([]);
  const [relationships, setRelationships] = useState<BibleRelationship[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [form, setForm] = useState<Form>(EMPTY_FORM);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api<BibleSummary>(`${base}/summary`);
      setCharacters(data.characters);
      setRelationships(data.relationships);
      setForm((current) => ({
        ...current,
        character_a_id: current.character_a_id || data.characters[0]?.id || '',
        character_b_id:
          current.character_b_id || data.characters.find((c) => c.id !== data.characters[0]?.id)?.id || '',
      }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load relationships.');
    } finally {
      setLoading(false);
    }
  }, [base]);

  useEffect(() => {
    if (projectId && bookId) void load();
  }, [load, projectId, bookId]);

  const nameOf = (id: string) => characters.find((character) => character.id === id)?.name || 'Unknown';

  function selectRelationship(relationship: BibleRelationship) {
    setSelectedId(relationship.id);
    setForm({
      character_a_id: relationship.character_a_id,
      character_b_id: relationship.character_b_id,
      relationship_type: relationship.relationship_type,
      intensity: relationship.intensity || 3,
      description: relationship.description || '',
    });
  }

  function reset() {
    setSelectedId(null);
    setForm({
      ...EMPTY_FORM,
      character_a_id: characters[0]?.id || '',
      character_b_id: characters.find((c) => c.id !== characters[0]?.id)?.id || '',
    });
  }

  async function save() {
    if (form.character_a_id === form.character_b_id) {
      setError('A character cannot be in a relationship with themselves.');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const payload = {
        character_a_id: form.character_a_id,
        character_b_id: form.character_b_id,
        relationship_type: form.relationship_type,
        intensity: Number(form.intensity),
        description: form.description.trim() || null,
      };
      if (selectedId) {
        const updated = await api<BibleRelationship>(`${base}/relationships/${selectedId}`, {
          method: 'PATCH',
          body: JSON.stringify(payload),
        });
        setRelationships((current) =>
          current.map((item) => (item.id === updated.id ? updated : item))
        );
      } else {
        const created = await api<BibleRelationship>(`${base}/relationships`, {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        setRelationships((current) => [...current, created]);
        setSelectedId(created.id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save the relationship.');
    } finally {
      setSaving(false);
    }
  }

  async function remove() {
    if (!selectedId) return;
    try {
      await api(`${base}/relationships/${selectedId}`, { method: 'DELETE' });
      setRelationships((current) => current.filter((item) => item.id !== selectedId));
      reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not delete the relationship.');
    }
  }

  if (loading) return <p className="text-sm text-muted-foreground">Loading relationships…</p>;

  if (characters.length < 2) {
    return (
      <div className="min-w-0">
        <h1 className="font-serif text-2xl font-bold text-foreground">Relationships</h1>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
          A relationship needs two people. Add at least two characters on the Characters screen
          and the map will have something to draw.
        </p>
      </div>
    );
  }

  return (
    <div className="min-w-0">
      <header className="mb-6">
        <h1 className="font-serif text-2xl font-bold text-foreground">Relationships</h1>
        <p className="mt-1 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          Every line is a pressure the plot can lean on. Click an edge to edit it.
        </p>
      </header>

      <div className="mb-8 hidden rounded-xl border border-border p-2 md:block">
        <RelationshipMap
          characters={characters}
          relationships={relationships}
          selectedId={selectedId}
          onSelect={(id) => {
            const relationship = relationships.find((item) => item.id === id);
            if (relationship) selectRelationship(relationship);
          }}
        />
      </div>

      <section className="mb-10">
        <h2 className="mb-3 font-serif text-lg font-semibold text-foreground">
          Connections ({relationships.length})
        </h2>
        {relationships.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Nothing connects them yet. What does one owe the other — and what would break it?
          </p>
        ) : (
          <ul className="divide-y divide-border border-y border-border">
            {relationships.map((relationship) => {
              const active = relationship.id === selectedId;
              return (
                <li key={relationship.id}>
                  <button
                    type="button"
                    onClick={() => selectRelationship(relationship)}
                    className={`w-full px-2 py-3 text-left transition-colors ${
                      active ? 'bg-muted/60' : 'hover:bg-muted/30'
                    }`}
                  >
                    <div className="flex flex-wrap items-baseline gap-x-2 gap-y-1">
                      <span className="text-sm font-medium text-foreground">
                        {nameOf(relationship.character_a_id)}
                      </span>
                      <span className="text-xs uppercase tracking-wider text-muted-foreground">
                        {relationship.relationship_type}
                      </span>
                      <span className="text-sm font-medium text-foreground">
                        {nameOf(relationship.character_b_id)}
                      </span>
                      <span className="ml-auto text-xs tabular-nums text-muted-foreground">
                        intensity {relationship.intensity}/5
                      </span>
                    </div>
                    {relationship.description ? (
                      <p className="mt-1 break-words text-xs leading-relaxed text-muted-foreground">
                        {relationship.description}
                      </p>
                    ) : null}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section className="rounded-xl border border-border p-5">
        <h2 className="font-serif text-lg font-semibold text-foreground">
          {selectedId ? 'Edit this connection' : 'Add a connection'}
        </h2>
        <p className="mb-5 mt-1 text-sm leading-relaxed text-muted-foreground">
          Name what binds them and what it costs to keep. A relationship with no cost will not
          hold a scene.
        </p>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="min-w-0">
            <label htmlFor="rel-a" className="block text-sm font-medium text-foreground">
              Character
            </label>
            <select
              id="rel-a"
              value={form.character_a_id}
              onChange={(event) => setForm({ ...form, character_a_id: event.target.value })}
              className="mt-2 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {characters.map((character) => (
                <option key={character.id} value={character.id}>
                  {character.name}
                </option>
              ))}
            </select>
          </div>

          <div className="min-w-0">
            <label htmlFor="rel-b" className="block text-sm font-medium text-foreground">
              Is connected to
            </label>
            <select
              id="rel-b"
              value={form.character_b_id}
              onChange={(event) => setForm({ ...form, character_b_id: event.target.value })}
              className="mt-2 w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {characters.map((character) => (
                <option key={character.id} value={character.id}>
                  {character.name}
                </option>
              ))}
            </select>
          </div>

          <div className="min-w-0">
            <label htmlFor="rel-type" className="block text-sm font-medium text-foreground">
              Type
            </label>
            <p className="mb-2 mt-1 text-xs text-muted-foreground">
              What are they to each other when it matters?
            </p>
            <select
              id="rel-type"
              value={form.relationship_type}
              onChange={(event) => setForm({ ...form, relationship_type: event.target.value })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {RELATIONSHIP_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="min-w-0">
            <label htmlFor="rel-intensity" className="block text-sm font-medium text-foreground">
              Intensity
            </label>
            <p className="mb-2 mt-1 text-xs text-muted-foreground">
              How much of the book does this relationship carry?
            </p>
            <select
              id="rel-intensity"
              value={form.intensity}
              onChange={(event) => setForm({ ...form, intensity: Number(event.target.value) })}
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            >
              {[1, 2, 3, 4, 5].map((value) => (
                <option key={value} value={value}>
                  {value} — {value === 5 ? 'load-bearing' : value === 1 ? 'background' : 'present'}
                </option>
              ))}
            </select>
          </div>

          <div className="min-w-0 sm:col-span-2">
            <label htmlFor="rel-note" className="block text-sm font-medium text-foreground">
              One line
            </label>
            <p className="mb-2 mt-1 text-xs text-muted-foreground">
              What does one owe the other — and what would break it?
            </p>
            <input
              id="rel-note"
              value={form.description}
              onChange={(event) => setForm({ ...form, description: event.target.value })}
              placeholder="He taught her to read; she will be the one who testifies against him."
              className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={save}
            disabled={saving}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary-hover disabled:opacity-60"
          >
            {saving ? 'Saving…' : selectedId ? 'Save connection' : 'Add connection'}
          </button>
          {selectedId ? (
            <>
              <button
                type="button"
                onClick={reset}
                className="rounded-lg border border-border px-3 py-2 text-sm text-foreground transition-colors hover:bg-muted"
              >
                New connection
              </button>
              <button
                type="button"
                onClick={remove}
                className="ml-auto text-xs text-muted-foreground underline-offset-4 hover:text-destructive hover:underline"
              >
                Delete connection
              </button>
            </>
          ) : null}
        </div>
        {error ? <p className="mt-3 text-sm text-destructive">{error}</p> : null}
      </section>
    </div>
  );
}
