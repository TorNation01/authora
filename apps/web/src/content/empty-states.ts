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
      'Create your first project to begin. A project holds one book or a series—whatever fits your story.',
    action: 'Create project',
  },
  no_books: {
    title: 'Add your first book',
    description:
      'Choose a template that fits your genre, or start from a blank page. You can always change things later.',
    action: 'Add book',
  },
  no_chapters: {
    title: 'Your first chapter awaits',
    description:
      'Add a chapter to start writing. You can reorder and add more anytime—there\'s no wrong way to begin.',
    action: 'Add chapter',
  },
  no_notes: {
    title: 'Capture your ideas',
    description:
      'Jot down research, quotes, and inspiration here. Link notes to chapters so they\'re easy to find while writing.',
    action: 'Add note',
  },
  no_highlights: {
    title: 'No highlights yet',
    description: 'Select text in your chapter to highlight. Great for marking passages you want to revisit.',
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
    title: 'Set a gentle goal',
    description:
      'A daily or weekly word count can help you stay on track. We\'ll nudge you kindly—no pressure, just support.',
    action: 'Set goal',
  },
  no_exports: {
    title: 'Ready when you are',
    description:
      'When your manuscript feels ready, export to DOCX, PDF, EPUB, or plain text. One click, no fuss.',
    action: 'Export',
  },
  empty_chapter: {
    title: 'Begin here',
    description:
      'Start typing, or use AI to generate a draft from your outline. Your voice, your pace.',
  },
  empty_editor: {
    title: 'Choose a chapter',
    description:
      'Pick a chapter from the sidebar to start writing, or add a new one. Take your time—we\'re here when you\'re ready.',
  },
};

export function getEmptyStateCopy(key: string): EmptyStateCopy | undefined {
  return EMPTY_STATE_COPY[key];
}
