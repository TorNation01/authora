/** Empty state copy for UI. */

export interface EmptyStateCopy {
  title: string;
  description: string;
  action?: string;
}

export const EMPTY_STATE_COPY: Record<string, EmptyStateCopy> = {
  no_projects: {
    title: 'No projects yet',
    description:
      'Create a project to organize your books. A project can hold one book or a series.',
    action: 'Create project',
  },
  no_books: {
    title: 'No books yet',
    description:
      'Add your first book to this project. Choose a template or start from scratch.',
    action: 'Add book',
  },
  no_chapters: {
    title: 'No chapters yet',
    description:
      'Add your first chapter to start writing. You can reorder and add more anytime.',
    action: 'Add chapter',
  },
  no_notes: {
    title: 'No notes yet',
    description:
      'Capture ideas, research, and quotes. Link notes to chapters for easy reference.',
    action: 'Add note',
  },
  no_highlights: {
    title: 'No highlights',
    description: 'Select text to highlight. Highlights help you track important passages.',
  },
  no_versions: {
    title: 'No version history',
    description: 'Versions are saved as you write. Edit this chapter to build history.',
  },
  no_achievements: {
    title: 'No achievements yet',
    description:
      'Write consistently to earn badges and XP. Your first achievement is just a few words away.',
  },
  no_goals: {
    title: 'No goals set',
    description:
      "Set a daily or weekly word goal to stay on track. We'll nudge you when you want.",
    action: 'Set goal',
  },
  no_exports: {
    title: 'No exports yet',
    description:
      'Export your manuscript when you\'re ready. We support DOCX, PDF, EPUB, and more.',
    action: 'Export',
  },
  empty_chapter: {
    title: 'Start writing',
    description:
      "This chapter is empty. Type here or use AI to generate a draft from your outline.",
  },
  empty_editor: {
    title: 'Your manuscript',
    description:
      'Select a chapter from the sidebar to start writing. Or add a new chapter.',
  },
};

export function getEmptyStateCopy(key: string): EmptyStateCopy | undefined {
  return EMPTY_STATE_COPY[key];
}
