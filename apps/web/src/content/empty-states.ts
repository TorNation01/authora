/** Empty state copy for UI. Warm, supportive, low-friction. */

export interface EmptyStateCopy {
  title: string;
  description: string;
  action?: string;
}

export const EMPTY_STATE_COPY: Record<string, EmptyStateCopy> = {
  no_projects: {
    title: 'Your writing space is ready',
    description:
      'Create your first project to begin. A project can hold one book or a whole series—whatever fits your story.',
    action: 'Create project',
  },
  no_books: {
    title: 'Add your first book',
    description:
      'Pick a template that fits your genre, or start from a blank page. You can change things anytime.',
    action: 'Add book',
  },
  no_chapters: {
    title: 'Your first chapter awaits',
    description:
      'Add a chapter to start writing. Reorder and add more whenever you like—there\'s no wrong way to begin.',
    action: 'Add chapter',
  },
  no_notes: {
    title: 'Keep the thought close',
    description:
      'Add a private note. Leave yourself a marker. Return to this later.',
    action: 'Add note',
  },
  no_highlights: {
    title: 'Mark for revision',
    description: 'Highlight key moments. Flag for rewrite. Check continuity.',
  },
  no_versions: {
    title: 'Your history will appear here',
    description: 'As you write, we\'ll save versions automatically. Come back anytime to restore a previous draft.',
  },
  no_achievements: {
    title: 'Your first badge is close',
    description:
      'Write a little each day and watch your progress grow. Every word counts—we\'re cheering you on.',
  },
  no_goals: {
    title: 'Set a pace you can keep',
    description:
      'Progress builds books. Small, steady sessions count. Set a daily or weekly goal and we\'ll support you—no guilt, just momentum.',
    action: 'Set goal',
  },
  no_exports: {
    title: 'Ready when you are',
    description:
      'When your manuscript feels ready, export to Word, PDF, e-reader format, or plain text. One click.',
    action: 'Export',
  },
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
};

export function getEmptyStateCopy(key: string): EmptyStateCopy | undefined {
  return EMPTY_STATE_COPY[key];
}
