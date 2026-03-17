/**
 * First writing experience copy.
 * Warm, low-pressure, action-oriented.
 */

export const FIRST_WRITE = {
  /** Main options when editor is empty */
  options: {
    startWriting: {
      label: 'Start writing',
      desc: 'Just begin. Type your first words.',
    },
    generateIdea: {
      label: 'Generate opening idea',
      desc: 'AI suggests a starter—you edit or keep.',
    },
    outlineChapter: {
      label: 'Outline chapter',
      desc: 'Plan what happens, then write.',
    },
  },

  /** Optional prompt chips */
  prompts: {
    firstSentence: 'Start your first sentence',
    mainIdea: 'Describe your main idea',
    outlineFirst: 'Outline your first chapter',
  },

  /** AI assist entry */
  aiAssist: {
    generateStarter: 'Generate starter paragraph',
    rewriteFirstLine: 'Rewrite first line',
    suggestIdeas: 'Suggest ideas',
  },

  /** Progress reinforcement */
  progress: {
    started: "You've started!",
    words: (n: number) => `${n} word${n === 1 ? '' : 's'}`,
    keepGoing: 'Keep going—momentum builds books.',
    firstParagraph: 'First paragraph done.',
  },
} as const;
