'use client';

import { BibleCharacter, BibleRelationship, RELATIONSHIP_TYPES } from '@/lib/bible';

interface Props {
  characters: BibleCharacter[];
  relationships: BibleRelationship[];
  selectedId: string | null;
  onSelect: (relationshipId: string) => void;
}

const NEGATIVE = new Set(['enemy', 'rival']);

/**
 * A legible relationship map drawn with plain SVG: characters sit on a ring,
 * typed edges carry their label and intensity. Clicking an edge selects it for
 * editing. Below the md breakpoint the page renders a list instead; this
 * component is hidden there rather than squeezed.
 */
export function RelationshipMap({ characters, relationships, selectedId, onSelect }: Props) {
  if (characters.length === 0 || relationships.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border bg-muted/20 p-6 text-sm text-muted-foreground">
        The map appears once two characters are connected.
      </div>
    );
  }

  const width = 760;
  const height = 440;
  const cx = width / 2;
  const cy = height / 2;
  const radius = characters.length === 1 ? 0 : Math.min(165, 90 + characters.length * 12);

  const positions = new Map<string, { x: number; y: number }>();
  characters.forEach((character, index) => {
    const angle = (index / Math.max(characters.length, 1)) * Math.PI * 2 - Math.PI / 2;
    positions.set(character.id, {
      x: cx + Math.cos(angle) * radius,
      y: cy + Math.sin(angle) * radius * 0.82,
    });
  });

  const nameOf = (id: string) => characters.find((c) => c.id === id)?.name || 'Unknown';

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Relationship map"
      className="h-auto w-full select-none"
    >
      {relationships.map((relationship) => {
        const a = positions.get(relationship.character_a_id);
        const b = positions.get(relationship.character_b_id);
        if (!a || !b) return null;

        const selected = relationship.id === selectedId;
        const strokeWidth = selected ? 2.5 : 0.9 + relationship.intensity * 0.35;
        const midX = (a.x + b.x) / 2;
        const midY = (a.y + b.y) / 2;
        const label = relationship.relationship_type.replace('_', ' ');

        return (
          <g key={relationship.id}>
            <title>
              {nameOf(relationship.character_a_id)} — {label} —{' '}
              {nameOf(relationship.character_b_id)}
            </title>
            <line
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              strokeWidth={16}
              className="cursor-pointer stroke-transparent"
              onClick={() => onSelect(relationship.id)}
            />
            <line
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              strokeWidth={strokeWidth}
              strokeDasharray={NEGATIVE.has(relationship.relationship_type) ? '5 4' : undefined}
              className={`pointer-events-none ${selected ? 'stroke-primary' : 'stroke-border'}`}
            />
            <text
              x={midX}
              y={midY - 4}
              textAnchor="middle"
              className={`pointer-events-none text-[11px] uppercase tracking-wide ${
                selected ? 'fill-primary' : 'fill-muted-foreground'
              }`}
              stroke="none"
            >
              {label}
            </text>
          </g>
        );
      })}

      {characters.map((character) => {
        const position = positions.get(character.id);
        if (!position) return null;
        const onLeft = position.x < cx;
        return (
          <g key={character.id}>
            <circle
              cx={position.x}
              cy={position.y}
              r={4}
              className="fill-foreground"
            />
            <text
              x={onLeft ? position.x - 10 : position.x + 10}
              y={position.y + 4}
              textAnchor={onLeft ? 'end' : 'start'}
              className="fill-foreground text-[13px]"
            >
              {character.name}
            </text>
            <text
              x={onLeft ? position.x - 10 : position.x + 10}
              y={position.y + 19}
              textAnchor={onLeft ? 'end' : 'start'}
              className="fill-muted-foreground text-[10px] uppercase tracking-wide"
            >
              {character.role.replace('_', ' ')}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export function RelationshipTypeOptions() {
  return (
    <>
      {RELATIONSHIP_TYPES.map((type) => (
        <option key={type} value={type}>
          {type.charAt(0).toUpperCase() + type.slice(1)}
        </option>
      ))}
    </>
  );
}
