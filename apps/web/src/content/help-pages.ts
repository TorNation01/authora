/**
 * Help center page content for public /help routes.
 * Simple language, non-technical, step-by-step, friendly tone.
 */

export interface HelpPageSection {
  heading: string;
  body: string[];
}

export interface HelpPage {
  slug: string;
  title: string;
  description: string;
  sections: HelpPageSection[];
  keywords: string[];
}

export const HELP_PAGES: HelpPage[] = [
  {
    slug: 'getting-started',
    title: 'Getting started',
    description: 'Start your book in a few simple steps.',
    keywords: ['start', 'create', 'book', 'project', 'first', 'begin', 'setup'],
    sections: [
      {
        heading: 'How to start a book',
        body: [
          'Create a project first. A project holds one or more books—like a novel, a series, or a non-fiction book.',
          'Add a book to your project. Choose a template (fiction or non-fiction) or start from scratch. Templates give you a helpful structure—you can always change it later.',
          'Add chapters to your outline. One sentence per chapter is enough to begin. You can reorder chapters anytime by dragging them in the sidebar.',
          'Open a chapter and start writing. Or use Ghostwriter to generate a first draft from your outline.',
        ],
      },
      {
        heading: 'How to choose your guidance level',
        body: [
          'When you create a book, we ask how much structure you want. This helps us suggest the right tools.',
          'Guided: More structure. We suggest frameworks, check story beats, and nudge you toward a clear path. Great if you like a roadmap.',
          'Flexible: Some structure where it helps. Freedom where you want it. A middle ground.',
          'Freeform: Minimal structure. You write your way. We still offer tools when you ask.',
          'You can change this anytime in your project settings.',
        ],
      },
    ],
  },
  {
    slug: 'writing-with-authora',
    title: 'Writing with Authora',
    description: 'How to write chapters and stay in flow.',
    keywords: ['write', 'chapter', 'flow', 'editor', 'focus', 'typing'],
    sections: [
      {
        heading: 'How to write chapters',
        body: [
          'Click a chapter in the sidebar to open it. The editor opens with your content.',
          'Just start typing. Your work saves automatically—no save button needed.',
          'Use the toolbar for notes, AI help, find & replace, and more. Everything is one click away.',
          'Add a chapter brief—a few sentences about what happens in this chapter. AI uses briefs to help you draft and stay on track.',
        ],
      },
      {
        heading: 'How to stay in flow',
        body: [
          'Use Focus mode from the toolbar. It clears the noise so you can stay with the page.',
          'Set a word goal if it helps. Small, steady sessions build books. We count manuscript words only.',
          'Link notes to chapters. Keep research, character sheets, and ideas in the Notes panel. No tab chaos.',
          'Version history lets you restore any previous version. Try something new—you can always go back.',
        ],
      },
    ],
  },
  {
    slug: 'story-integrity-engine',
    title: 'Story Integrity Engine',
    description: 'Find what your story is missing—and fix it with clarity.',
    keywords: ['integrity', 'plot', 'character', 'arc', 'gap', 'thread', 'structure', 'scan'],
    sections: [
      {
        heading: 'What it does',
        body: [
          'The Story Integrity Engine finds unresolved plot threads, weak character arcs, and structural gaps. It asks: What is missing? What is unresolved?',
          'It analyzes your manuscript and surfaces issues you might have missed. Each issue comes with a clear explanation and fix suggestions.',
          'You stay in control. The engine suggests—you decide what to fix, what to keep, and what to mark as intentional.',
        ],
      },
      {
        heading: 'How to use it',
        body: [
          'Open the Story Health panel from the toolbar (the activity icon).',
          'Click Scan to analyze your manuscript. The first scan may take a minute.',
          'Review the issues. Each shows severity, category, and a short description. Click "Go to chapter" to jump to the relevant spot.',
          'Resolve issues one at a time. Or mark something as "Intentional" if you meant it that way.',
        ],
      },
      {
        heading: 'Examples of what it finds',
        body: [
          'Unresolved threads: A character or plot point introduced but never paid off.',
          'Weak arcs: A character who doesn\'t change or grow enough.',
          'Structural gaps: Missing setup before a payoff, or a climax that comes too early.',
          'The engine adapts to fiction, non-fiction, memoir, and workbook. It uses your project type to focus on what matters most.',
        ],
      },
    ],
  },
  {
    slug: 'story-density-engine',
    title: 'Story Density Engine',
    description: 'Cut filler, find repetition, and strengthen weak sections.',
    keywords: ['density', 'filler', 'repetition', 'trim', 'tighten', 'pacing', 'bloat'],
    sections: [
      {
        heading: 'What it does',
        body: [
          'The Story Density Engine finds filler, repetition, and weak sections. It asks: What is bloated? What is dragging? What needs trimming or strengthening?',
          'It helps you tighten prose without losing what matters. You decide what to cut, compress, or expand.',
        ],
      },
      {
        heading: 'When to trim vs expand',
        body: [
          'Trim: Redundant explanation, padding, or scenes that don\'t move the story forward. The engine highlights low-value content so you can cut with confidence.',
          'Expand: Thin transitions, underdeveloped payoffs, or moments that need more weight. The engine finds sections that could use more support.',
          'Use density scans during revision—after you have a full draft. It works best when you\'re ready to polish.',
        ],
      },
    ],
  },
  {
    slug: 'ai-assistance',
    title: 'AI assistance',
    description: 'Use AI to write faster—without losing your voice.',
    keywords: ['ai', 'rewrite', 'expand', 'shorten', 'ghostwriter', 'voice', 'assist'],
    sections: [
      {
        heading: 'How to use AI properly',
        body: [
          'Select text in the editor. The AI menu appears with actions: rewrite, expand, shorten, or continue.',
          'Or open the AI panel from the toolbar. Describe what you need—AI suggests, you decide.',
          'Use AI when you\'re stuck, when you want a fresh take, or when you need to tighten or expand a passage. Ignore it when you don\'t.',
        ],
      },
      {
        heading: 'How to keep your voice',
        body: [
          'AI assists—it doesn\'t replace you. You approve, edit, or reject every suggestion.',
          'Set your preferred AI level in settings: minimal (suggestions only), moderate (rewrites and expansions), or full (drafts and continuations).',
          'Your content is sent to the AI provider only when you trigger an action. We do not train models on your work.',
        ],
      },
    ],
  },
  {
    slug: 'account-and-billing',
    title: 'Account and billing',
    description: 'Manage your account, plan, and billing.',
    keywords: ['account', 'billing', 'plan', 'subscription', 'settings', 'payment'],
    sections: [
      {
        heading: 'Account settings',
        body: [
          'Go to Settings from the dashboard to update your profile, display name, and preferences.',
          'Add or update your AI API key in Settings → AI if you want to use your own OpenAI or Anthropic key.',
        ],
      },
      {
        heading: 'Billing and plans',
        body: [
          'View your plan and billing in the Billing section. Upgrade or change plans anytime.',
          'We accept major credit cards. Invoices are available in your account.',
          'Questions? Contact us—we typically respond within 24–48 hours.',
        ],
      },
    ],
  },
  {
    slug: 'export-and-publishing',
    title: 'Export and publishing',
    description: 'Export your manuscript and prepare for publishing.',
    keywords: ['export', 'publish', 'docx', 'pdf', 'epub', 'synopsis', 'blurb', 'query'],
    sections: [
      {
        heading: 'Export formats',
        body: [
          'Go to Dashboard → Export. Choose DOCX, PDF, EPUB, or plain text.',
          'DOCX: Best for editing in Word, querying agents, or sending to editors.',
          'PDF: Read-only. Good for beta readers, proofreading, or print preview.',
          'EPUB: E-book format. Use for Kindle, Kobo, Apple Books, or self-publishing.',
          'TXT: Plain text. Minimal formatting. Good for backups or conversion.',
        ],
      },
      {
        heading: 'Publishing prep',
        body: [
          'Authora helps you create materials for querying agents or self-publishing.',
          'Synopsis: Generate a 1–2 page summary of your book from your manuscript.',
          'Blurb: Back-cover copy. Short, punchy, hooks the reader.',
          'Query letter: Draft a query from your synopsis and blurb. Customize before sending.',
        ],
      },
      {
        heading: 'Finishing a book',
        body: [
          'Use Finish Mode when you\'re close to the end. It focuses you on one chapter at a time—momentum over perfection.',
          'Run Story Integrity and Story Density scans before export. Fix issues, tighten prose, then export with confidence.',
        ],
      },
    ],
  },
];

export const HELP_NAV = [
  { slug: '', title: 'Overview' },
  ...HELP_PAGES.map((p) => ({ slug: p.slug, title: p.title })),
];

export function getHelpPage(slug: string): HelpPage | undefined {
  return HELP_PAGES.find((p) => p.slug === slug);
}

export function searchHelpPages(query: string): HelpPage[] {
  const q = query.toLowerCase().trim();
  if (!q) return HELP_PAGES;
  return HELP_PAGES.filter(
    (p) =>
      p.title.toLowerCase().includes(q) ||
      p.description.toLowerCase().includes(q) ||
      p.keywords.some((k) => k.includes(q)) ||
      p.sections.some(
        (s) =>
          s.heading.toLowerCase().includes(q) ||
          s.body.some((b) => b.toLowerCase().includes(q))
      )
  );
}
