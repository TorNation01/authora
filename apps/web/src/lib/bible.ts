/**
 * Book Bible: types, API paths and the questions that make the fields useful.
 *
 * Every field here maps to a real column on the fiction_* / vault_* tables —
 * nothing in this file is presentation-only. The `question` strings are the
 * interview the writer is being asked; they are the point of the section.
 */
import { api } from '@/lib/api';

export interface BibleWorkspace {
  id: string;
  book_id: string;
  premise: string | null;
  logline: string | null;
  genre: string | null;
  subgenre: string | null;
  audience: string | null;
  pov: string | null;
  tense: string | null;
  target_word_count: number | null;
  comparable_titles: string[] | null;
  central_question: string | null;
  tone: string | null;
  themes: string[] | null;
  pacing_notes: string | null;
  protagonist_id: string | null;
  antagonist_id: string | null;
}

export type CharacterRole =
  | 'protagonist'
  | 'antagonist'
  | 'love_interest'
  | 'mentor'
  | 'foil'
  | 'minor'
  | 'supporting';

export interface BibleCharacter {
  id: string;
  book_id: string;
  name: string;
  role: CharacterRole;
  description: string | null;
  age: string | null;
  appearance: string | null;
  voice: string | null;
  backstory: string | null;
  goals: string | null;
  need: string | null;
  wound: string | null;
  flaws: string | null;
  secret: string | null;
  arc_summary: string | null;
  first_appearance: string | null;
  status: string;
  traits: Record<string, unknown> | null;
  sort_order: number;
}

export interface BibleRelationship {
  id: string;
  book_id: string;
  character_a_id: string;
  character_b_id: string;
  relationship_type: string;
  description: string | null;
  arc_notes: string | null;
  intensity: number;
}

export interface ArcBeat {
  label?: string;
  change?: string;
  chapter?: string;
  emotional_turn?: string;
  /** Legacy beat shape written by earlier versions of the planner. */
  name?: string;
  description?: string;
  chapter_id?: string;
}

export interface BibleArc {
  id: string;
  book_id: string;
  name: string;
  structure: string;
  character_id: string | null;
  beats: ArcBeat[] | null;
  sort_order: number;
}

export type WorldCategory = 'location' | 'faction' | 'rule' | string;

export interface BibleWorldElement {
  id: string;
  book_id: string;
  category: WorldCategory;
  name: string;
  description: string | null;
  details: Record<string, unknown> | null;
  sort_order: number;
}

export interface BibleTheme {
  id: string;
  project_id: string;
  book_id: string | null;
  name: string;
  theme_type: string;
  description: string | null;
  notes: string | null;
  is_central: boolean;
  sort_order: number;
}

export interface BibleTimelineEvent {
  id: string;
  project_id: string;
  book_id: string | null;
  title: string;
  description: string | null;
  event_type: string;
  event_date: string | null;
  date_label: string | null;
  chapter_id: string | null;
  character_ids: string[];
  sequence_order: number;
  storyline: string | null;
  time_period: string | null;
}

export interface BibleChapter {
  id: string;
  book_id: string;
  title: string;
  sort_order: number;
  word_count: number;
}

export interface BibleSummary {
  workspace: BibleWorkspace;
  characters: BibleCharacter[];
  relationships: BibleRelationship[];
  world_elements: BibleWorldElement[];
  plot_arcs: BibleArc[];
}

export const fictionBase = (projectId: string, bookId: string) =>
  `/api/v1/projects/${projectId}/books/${bookId}/fiction`;

export const vaultBase = (projectId: string) => `/api/v1/projects/${projectId}/vault`;

export const chaptersBase = (projectId: string, bookId: string) =>
  `/api/v1/projects/${projectId}/books/${bookId}/chapters`;

/**
 * Chapters are returned on the book payload rather than a list endpoint;
 * fetch the book and take its ordered chapters.
 */
export async function fetchChapters(projectId: string, bookId: string): Promise<BibleChapter[]> {
  if (!projectId || !bookId) return [];
  try {
    const book = await api<{ chapters?: BibleChapter[] }>(
      `/api/v1/projects/${projectId}/books/${bookId}`
    );
    const chapters = Array.isArray(book.chapters) ? book.chapters : [];
    return chapters.slice().sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0));
  } catch {
    return [];
  }
}

export const ROLE_LABELS: Record<string, string> = {
  protagonist: 'Protagonist',
  antagonist: 'Antagonist',
  love_interest: 'Love interest',
  mentor: 'Mentor',
  foil: 'Foil',
  minor: 'Minor',
  supporting: 'Supporting',
};

export const RELATIONSHIP_TYPES = [
  'ally',
  'rival',
  'parent',
  'sibling',
  'mentor',
  'lover',
  'enemy',
  'colleague',
] as const;

export const STATUS_LABELS: Record<string, string> = {
  active: 'In the book',
  background: 'Background',
  cut: 'Cut',
};

/** Fields that decide whether a character sheet is actually usable. */
export const CORE_CHARACTER_FIELDS: (keyof BibleCharacter)[] = [
  'name',
  'role',
  'description',
  'goals',
  'need',
  'wound',
  'flaws',
  'voice',
  'arc_summary',
];

export function characterCompleteness(c: BibleCharacter): { filled: number; total: number; pct: number } {
  const filled = CORE_CHARACTER_FIELDS.filter((key) => {
    const value = c[key];
    if (typeof value === 'string') return value.trim().length > 0;
    return value !== null && value !== undefined;
  }).length;
  const total = CORE_CHARACTER_FIELDS.length;
  return { filled, total, pct: Math.round((filled / total) * 100) };
}

export const OVERVIEW_FIELDS: {
  key: keyof BibleWorkspace;
  label: string;
  question: string;
  multiline?: boolean;
  rows?: number;
  placeholder?: string;
}[] = [
  {
    key: 'premise',
    label: 'Premise',
    question: 'In two or three sentences, what happens — and what does it cost the person it happens to?',
    multiline: true,
    rows: 4,
    placeholder: 'A salt trader forges a customs ledger to cross a collapsing empire…',
  },
  {
    key: 'logline',
    label: 'Logline',
    question: 'One sentence: who wants what, what stands in the way, and what happens if they fail?',
    multiline: true,
    rows: 2,
  },
  {
    key: 'central_question',
    label: 'Central dramatic question',
    question: 'What question does the book answer only on its last page?',
    multiline: true,
    rows: 2,
  },
  {
    key: 'genre',
    label: 'Genre',
    question: 'Which shelf would a bookseller put it on?',
    placeholder: 'Literary fiction, historical fantasy, thriller…',
  },
  {
    key: 'subgenre',
    label: 'Subgenre',
    question: 'What kind of book inside that shelf — and what does a reader of it expect?',
    placeholder: 'Political intrigue, domestic suspense…',
  },
  {
    key: 'audience',
    label: 'Audience',
    question: 'Who is this written for, and what do they already believe about the world?',
    placeholder: 'Adult readers of literary historical fiction',
  },
  {
    key: 'pov',
    label: 'Point of view',
    question: 'Whose head are we in when it hurts most?',
  },
  {
    key: 'tense',
    label: 'Tense',
    question: 'Does the story feel like it is happening, or being remembered?',
  },
  {
    key: 'target_word_count',
    label: 'Target word count',
    question: 'How long is the book you are promising the reader? (A debut novel is usually 70,000–100,000.)',
  },
  {
    key: 'comparable_titles',
    label: 'Comparable titles',
    question: 'Name two published books a reader of this would also own — comma separated.',
    placeholder: 'Wolf Hall, The English Patient',
  },
  {
    key: 'tone',
    label: 'Tone',
    question: 'What should the reader feel on page fifty — and is that the feeling the ending earns?',
  },
];

export const CHARACTER_FIELDS: {
  key: keyof BibleCharacter;
  label: string;
  question: string;
  multiline?: boolean;
  rows?: number;
  placeholder?: string;
}[] = [
  {
    key: 'name',
    label: 'Full name',
    question: 'What do people call them — and what does only one person call them?',
  },
  {
    key: 'age',
    label: 'Age',
    question: 'How old are they, and what does that age make possible or impossible?',
  },
  {
    key: 'description',
    label: 'One-line description',
    question: 'Describe them in a line a stranger could recognise them by.',
    multiline: true,
    rows: 2,
  },
  {
    key: 'appearance',
    label: 'Appearance',
    question: 'What do we see first — and what do they do to hide it?',
    multiline: true,
    rows: 3,
  },
  {
    key: 'voice',
    label: 'Voice and speech pattern',
    question: 'How do they talk when they are lying? When they are afraid?',
    multiline: true,
    rows: 3,
    placeholder: 'Clips sentences. Never uses names when angry.',
  },
  {
    key: 'goals',
    label: 'Want (external goal)',
    question: 'What do they want badly enough to act badly for?',
    multiline: true,
    rows: 3,
  },
  {
    key: 'need',
    label: 'Need (internal)',
    question: 'What do they need that they would refuse if it were offered?',
    multiline: true,
    rows: 3,
  },
  {
    key: 'wound',
    label: 'Wound',
    question: 'What happened before page one that taught them to be this way?',
    multiline: true,
    rows: 3,
  },
  {
    key: 'flaws',
    label: 'Flaw',
    question: 'What do they keep doing that makes their own life harder?',
    multiline: true,
    rows: 3,
  },
  {
    key: 'secret',
    label: 'Secret',
    question: 'What are they protecting — and who would it hurt if it came out?',
    multiline: true,
    rows: 3,
  },
  {
    key: 'backstory',
    label: 'Backstory',
    question: 'Which three events made them, and which one do they misremember?',
    multiline: true,
    rows: 4,
  },
  {
    key: 'arc_summary',
    label: 'Arc summary',
    question: 'Who are they on page one, who are they at the end, and which belief changes in between?',
    multiline: true,
    rows: 3,
  },
  {
    key: 'first_appearance',
    label: 'First appearance',
    question: 'Where do we first see them — and what are they doing when we do?',
    placeholder: 'Chapter 2 — at the customs gate',
  },
];

export const WORLD_GROUPS: {
  category: 'location' | 'faction' | 'rule';
  title: string;
  blurb: string;
  question: string;
  nameQuestion: string;
}[] = [
  {
    category: 'location',
    title: 'Locations',
    blurb: 'Places that change what a scene can do.',
    nameQuestion: 'What is this place called?',
    question: 'What does this place demand of anyone who enters it?',
  },
  {
    category: 'faction',
    title: 'Factions and organisations',
    blurb: 'Groups with their own appetite.',
    nameQuestion: 'What is this group called?',
    question: 'What does this group want, and what will it sacrifice to get it?',
  },
  {
    category: 'rule',
    title: 'Rules of the world',
    blurb: 'The laws the story cannot break.',
    nameQuestion: 'State the rule.',
    question: 'What does this rule forbid — and who is punished for breaking it?',
  },
];
