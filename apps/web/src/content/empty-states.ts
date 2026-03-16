/**
 * Premium empty states for AUTHORA.
 * Warm, supportive copy that makes every blank screen feel helpful rather than intimidating.
 */

export interface EmptyStateAction {
  label: string;
  href?: string;
  onClick?: () => void;
}

export interface EmptyStateConfig {
  title: string;
  description: string;
  primaryAction?: EmptyStateAction;
  secondaryAction?: EmptyStateAction;
  /** Smart default actions—quick paths to get started */
  defaultActions?: EmptyStateAction[];
}

export const EMPTY_STATES: Record<string, EmptyStateConfig> = {
  // ─── Projects ─────────────────────────────────────────────────────────────
  no_projects: {
    title: 'Start your first project',
    description:
      'Your writing space is ready. Create a project to begin—we\'ll guide you through planning and writing. No rush.',
    primaryAction: { label: 'Create project', href: '/dashboard/projects/new' },
    defaultActions: [
      { label: 'Choose a starter template', href: '/dashboard/projects/new' },
      { label: 'Start from blank', href: '/dashboard/projects/new' },
    ],
  },

  // ─── Chapters ──────────────────────────────────────────────────────────────
  no_chapters: {
    title: 'Build the manuscript one chapter at a time',
    description:
      'Your first chapter awaits. Add one to start writing—reorder and add more whenever you like. There\'s no wrong way to begin.',
    primaryAction: { label: 'Create first chapter', onClick: undefined },
    defaultActions: [
      { label: 'Create first chapter', onClick: undefined },
      { label: 'Start with outline', href: undefined },
      { label: 'Open blank page', onClick: undefined },
    ],
  },

  // ─── Ideas ─────────────────────────────────────────────────────────────────
  no_ideas: {
    title: 'Capture the idea before it disappears',
    description:
      'Store now, shape later. Everything you capture stays here—ready when you need it.',
    primaryAction: { label: 'Add idea', onClick: undefined },
    defaultActions: [
      { label: 'Add idea', onClick: undefined },
    ],
  },

  // ─── Notes ─────────────────────────────────────────────────────────────────
  no_notes: {
    title: 'Add your first note',
    description:
      'Keep the thought close. Leave yourself a marker. Return to this later.',
    primaryAction: { label: 'Add note', onClick: undefined },
    defaultActions: [
      { label: 'Add note', onClick: undefined },
    ],
  },

  // ─── Revision passes ───────────────────────────────────────────────────────

  no_revision_passes: {
    title: 'Begin your first revision pass',
    description:
      'Work through the manuscript one issue at a time. Add comments as you read—we\'ll keep track of what needs attention.',
    primaryAction: { label: 'Add revision pass', onClick: undefined },
    defaultActions: [
      { label: 'Add revision pass', onClick: undefined },
      { label: 'Enable focus mode', onClick: undefined },
    ],
  },

  // ─── Exports ───────────────────────────────────────────────────────────────
  no_exports: {
    title: 'Export when the manuscript is ready',
    description:
      'When your manuscript feels ready, export to Word, PDF, e-reader format, or plain text. One click.',
    primaryAction: { label: 'Export', href: '/dashboard/export' },
    defaultActions: [
      { label: 'Export manuscript', href: '/dashboard/export' },
    ],
  },

  no_books_export: {
    title: 'Export when the manuscript is ready',
    description:
      'Create a project and book first. We\'ll be ready when you are.',
    primaryAction: { label: 'Go to Home', href: '/dashboard' },
  },

  // ─── Collaborators ─────────────────────────────────────────────────────────
  no_collaborators: {
    title: 'Invite someone in when you want feedback',
    description:
      'Share your manuscript with beta readers, editors, or clients. You control what others see.',
    primaryAction: { label: 'Invite collaborator', onClick: undefined },
    defaultActions: [
      { label: 'Invite collaborator', onClick: undefined },
    ],
  },

  // ─── Sources ───────────────────────────────────────────────────────────────
  no_sources: {
    title: 'Build the references behind the book',
    description:
      'Add books, articles, and references. Track citations and link to chapters—keep sources organised.',
    primaryAction: { label: 'Add source', onClick: undefined },
    defaultActions: [
      { label: 'Add source', onClick: undefined },
    ],
  },

  // ─── Character entries ──────────────────────────────────────────────────────
  no_characters: {
    title: 'Build the people, places, and details behind the book',
    description:
      'Add your first character to build your character bible. Track roles, arcs, and motivations—build people worth following.',
    primaryAction: { label: 'Add character', onClick: undefined },
    defaultActions: [
      { label: 'Add character', onClick: undefined },
    ],
  },

  // ─── Worldbuilding entries ─────────────────────────────────────────────────
  no_worldbuilding: {
    title: 'Build the people, places, and details behind the book',
    description:
      'Shape the world behind the words. Add places, factions, cultures, and rules—keep the setting coherent as the story grows.',
    primaryAction: { label: 'Add location', onClick: undefined },
    defaultActions: [
      { label: 'Add location', onClick: undefined },
    ],
  },

  // ─── Timeline events ───────────────────────────────────────────────────────
  no_timeline_events: {
    title: 'See the story in sequence',
    description:
      'Track story chronology, backstory, and key moments. Keep events aligned—what happened, when, and why it matters.',
    primaryAction: { label: 'Add event', onClick: undefined },
    defaultActions: [
      { label: 'Add event', onClick: undefined },
    ],
  },

  // ─── Research ───────────────────────────────────────────────────────────────
  no_research: {
    title: 'Keep your supporting material in reach',
    description:
      'Add research notes, clipped snippets, and summaries. Link them to chapters when you write—keep your supporting material in reach.',
    primaryAction: { label: 'Add research', onClick: undefined },
    defaultActions: [
      { label: 'Add research', onClick: undefined },
    ],
  },

  // ─── Goals ──────────────────────────────────────────────────────────────────
  no_goals: {
    title: 'Set a pace you can keep',
    description:
      'Progress builds books. Small, steady sessions count. Set a daily or weekly goal and we\'ll support you—no guilt, just momentum.',
    primaryAction: { label: 'Set goal', onClick: undefined },
    defaultActions: [
      { label: 'Set writing goal', onClick: undefined },
    ],
  },

  // ─── Empty chapter / editor ────────────────────────────────────────────────
  empty_chapter: {
    title: 'Begin here',
    description:
      'This section is yours to shape. Write first. Refine after.',
  },
  empty_editor: {
    title: 'Choose a chapter',
    description:
      'Pick a chapter from the sidebar to start writing, or add a new one.',
  },

  // ─── Notes (no projects) ───────────────────────────────────────────────────
  no_projects_notes: {
    title: 'Create a project first',
    description:
      'Notes live with your projects. Create one to get started.',
    primaryAction: { label: 'Back to Home', href: '/dashboard' },
  },

  // ─── No books ──────────────────────────────────────────────────────────────
  no_books: {
    title: 'Add your first book',
    description:
      'Pick a template that fits your genre, or start from a blank page. You can change things anytime.',
    primaryAction: { label: 'Add book', href: undefined },
  },
};

/** @deprecated Use EMPTY_STATES and getEmptyStateConfig */
export const EMPTY_STATE_COPY: Record<string, { title: string; description: string; action?: string }> = Object.fromEntries(
  Object.entries(EMPTY_STATES).map(([k, v]) => [
    k,
    {
      title: v.title,
      description: v.description,
      action: v.primaryAction?.label,
    },
  ])
);

export function getEmptyStateConfig(
  key: string,
  overrides?: Partial<EmptyStateConfig>
): EmptyStateConfig | undefined {
  const config = EMPTY_STATES[key];
  if (!config) return undefined;
  return overrides ? { ...config, ...overrides } : config;
}

/** @deprecated Use getEmptyStateConfig */
export function getEmptyStateCopy(key: string) {
  return getEmptyStateConfig(key);
}
