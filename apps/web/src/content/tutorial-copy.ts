/** Tutorial and guided overlay copy. Short, clear, non-intrusive. */

export const TUTORIAL_OVERLAYS = {
  editor_first: {
    title: 'Your writing space',
    steps: [
      { text: 'Chapters are in the sidebar. Click to switch, drag to reorder.' },
      { text: 'The toolbar has AI, notes, reference, and export.' },
      { text: 'Just start typing. Your work saves automatically.' },
    ],
    cta: "Let's write",
    skip: 'Skip',
  },
  ai_first: {
    title: 'AI assistance',
    steps: [
      { text: 'Select text, then choose an action: rewrite, expand, shorten, or continue.' },
      { text: 'Or describe what you need. AI suggests; you decide.' },
    ],
    cta: 'Got it',
    skip: 'Skip',
  },
  integrity_first: {
    title: 'Story Integrity Engine',
    steps: [
      { text: 'Finds unresolved plot threads, weak character arcs, and structural gaps.' },
      { text: 'Click Scan to analyze. Fix issues one at a time.' },
    ],
    cta: 'Got it',
    skip: 'Skip',
  },
  density_first: {
    title: 'Story Density Engine',
    steps: [
      { text: 'Finds filler, repetition, and weak sections.' },
      { text: 'Shows what to cut, compress, or strengthen.' },
    ],
    cta: 'Got it',
    skip: 'Skip',
  },
} as const;

export const FEATURE_INTRO_CARDS = {
  integrity: {
    title: 'Story Integrity Engine',
    description: 'Find what your story is missing—unresolved threads, weak arcs, structural gaps.',
    why: 'Fix issues before readers notice. Revise with clarity.',
    cta: 'Run scan',
  },
  density: {
    title: 'Story Density Engine',
    description: 'Cut filler, find repetition, strengthen weak sections.',
    why: 'Know what to trim and what to build. Tighter prose.',
    cta: 'View density',
  },
  finish_mode: {
    title: 'Finish Mode',
    description: 'Focus on crossing the finish line. One chapter at a time.',
    why: 'Momentum over perfection. Get to the end.',
    cta: 'Enter Finish Mode',
  },
} as const;
